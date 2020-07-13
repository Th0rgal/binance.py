import os, sys, toml, shutil, asyncio

# to import binance.py from the dev directory, you can actually remove this line
# if you just want to start your bot from this base
sys.path.append("../")
import binance


class Config:
    def __init__(self, file_name, template_name):
        config_file = self.extract_config(file_name, template_name)
        self.load_config(config_file)

    def get_path(self, name):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)

    def extract_config(self, file_name, template_name):
        config_file = self.get_path(file_name)
        if not os.path.isfile(config_file):
            print("config file doesn't exist, copying template!")
            shutil.copyfile(self.get_path(template_name), config_file)
        return config_file

    def load_config(self, config_file):
        config = toml.load(config_file)

        binance = config["binance"]
        self.api_key = binance["api_key"]
        self.api_secret = binance["api_secret"]


def on_price_change(event):
    print(
        f"symbol: {event.symbol}, best bid: {event.best_bid_quantity}×{event.best_bid_price}, best ask: {event.best_ask_quantity}×{event.best_ask_price}"
    )


async def main(loop):
    # /!\ Never hardcode your api secrets, prefer to use a config (I love toml, yaml is fine, json works)
    # Don't forget to add your config to .gitignore and give a template
    config = Config("config.toml", "config.template.toml")
    client = binance.Client(config.api_key, config.api_secret)
    # we load the client (this is not mandatory but it allows binance.py
    # to prevent you if you entered a wrong token name for example)
    await client.load()
    # we register the events
    # client.events.register_event(on_price_update, "ethbtc@bookTicker")
    client.events.register_event(on_price_change, "ethbtc@bookTicker")
    # we start the data stream
    loop.create_task(client.start_market_events_listener())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))
    # because we don't want to exit but wait for events
    loop.run_forever()
