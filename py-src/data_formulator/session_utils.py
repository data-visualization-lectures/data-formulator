import secrets
from flask import request, session as flask_session


def resolve_session_id() -> str:
    """
    Resolve the session ID for the current request.

    Priority:
      1. X-Session-Id request header  (cross-origin frontend, e.g. Vercel → Railway)
      2. Flask session cookie           (same-origin / local development)
      3. Generate a new ID             (last resort; should not happen in normal flow)

    Background:
      When the frontend (Vercel) calls the API (Railway) cross-origin, the browser
      does not send Flask session cookies because CORS credentials mode is not enabled.
      Instead, the frontend stores the session_id in localStorage and sends it via the
      X-Session-Id header with every request.
    """
    # 1. Header takes priority for cross-origin setups
    session_id = request.headers.get('X-Session-Id')
    if session_id:
        return session_id

    # 2. Fall back to Flask session cookie (same-origin / local dev)
    session_id = flask_session.get('session_id')
    if session_id:
        return session_id

    # 3. Last resort: generate a fresh ID and store it in the Flask session
    new_id = secrets.token_hex(16)
    flask_session['session_id'] = new_id
    return new_id
