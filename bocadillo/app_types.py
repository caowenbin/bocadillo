from typing import Callable, Awaitable, MutableMapping, Any
from starlette.datastructures import QueryParams as _QP

from .request import Request
from .response import Response

# ASGI
Scope = dict
Event = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Event]]
Send = Callable[[Event], None]
ASGIAppInstance = Callable[[Receive, Send], Awaitable[None]]
ASGIApp = Callable[[Scope], ASGIAppInstance]

# Views
Handler = Callable[[Request, Response, Any], Awaitable[None]]

# HTTP
HTTPApp = Callable[[Request, Response], Awaitable[Response]]
ErrorHandler = Callable[[Request, Response, Exception], None]
QueryParams = _QP

# Server lifespan events
EventHandler = Callable[[], Awaitable[None]]
