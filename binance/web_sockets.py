from . import __version__
import aiohttp
import asyncio
import logging
import json


class EventsDataStream:
    def __init__(self, client, endpoint, user_agent):
        self.client = client
        self.endpoint = endpoint
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = f"binance.py (https://git.io/binance.py, {__version__})"

    async def _handle_messages(self, web_socket):
        while True:
            msg = await web_socket.receive()
            if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSE):
                logging.error(
                    "Trying to receive something while the websocket is closed! Trying to reconnect."
                )
                asyncio.ensure_future(self.connect())
            elif msg.type is aiohttp.WSMsgType.ERROR:
                logging.error(
                    f"Something went wrong with the websocket, reconnecting..."
                )
                asyncio.ensure_future(self.connect())
            self._handle_event(json.loads(msg.data))


class MarketEventsDataStream(EventsDataStream):
    def __init__(self, client, endpoint, user_agent):
        super().__init__(client, endpoint, user_agent)

    async def start(self):
        async with aiohttp.ClientSession() as session:
            combined_streams = "/".join(self.client.events.registered_streams)
            self.web_socket = await session.ws_connect(
                f"{self.endpoint}/stream?streams={combined_streams}"
            )
            await self._handle_messages(self.web_socket)

    def _handle_event(self, content):
        if "stream" in content:
            stream_name = content["stream"]
            content = content["data"]
        if isinstance(content, list):
            for event_content in content:
                event_content["stream"] = stream_name
                self.client.events.wrap_event(event_content).fire()
        else:
            content["stream"] = stream_name
            self.client.events.wrap_event(content).fire()


class UserEventsDataStream(EventsDataStream):
    def __init__(self, client, endpoint, user_agent):
        super().__init__(client, endpoint, user_agent)

    async def _heartbeat(
        self, listen_key, interval=60 * 30
    ):  # 30 minutes is recommended according to
        # https://github.com/binance-exchange/binance-official-api-docs/blob/master/user-data-stream.md#pingkeep-alive-a-listenkey
        while True:
            await asyncio.sleep(interval)
            await self.client.keep_alive_listen_key(listen_key)

    async def start(self):
        async with aiohttp.ClientSession() as session:
            listen_key = (await self.client.create_listen_key())["listenKey"]
            web_socket = await session.ws_connect(f"{self.endpoint}/ws/{listen_key}")
            asyncio.ensure_future(self._heartbeat(listen_key))
            await self._handle_messages(web_socket)

    def _handle_event(self, content):
        event = self.client.events.wrap_event(content)
        event.fire()
