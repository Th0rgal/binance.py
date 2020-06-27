import sys, unittest

sys.path.append("../")
from binance.http import HttpClient


class TestSignature(unittest.TestCase):
    # see: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#example-2-as-a-query-string
    def test_example_query_string(self):
        client = HttpClient(
            "vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A",
            "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j",
            None,
            None,
        )
        """ Original query:
        {
            "symbol": "LTCBTC",
            "side": "BUY",
            "type": "LIMIT",
            "timeInForce": "GTC",
            "quantity": 1,
            "price": 0.1,
            "recvWindow": 5000,
            "timestamp": 1499827319559,
        }
        """
        example_query = "symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&price=0.1&recvWindow=5000&timestamp=1499827319559"
        self.assertEqual(
            client._generate_signature(example_query),
            "c8db56825ae71d6d79447849e617115f4a920fa2acdcab2b053c4b2838bd6b71",
        )


if __name__ == "__main__":
    unittest.main()
