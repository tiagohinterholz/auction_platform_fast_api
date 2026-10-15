from typing import Annotated

from fastapi import Depends, Request

from app.core.events.event_bus_interface import EventBusInterface


def get_event_bus(request: Request) -> EventBusInterface:
    return request.app.state.event_bus


EventBusDep = Annotated[EventBusInterface, Depends(get_event_bus)]
