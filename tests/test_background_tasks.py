from bocadillo import App


def test_background_task_is_executed(app: App):
    executed = False

    @app.route("/")
    async def index(req, res):
        @res.background
        async def notify_executed():
            nonlocal executed
            executed = True

        res.text = "OK"

    response = app.client.get("/")
    assert response.status_code == 200
    assert response.text == "OK"
    assert executed


def test_background_task_is_executed_after_response_is_sent(app: App):
    @app.route("/")
    async def index(req, res):
        @res.background
        async def send_bar():
            res.text = "BAR"

        res.text = "FOO"

    response = app.client.get("/")
    assert response.text == "FOO"


def test_can_pass_extra_kwargs(app: App):
    called = False

    async def set_called(what):
        nonlocal called
        called = what

    @app.route("/")
    async def index(req, res):
        res.background(set_called, "true")

    response = app.client.get("/")
    assert response.status_code == 200
    assert called == "true"
