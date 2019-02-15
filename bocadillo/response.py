import inspect
from typing import (
    Any,
    AsyncIterable,
    Callable,
    Coroutine,
    Dict,
    Optional,
    Union,
)

from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import (
    Response as _Response,
    StreamingResponse as _StreamingResponse,
)

from .constants import CONTENT_TYPE
from .media import MediaHandler

AnyStr = Union[str, bytes]
BackgroundFunc = Callable[..., Coroutine]
Stream = AsyncIterable[AnyStr]
StreamFunc = Callable[[], Stream]


def _content_setter(content_type: str):
    def fset(res: "Response", value: AnyStr):
        res.content = value
        res.headers["content-type"] = content_type

    doc = (
        "Write-only property that sets `content` to the set value and sets "
        f'the `Content-Type` header to `"{content_type}"`.'
    )

    return property(fget=None, fset=fset, doc=doc)


class Response:
    """The response builder, passed to HTTP views and typically named `res`.

    At the lower-level, `Response` behaves like an ASGI application instance:
    it is a callable and accepts `receive` and `send` as defined in the [ASGI
    spec](https://asgi.readthedocs.io/en/latest/specs/main.html#applications).

    [media]: ../guides/http/media.md

    # Parameters
    request (Request): the currently processed request.
    media_type (str): the configured media type (given by the `API`).
    media_handler (callable): the configured media handler (given by the `API`).

    # Attributes
    content (bytes or str): the raw response content.
    status_code (int): the HTTP status code. If not set, defaults to `200`.
    headers (dict):
        a case-insensitive dictionary of HTTP headers.
        If not set, `content-type` header is set to `text/plain`.
    chunked (bool): sets the `transfer-encoding` header to `chunked`.
    """

    text = _content_setter(CONTENT_TYPE.PLAIN_TEXT)
    html = _content_setter(CONTENT_TYPE.HTML)

    def __init__(
        self, request: Request, media_type: str, media_handler: MediaHandler
    ):
        # Public attributes.
        self.content: Optional[AnyStr] = None
        self.request = request
        self.status_code: Optional[int] = None
        self.headers: Dict[str, str] = {}
        self.chunked = False
        # Private attributes.
        self._media_type = media_type
        self._media_handler = media_handler
        self._background: Optional[BackgroundFunc] = None
        self._stream: Optional[Stream] = None

    media = property(
        doc=(
            "Write-only property that sets `content` to the set value "
            "serializer using the `media_handler`, sets the "
            "`Content-Type` header to the `media_type`."
        )
    )

    @media.setter
    def media(self, value: Any):
        self.content = self._media_handler(value)
        self.headers["content-type"] = self._media_type

    def background(
        self, func: BackgroundFunc, *args, **kwargs
    ) -> BackgroundFunc:
        """Register a coroutine function to be executed in the background.

        This can be used either as a decorator or a regular function.

        # Parameters
        func (callable):
            A coroutine function.
        *args, **kwargs:
            Any positional and keyword arguments to pass to `func` when
            executing it.
        """

        async def background():
            await func(*args, **kwargs)

        self._background = background
        return func

    @property
    def _background_task(self) -> Optional[BackgroundTask]:
        if self._background is not None:
            return BackgroundTask(self._background)
        return None

    def stream(self, func: StreamFunc) -> StreamFunc:
        """Stream the response.

        Should be used to decorate a no-argument asynchronous generator
        function.
        """
        assert inspect.isasyncgenfunction(func)
        self._stream = func()
        return func

    async def __call__(self, receive, send):
        """Build and send the response."""
        if self.status_code is None:
            self.status_code = 200

        if self.status_code != 204:
            self.headers.setdefault("content-type", "text/plain")

        if self.chunked:
            self.headers["transfer-encoding"] = "chunked"

        response_kwargs = {
            "content": self.content,
            "status_code": self.status_code,
            "headers": self.headers,
            "background": self._background_task,
        }

        response_cls = _Response

        if self._stream is not None:
            response_cls = _StreamingResponse
            response_kwargs["content"] = self._stream

        response: _Response = response_cls(**response_kwargs)
        await response(receive, send)
