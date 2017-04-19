from dht.utils import hash_string
from dht.node import SelfNode
from dht.routing import BucketTree
from dht.server import DHTProtocol

import asyncio
import random
import string


class DHT:

    def __init__(self):
        self.self_key = self.create_self_key()
        self.self_node = self.create_self_node()
        self.bucket_tree = self.create_bucket_tree()
        self.loop = asyncio.get_event_loop()

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
            lambda: DHTProtocol(self.bucket_tree), local_addr=('0.0.0.0', 9999))

        transport, protocol = self.loop.run_until_complete(listen)

    def run(self):
        """ Run the loop to start everything. """

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

        self.loop.close()
