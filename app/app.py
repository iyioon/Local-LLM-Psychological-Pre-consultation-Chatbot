"""Web interface for the psychological pre-consultation chatbot."""

from __future__ import annotations

import logging
import os
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, session

from src.chat_engine import ChatEngine
from src.config import MAX_CONVERSATION_TURNS

logger = logging.getLogger(__name__)


def create_app() -> Flask:

    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    # Use environment secret by default or fall back to a development key.
    app.config["SECRET_KEY"] = os.environ.get(
        "CHATBOT_SECRET_KEY", "local-dev-secret")

    # Store chat engines per user session to keep conversations isolated.
    session_engines: dict[str, ChatEngine] = {}

    def _get_engine() -> ChatEngine:
        """Retrieve or create a ChatEngine bound to the user's session."""

        session_id = session.get("chat_session_id")
        if not session_id or session_id not in session_engines:
            session_id = str(uuid4())
            session["chat_session_id"] = session_id
            session_engines[session_id] = ChatEngine()
            logger.info("Created new ChatEngine for session %s", session_id)
        return session_engines[session_id]

    def _drop_engine() -> None:
        session_id = session.pop("chat_session_id", None)
        if session_id and session_id in session_engines:
            logger.info("Resetting ChatEngine for session %s", session_id)
            session_engines.pop(session_id, None)

    @app.route("/")
    def index() -> str:
        """Serve the chat interface."""

        return render_template("index.html")

    @app.get("/api/session")
    def session_info():
        """Provide session bootstrap information such as the disclaimer text."""

        engine = _get_engine()
        disclaimer = engine.moderator.get_disclaimer()
        return jsonify(
            {
                "disclaimer": disclaimer.strip(),
                "max_turns": MAX_CONVERSATION_TURNS,
            }
        )

    @app.post("/api/message")
    def send_message():
        """Handle a user message by running it through the moderation pipeline."""

        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()
        include_context = bool(data.get("include_context", True))

        if not message:
            return jsonify({"error": "Message cannot be empty."}), 400

        engine = _get_engine()

        try:
            result = engine.process_message(
                user_input=message,
                include_context=include_context,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Chat engine failed to process message")
            return (
                jsonify(
                    {
                        "error": "An unexpected error occurred. Please try again or restart the session.",
                        "details": str(exc),
                    }
                ),
                500,
            )

        return jsonify(result)

    @app.post("/api/reset")
    def reset_session():
        """Reset the conversation for the current user."""

        _drop_engine()
        return jsonify({"success": True})

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover - manual execution
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
