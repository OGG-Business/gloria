import asyncio
import json
from typing import AsyncGenerator, Dict, List
from .core.config import settings


class SSEBroker:
    def __init__(self) -> None:
        self._subscribers: Dict[int, List[asyncio.Queue]] = {}

    def publish_sync(self, transfer_id: int, event):
        queues = self._subscribers.get(transfer_id, [])
        for q in queues:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass

    async def publish(self, transfer_id: int, event: str):
        queues = self._subscribers.get(transfer_id, [])
        for q in queues:
            await q.put(event)

    async def subscribe(self, transfer_id: int) -> AsyncGenerator[str, None]:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.setdefault(transfer_id, []).append(queue)
        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            self._subscribers.get(transfer_id, []).remove(queue)


broker = SSEBroker()


_pubsub_publisher = None
_pubsub_topic_path = None


def _get_pubsub():
    global _pubsub_publisher, _pubsub_topic_path
    if not settings.pubsub_enabled:
        return None, None
    if _pubsub_publisher is None:
        from google.cloud import pubsub_v1  # type: ignore
        _pubsub_publisher = pubsub_v1.PublisherClient()
        _pubsub_topic_path = _pubsub_publisher.topic_path(
            settings.pubsub_project_id or "", settings.pubsub_topic_id or ""
        )
    return _pubsub_publisher, _pubsub_topic_path


def publish_event(transfer_id: int, event: Dict):
    # SSE
    broker.publish_sync(transfer_id, event)
    # Pub/Sub
    publisher, topic = _get_pubsub()
    if publisher and topic:
        data = json.dumps({"transfer_id": transfer_id, **event}).encode("utf-8")
        publisher.publish(topic, data=data)