from typing import List

import pytest

from bocadillo import API, Request, Response
from bocadillo.query_params import ConverterMustBeCallable


def test_with_default(api: API):
    @api.route("/")
    async def index(req, res, q: str = "default"):
        res.text = q

    r = api.client.get("/")
    assert r.status_code == 200
    assert r.text == "default"


def test_if_no_default_then_required(api: API):
    @api.route("/")
    async def index(req, res, q: str):
        res.text = q

    r = api.client.get("/")
    assert r.status_code == 400
    assert "q:" in r.text
    assert "query parameter" in r.text
    assert "required" in r.text


def test_if_no_annotation_then_string(api: API):
    @api.route("/")
    async def index(req, res, q):
        assert isinstance(q, str)
        res.text = q

    r = api.client.get("/", params={"q": "hello"})
    assert r.status_code == 200
    assert r.text == "hello"


def test_along_with_route_parameter(api: API):
    @api.route("/{x:d}")
    async def index(req, res, x: int, y: int):
        res.media = {"x": x, "y": y}

    r = api.client.get("/1", params={"y": 2})
    assert r.status_code == 200
    assert r.json() == {"x": 1, "y": 2}


def test_extra_query_params_are_ignored(api: API):
    @api.route("/")
    async def index(req, res):
        pass

    r = api.client.get("/", params={"q": "foo", "r": "spam"})
    assert r.status_code == 200


@pytest.mark.parametrize("key", ("req", "res"))
def test_req_and_res_ignored(api: API, key):
    @api.route("/")
    async def index(req, res):
        # Use req and res to make sure they haven't been when
        # converting query parameters.
        res.text = req.url.path

    r = api.client.get("/", params={key: "foo"})
    assert r.status_code == 200
    assert r.text == "/"


def test_conversion(api: API):
    @api.route("/")
    async def index(req, res, n: int):
        res.media = {"n": n}

    r = api.client.get("/", params={"n": 2})
    assert r.status_code == 200
    assert r.json() == {"n": 2}


def test_validation(api: API):
    @api.route("/")
    async def index(req, res, n: int):
        pass

    r = api.client.get("/", params={"n": "obviously not an integer"})
    assert r.status_code == 400
    # TODO: test error message


def test_custom_converter(api: API):
    def convert_parts(value: str) -> List[str]:
        return value.split(".")

    @api.route("/")
    async def index(req, res, parts: convert_parts):
        res.media = parts or []

    r = api.client.get("/", params={"parts": "a.b.c and d"})
    assert r.status_code == 200
    assert r.json() == ["a", "b", "c and d"]


@pytest.mark.parametrize("converter", [1, None, List[str]])
def test_annotation_must_be_callable(api: API, converter):
    with pytest.raises(ConverterMustBeCallable):

        @api.route("/")
        async def index(req, res, parts: converter):
            pass
