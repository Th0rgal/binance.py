import sys

sys.path.append("../")
import binance

def test_http():
    binance.http.test()

if __name__ == "__main__":
      test_http()