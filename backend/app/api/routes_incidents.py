"""Human-supervised incident and alert acknowledgement workflow."""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "incidents.db"


def utc_now() -> str:
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
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                station_id TEXT,
                station_name TEXT,
                river TEXT,
                risk_label TEXT NOT NULL,
                risk_level INTEGER NOT NULL,
                water_level_m REAL,
                danger_level_m REAL,
                status TEXT NOT NULL,
                operator TEXT NOT NULL,
                summary TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                acknowledged_at TEXT,
                resolved_at TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS incident_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT NOT NULL,
                action TEXT NOT NULL,
                actor TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (incident_id) REFERENCES incidents(id)
            )
            """
        )
        incident_columns = {row[1] for row in connection.execute("PRAGMA table_info(incidents)").fetchall()}
        for column_name, definition in {
            "approval_confirmed": "INTEGER NOT NULL DEFAULT 0",
            "approved_by": "TEXT",
            "approved_at": "TEXT",
        }.items():
            if column_name not in incident_columns:
                connection.execute(f"ALTER TABLE incidents ADD COLUMN {column_name} {definition}")


initialize_database()


class CreateIncidentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=3, max_length=200)
    station_id: Optional[str] = Field(default=None, max_length=100)
    station_name: Optional[str] = Field(default=None, max_length=200)
    river: Optional[str] = Field(default=None, max_length=100)
    risk_label: Literal["Low", "Medium", "High", "Critical"]
    risk_level: int = Field(ge=0, le=3)
    water_level_m: Optional[float] = Field(default=None, ge=0)
    danger_level_m: Optional[float] = Field(default=None, ge=0)
    operator: str = Field(default="Field Operator", min_length=1, max_length=100)
    summary: str = Field(min_length=3, max_length=2000)


class UpdateIncidentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["Open", "Investigating", "Acknowledged", "Resolved"]
    operator: str = Field(default="Field Operator", min_length=1, max_length=100)
    note: str = Field(default="", max_length=2000)
    approval_confirmed: bool = False


def incident_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "station_id": row["station_id"],
        "station_name": row["station_name"],
        "river": row["river"],
        "risk_label": row["risk_label"],
        "risk_level": row["risk_level"],
        "water_level_m": row["water_level_m"],
        "danger_level_m": row["danger_level_m"],
        "status": row["status"],
        "operator": row["operator"],
        "summary": row["summary"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "acknowledged_at": row["acknowledged_at"],
        "resolved_at": row["resolved_at"],
        "approval_confirmed": bool(row["approval_confirmed"]),
        "approved_by": row["approved_by"],
        "approved_at": row["approved_at"],
    }


@router.post("", status_code=201)
def create_incident(payload: CreateIncidentRequest):
    incident_id = f"INC-{uuid.uuid4().hex[:10].upper()}"
    now = utc_now()
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO incidents
            (id, title, station_id, station_name, river, risk_label, risk_level,
             water_level_m, danger_level_m, status, operator, summary, created_at,
             updated_at, acknowledged_at, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open', ?, ?, ?, ?, NULL, NULL)
            """,
            (
                incident_id, payload.title, payload.station_id, payload.station_name,
                payload.river, payload.risk_label, payload.risk_level,
                payload.water_level_m, payload.danger_level_m, payload.operator,
                payload.summary, now, now,
            ),
        )
        connection.execute(
            "INSERT INTO incident_audit (incident_id, action, actor, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (incident_id, "incident_created", payload.operator, payload.summary, now),
        )
        row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    return incident_dict(row)


@router.get("")
def list_incidents(status: Optional[str] = None):
    with connect() as connection:
        if status:
            rows = connection.execute("SELECT * FROM incidents WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
        else:
            rows = connection.execute("SELECT * FROM incidents ORDER BY created_at DESC").fetchall()
    return [incident_dict(row) for row in rows]


@router.get("/{incident_id}")
def get_incident(incident_id: str):
    with connect() as connection:
        row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Incident not found")
        audit_rows = connection.execute(
            "SELECT action, actor, details, created_at FROM incident_audit WHERE incident_id = ? ORDER BY created_at ASC, id ASC",
            (incident_id,),
        ).fetchall()
    result = incident_dict(row)
    result["audit"] = [dict(item) for item in audit_rows]
    return result


@router.patch("/{incident_id}")
def update_incident(incident_id: str, payload: UpdateIncidentRequest):
    now = utc_now()
    with connect() as connection:
        row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Incident not found")

        acknowledged_at = row["acknowledged_at"]
        resolved_at = row["resolved_at"]
        approval_confirmed = bool(row["approval_confirmed"])
        approved_by = row["approved_by"]
        approved_at = row["approved_at"]

        if payload.status in {"Acknowledged", "Resolved"} and not payload.approval_confirmed:
            raise HTTPException(status_code=422, detail="Human approval confirmation is required")

        if payload.status == "Resolved" and row["status"] not in {"Investigating", "Acknowledged"}:
            raise HTTPException(status_code=409, detail="Resolve incidents only after investigation or acknowledgement")

        if payload.status in {"Acknowledged", "Resolved"}:
            approval_confirmed = True
            approved_by = payload.operator
            approved_at = now
        if payload.status == "Acknowledged" and acknowledged_at is None:
            acknowledged_at = now
        if payload.status == "Resolved" and resolved_at is None:
            resolved_at = now

        connection.execute(
            "UPDATE incidents SET status = ?, operator = ?, updated_at = ?, acknowledged_at = ?, resolved_at = ?, approval_confirmed = ?, approved_by = ?, approved_at = ? WHERE id = ?",
            (payload.status, payload.operator, now, acknowledged_at, resolved_at, int(approval_confirmed), approved_by, approved_at, incident_id),
        )
        detail = payload.note.strip() or f"Status changed to {payload.status}"
        connection.execute(
            "INSERT INTO incident_audit (incident_id, action, actor, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (incident_id, "status_changed", payload.operator, detail, now),
        )
        updated = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    return incident_dict(updated)
