from bocadillo import App, Recipe, WebSocket


def test_websocket_recipe_route(app: App):
    chat = Recipe("chat")

    @chat.websocket_route("/room/{name}", receive_type="json", send_type="text")
    async def chat_room(ws: WebSocket, name: str):
        async with ws:
            message = await ws.receive()
            await ws.send(f"[{name}]: {message['text']}")

    app.recipe(chat)

    with app.client.websocket_connect("/chat/room/test") as client:
        client.send_json({"text": "Hello"})
        assert client.receive_text() == "[test]: Hello"
