from .utils import hash_string
from .node import SelfNode
from .routing import BucketTree
from .protocol import DHTProtocol

import asyncio
import argparse
import random
import string


class DHT:

    def __init__(self, initial_node=None):
        self.initial_node = initial_node

        self.self_key = self.create_self_key()
        self.self_node = self.create_self_node()
        self.bucket_tree = self.create_bucket_tree()

        self.loop = asyncio.get_event_loop()

        self.create_server()

        if self.initial_node is not None:
            self.connect_to_initial_node()

    def create_self_key(self):
        """ Create a key with which we will identify ourself. """
        key = hash_string(
            ''.join([random.choice(string.ascii_letters) for _ in range(160)]))
        return key

    def create_self_node(self):
        """ Create a Node to repesent ourself. """
        self_node = SelfNode(key=self.self_key)
        return self_node

    def create_bucket_tree(self):
        """ Create the BucketTree to store Nodes. """
        tree = BucketTree(self.self_node)
        return tree

    def create_server(self):
        """ Create the UDP server to listen for incoming connections. """

        listen = self.loop.create_datagram_endpoint(
            lambda: DHTProtocol(self.bucket_tree, self.loop),
            local_addr=('0.0.0.0', 9999)
        )

        self.loop.run_until_complete(listen)

    def connect_to_initial_node(self):
        """ Connect to the initial node if one is known. """

        self.loop.create_datagram_endpoint(
            lambda: DHTProtocol(self.bucket_tree, self.loop),
            remote_addr=self.initial_node
        )

    def run(self):
        """ Run the loop to start everything. """

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

        self.loop.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A python DHT')
    parser.add_argument('--initial-node', help='The initial node to connect to.')

    args = parser.parse_args()

    dht = DHT(args.initial_node)
    dht.run()
