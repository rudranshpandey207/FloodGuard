"""Persistent local chat-session records for the FloodGuard assistant."""

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix="/api/chat", tags=["Chat Sessions"])
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "incidents.db"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                synthesis_source TEXT,
                tool_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
            )
            """
        )


initialize_database()


class CreateSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(default="FloodGuard operator chat", min_length=1, max_length=200)


class ChatMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=10000)
    synthesis_source: str = Field(default="offline-deterministic", max_length=100)
    tool_count: int = Field(default=0, ge=0)


@router.post("/sessions", status_code=201)
def create_session(payload: CreateSessionRequest):
    session_id = f"CHAT-{uuid.uuid4().hex[:10].upper()}"
    now = utc_now()
    with connect() as connection:
        connection.execute(
            "INSERT INTO chat_sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (session_id, payload.title, now, now),
        )
        row = connection.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
    return dict(row)


@router.get("/sessions")
def list_sessions():
    with connect() as connection:
        rows = connection.execute("SELECT * FROM chat_sessions ORDER BY updated_at DESC").fetchall()
    return [dict(row) for row in rows]


@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: str):
    with connect() as connection:
        session = connection.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        rows = connection.execute(
            "SELECT id, role, content, synthesis_source, tool_count, created_at FROM chat_messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,),
        ).fetchall()
    return {"session": dict(session), "messages": [dict(row) for row in rows]}


@router.post("/sessions/{session_id}/messages", status_code=201)
def add_message(session_id: str, payload: ChatMessageRequest):
    now = utc_now()
    with connect() as connection:
        session = connection.execute("SELECT id FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        connection.execute(
            "INSERT INTO chat_messages (session_id, role, content, synthesis_source, tool_count, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, payload.role, payload.content, payload.synthesis_source, payload.tool_count, now),
        )
        connection.execute("UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (now, session_id))
        row = connection.execute(
            "SELECT id, role, content, synthesis_source, tool_count, created_at FROM chat_messages WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (session_id,),
        ).fetchone()
    return dict(row)
