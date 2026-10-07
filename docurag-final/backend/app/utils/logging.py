"""Structured logging utilities."""
import json, logging, sys
from datetime import UTC, datetime
from typing import Any
from app.config import Settings
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {"timestamp": datetime.now(UTC).isoformat(), "level": record.levelname, "logger": record.name, "message": record.getMessage()}
        if record.exc_info: payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)
def configure_logging(settings: Settings) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter() if settings.log_json else logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    root = logging.getLogger(); root.handlers.clear(); root.addHandler(handler); root.setLevel(settings.log_level.upper())
