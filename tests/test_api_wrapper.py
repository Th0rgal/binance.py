import sys, unittest, logging, asyncio, time, toml, os, shutil

sys.path.append("../")
import binance

logging.basicConfig(level=logging.INFO)


class Config:
    def __init__(self, file_name, template_name):
        config_file = self.extract_config(file_name, template_name)
        self.load_config(config_file)

    def get_path(self, name):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)

    def extract_config(self, file_name, template_name):
        config_file = self.get_path(file_name)
        if not os.path.isfile(config_file):
            logging.info("config file doesn't exist, copying template!")
            shutil.copyfile(self.get_path(template_name), config_file)
        return config_file

    def load_config(self, config_file):
        config = toml.load(config_file)

        binance = config["binance"]
        self.api_key = binance["api_key"]
        self.api_secret = binance["api_secret"]


class TestQueries(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        config = Config("config.toml", "config.template.toml")
        self.client = binance.Client(config.api_key, config.api_secret)

    async def test_connection(self):
        start = time.time()
        response = await self.client.ping()
        delay = time.time() - start
        logging.info(f"Binance pinged in {delay}s")
        self.assertEqual(response, {})

    async def test_server_time(self):
        server_time = (await self.client.fetch_server_time())["serverTime"]
        self.assertTrue(server_time)

    async def test_load(self):
        await self.client.load()
        self.assertTrue(self.client.rate_limits)

    async def test_order_book(self):
        symbol = "ETHBTC"
        default_limit = await self.client.fetch_order_book(symbol)
        self.assertTrue(default_limit)
        special_limit = await self.client.fetch_order_book(symbol, 5)
        self.assertTrue(special_limit)
        with self.assertRaises(ValueError):
            await self.client.fetch_order_book(symbol, 3)

    async def test_recent_trade_list(self):
        symbol = "ETHBTC"
        default_limit = await self.client.fetch_recent_trades_list(symbol)
        self.assertTrue(default_limit)
        special_limit = await self.client.fetch_recent_trades_list(symbol, 1)
        self.assertTrue(special_limit)

    async def test_old_trade_list(self):
        symbol = "ETHBTC"
        default_limit = await self.client.fetch_old_trades_list(symbol)
        self.assertTrue(default_limit)
        special_limit = await self.client.fetch_old_trades_list(symbol, 1)
        self.assertTrue(special_limit)


if __name__ == "__main__":
    unittest.main()
