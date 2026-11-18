# FloodGuard frontend

The React/Vite operations console consumes the FastAPI service on `http://127.0.0.1:8000`. Start the backend first, then run:

```powershell
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` when the backend runs elsewhere:

```powershell
$env:VITE_API_BASE_URL="http://127.0.0.1:8000"
```

The UI starts in a loading state, reports backend errors explicitly, and falls back to the checked-in synthetic station telemetry when the API is unavailable. Fallback data is labelled as offline synthetic data and must not be interpreted as live telemetry.
