from typing import List

import pytest

from bocadillo import API, Request, Response


@pytest.mark.parametrize("q, expected", [(None, ""), ("hello", "hello")])
def test_annotated_query_param(api: API, q: str, expected):
    @api.route("/{pos:d}")
    async def index(req, res, pos: int, q: str = ""):
        assert isinstance(pos, int)
        res.text = q

    params = {} if q is None else {"q": q}
    r = api.client.get("/34", params=params)
    assert r.status_code == 200
    assert r.text == expected


def test_ignores_request(api: API):
    @api.route("/")
    async def index(req: Request, res):
        res.text = "OK"

    r = api.client.get("/", params={"q": "foo"})
    assert r.status_code == 200
    assert r.text == "OK"


def test_ignores_response(api: API):
    @api.route("/")
    async def index(req, res: Response):
        res.text = "OK"

    r = api.client.get("/", params={"q": "foo"})
    assert r.status_code == 200
    assert r.text == "OK"


@pytest.mark.parametrize("value, expected", [(None, {"n": 0}), (2, {"n": 2})])
def test_query_param_conversion(api: API, value, expected):
    @api.route("/")
    async def index(req, res, n: int = 0):
        assert isinstance(n, int)
        res.media = {"n": n}

    params = {} if value is None else {"n": value}
    r = api.client.get("/", params=params)
    assert r.status_code == 200
    assert r.json() == expected


def test_query_param_validation(api: API):
    @api.route("/")
    async def index(req, res, n: int = 0):
        pass

    r = api.client.get("/", params={"n": "obviously not an integer"})
    assert r.status_code == 400


def test_custom_converter(api: API):
    def converter_parts(value: str) -> List[str]:
        return value.split(".")

    @api.route("/")
    async def index(req, res, parts: converter_parts = None):
        res.media = parts or []

    r = api.client.get("/", params={"parts": "a.b.c and d"})
    assert r.status_code == 200
    assert r.json() == ["a", "b", "c and d"]
