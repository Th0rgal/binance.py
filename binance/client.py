import logging
import http


class Client:
    def __init__(self, endpoint="https://api.binance.com"):
        self.endpoint = "https://api.binance.com"

    def connect(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
