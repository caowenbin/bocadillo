import pytest

from bocadillo import App


def test_default_response_is_success_empty_text(app: App):
    @app.route("/")
    async def index(req, res):
        pass

    response = app.client.get("/")
    assert response.text == ""
    assert response.status_code == 200


def test_if_status_code_is_no_content_then_no_content_type_set(app: App):
    @app.route("/")
    async def index(req, res):
        res.status_code = 204
        pass

    response = app.client.get("/")
    assert response.status_code == 204
    assert not response.text
    assert response.headers.get("content-type") is None


def test_content_type_defaults_to_plaintext(app: App):
    @app.route("/")
    async def index(req, res):
        res.content = "Something magical"
        # make sure no content-type is set before leaving the view
        res.headers.pop("Content-Type", None)
        pass

    response = app.client.get("/")
    assert response.headers["Content-Type"] == "text/plain"


def test_if_text_set_then_response_is_plain_text(app: App):
    @app.route("/")
    async def index(req, res):
        res.text = "foo"
        pass

    response = app.client.get("/")
    assert response.headers["Content-Type"] == "text/plain"
    assert response.text == "foo"


def test_if_media_set_then_response_is_json(app: App):
    @app.route("/")
    async def index(req, res):
        res.media = {"foo": "bar"}

    response = app.client.get("/")
    assert response.json() == {"foo": "bar"}


def test_if_html_set_then_response_is_html(app: App):
    @app.route("/")
    async def index(req, res):
        res.html = "<h1>Foo</h1>"

    response = app.client.get("/")
    assert response.headers["Content-Type"] == "text/html"
    assert response.text == "<h1>Foo</h1>"


@pytest.mark.parametrize(
    "contents, content_type, check_content",
    [
        [
            [("media", {"foo": "bar"}), ("text", "foo")],
            "text/plain",
            lambda r: r.text == "foo",
        ],
        [
            [("text", "foo"), ("media", {"foo": "bar"})],
            "application/json",
            lambda r: r.json() == {"foo": "bar"},
        ],
    ],
)
def test_last_response_setter_called_has_priority(
    app: App, contents: list, content_type: str, check_content
):
    @app.route("/")
    async def index(req, res):
        for attr, value in contents:
            setattr(res, attr, value)

    response = app.client.get("/")
    assert response.headers["Content-Type"] == content_type
    assert check_content(response)
