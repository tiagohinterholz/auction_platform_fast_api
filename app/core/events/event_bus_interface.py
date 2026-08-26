from abc import ABC, abstractmethod
from collections.abc import Callable


class EventBusInterface(ABC):

    @abstractmethod
    async def publish(self, events: list) -> None:
        pass

    @abstractmethod
    async def subscribe(
        self, event_name: str, handler: Callable, broadcast: bool = False
    ) -> None:
        """`broadcast=False` (default): exactly-once-among-subscribers of this
        event, the right choice for handlers that write to the DB (e.g. read
        model projections) - two workers both processing the same event
        would double the write. `broadcast=True`: every subscriber process
        gets its own copy, needed by anything that depends on **local,
        per-process, in-memory state** - the only current example is the
        WebSocket notification handlers (app/modules/notifications), since
        the client's actual socket only lives in whichever worker process
        accepted that connection; a competing-consumer queue would deliver
        the event to a single, possibly-wrong worker and the notification
        would silently never reach that client.
        """
