# Distributes Hash Table

This is a [Kademlia distributed hash table](http://en.wikipedia.org/wiki/Kademlia) build in `Python >= 3.5` with [asyncio](https://docs.python.org/3.5/library/asyncio.html).


# Usage

## Starting the network

    PYTHONPATH=$(pwd) python3 dht/main.py --listen-port 9999

## Connecting to the network

    PYTHONPATH=$(pwd) python3 dht/main.py --listen-port 9998 --initial-node 127.0.0.1:9999

# Running tests

    python3 -m unittest

# Original paper

[Link to the original paper](https://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf) or see the pdf in the project.
