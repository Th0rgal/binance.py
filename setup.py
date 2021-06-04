import setuptools

def get_version(rel_path):
    with open(rel_path) as fp:
        for line in fp:
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as fh:
    required = fh.read().splitlines()

setuptools.setup(
    name="binance.py",
    version=get_version("binance/__init__.py"),
    author="Th0rgal",
    author_email="thomas.marchand@tuta.io",
    description="A python3 binance API wrapper powered by modern technologies such as asyncio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.io/binance.py",
    packages=setuptools.find_packages(),
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
