import json
import logging
from pathlib import Path

from dotenv import load_dotenv

from multi_agent.conversation_logger import ConversationLogger

logger = logging.getLogger("aelon.replay_failed_conversations")

load_dotenv()

FAILED_EVENTS_PATH = Path("data") / "processed" / "failed_conversation_events.jsonl"


def replay_failed_events(failed_events_path: str | None = None) -> dict:
    target_path = Path(failed_events_path) if failed_events_path else FAILED_EVENTS_PATH
    if not target_path.exists():
        return {
            "processed": 0,
            "replayed": 0,
            "skipped_existing": 0,
            "failed": 0,
            "remaining": 0,
            "details": [],
        }

    raw_lines = target_path.read_text(encoding="utf-8").splitlines()
    logger_instance = ConversationLogger(fallback_path=str(target_path))

    replayed = 0
    skipped_existing = 0
    failed = 0
    details: list[dict] = []
    remaining_events: list[str] = []

    for line in raw_lines:
        if not line.strip():
            continue

        try:
            event = json.loads(line)
        except Exception as exc:
            failed += 1
            details.append({"status": "invalid_json", "reason": str(exc), "raw": line[:200]})
            remaining_events.append(line)
            continue

        payload = event.get("payload") if isinstance(event, dict) else None
        if not isinstance(payload, dict):
            failed += 1
            details.append({"status": "invalid_payload", "event": event})
            remaining_events.append(line)
            continue

        conversation_id = str(payload.get("conversation_id") or "")

        try:
            if conversation_id and logger_instance.conversation_exists(conversation_id):
                skipped_existing += 1
                details.append({"status": "skipped_existing", "conversation_id": conversation_id})
                continue

            save_result = logger_instance.save_payload(payload, write_fallback_on_error=False)
            if save_result.get("saved"):
                replayed += 1
                details.append({
                    "status": "replayed",
                    "conversation_id": save_result.get("conversation_id", conversation_id),
                })
            else:
                failed += 1
                details.append({
                    "status": "failed",
                    "conversation_id": conversation_id,
                    "reason": save_result.get("reason"),
                })
                remaining_events.append(line)
        except Exception as exc:
            logger.exception("replay.failed conversation_id=%s", conversation_id)
            failed += 1
            details.append({
                "status": "failed_exception",
                "conversation_id": conversation_id,
                "reason": str(exc),
            })
            remaining_events.append(line)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8") as handle:
        for raw_event in remaining_events:
            handle.write(raw_event.rstrip("\n") + "\n")

    return {
        "processed": len([line for line in raw_lines if line.strip()]),
        "replayed": replayed,
        "skipped_existing": skipped_existing,
        "failed": failed,
        "remaining": len(remaining_events),
        "details": details,
    }


if __name__ == "__main__":
    summary = replay_failed_events()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
