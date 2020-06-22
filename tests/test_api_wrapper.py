import sys, unittest

sys.path.append("../")
import binance


class TestConnection(unittest.TestCase):
    def test_object_created(self):
        client = binance.Client()


if __name__ == "__main__":
    unittest.main()
