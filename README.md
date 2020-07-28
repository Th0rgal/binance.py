<h1 align="center">
  <br>
  <img src="https://oraxen.vercel.app/todo/binance.py.svg" alt="Binance.py logo" width="256">
  <br>
</h1>

<h4 align="center">🦾 A python3 binance API wrapper powered by asyncio and python Decimals.</h4>

<p align="center">
    <a href="https://discord.gg/bhbPCXW" alt="discord">
        <img src="https://img.shields.io/discord/725070664100216922?label=chat&logo=discord"/>
    </a>
    <a href="https://th0rgal.gitbook.io/binance-py/" alt="Docs (gitbook)">
        <img src="https://img.shields.io/badge/docs-gitbook-brightgreen"/>
    </a>
    <a href="https://app.fossa.com/projects/git%2Bgithub.com%2FTh0rgal%2Fbinance.py?ref=badge_shield" alt="FOSSA Status">
        <img src="https://app.fossa.com/api/projects/git%2Bgithub.com%2FTh0rgal%2Fbinance.py.svg?type=shield"/>
    </a>
    <a href="https://pypi.org/project/binance.py/">
        <img src="https://img.shields.io/pypi/dm/binance.py"/>
    </a>
    <a href="https://lgtm.com/projects/g/Th0rgal/binance.py/context:python">
        <img alt="Language grade: Python" src="https://img.shields.io/lgtm/grade/python/g/Th0rgal/binance.py.svg?logo=lgtm"/>
    </a>
</p>


## Get binance.py
To install the library, you can just run the following command:
```console
# Linux/macOS
python3 -m pip install -U binance.py

# Windows
py -3 -m pip install -U binance.py
```

## Why binance.py?
The binance api is complex to grasp and using a wrapper saves time but also ensures that the right practices are adopted. Binance.py offers a modern and asynchronous solution.

## Features
- Covers general endpoints (test connectivity and get exchange informations)
- Covers market data endpoints
- Covers Account endpoints (create and manage orders)
- Covers user data stream (receive real time user updates)
- Covers web socket streams (receive real time market updates)
- Async support
- Completely free and without limitations

## What it does not
- Binance.py does not cover the withdraw API
- Binance.py does not cover the margin trading API
> If you need these features, don't open an issue to ask me to implement them


## Get started

- [Generate an API Key](https://www.binance.com/en/support/articles/360002502072) and assign relevant permissions.
- import binance, create a client and send your first test order:
```python
import binance

client = binance.Client(API_KEY, API_SECRET)
await client.load()

order = await client.create_order(
    "ETHPAX", Side.BUY.value, OrderType.MARKET.value, quantity="1", test=True,
)
print(order)
```
- Check some [examples](https://github.com/Th0rgal/binance.py/tree/master/examples)

## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FTh0rgal%2Fbinance.py.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FTh0rgal%2Fbinance.py?ref=badge_large)

## Donate
- ETH (ENS): ``thomas.ethers.xyz``
- ETH (legacy address): ``0x54c5a92c57A07f33500Ec9977797219D70D506C9``
- BTC: ``bc1qm9g2k3fznl2a9vghnpnwem87p03txl4y5lahyu``