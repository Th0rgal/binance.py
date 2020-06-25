from . import __version__
import aiohttp, asyncio


class UserDataStream:
    def __init__(self, client, endpoint, user_agent):
        self.client = client
        self.endpoint = endpoint
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = f"binance.py (https://git.io/binance, {__version__})"

    async def _heartbeat(
        self, listen_key, interval=60 * 30
    ):  # 30 minutes is recommended according to
        # https://github.com/binance-exchange/binance-official-api-docs/blob/master/user-data-stream.md#pingkeep-alive-a-listenkey
        while True:
            await asyncio.sleep(interval)
            await self.client.keep_alive_listen_key(listen_key)

    async def connect(self):
        session = aiohttp.ClientSession()
        listen_key = (await self.client.start_user_data_stream())["listenKey"]
        web_socket = await session.ws_connect(f"{self.endpoint}/ws/{self.listen_key}")
        asyncio.ensure_future(self._heartbeat(listen_key))

        while True:
            msg = await web_socket.receive()
            if msg.tp == aiohttp.MsgType.text:
                print("msg:" + msg)
                if msg.data == "close":
                    await web_socket.close()
                    break
                else:
                    web_socket.send_str(msg.data + "/answer")
            elif msg.tp == aiohttp.MsgType.closed:
                break
            elif msg.tp == aiohttp.MsgType.error:
                break
