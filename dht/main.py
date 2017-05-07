from .utils import hash_string
from .node import SelfNode
from .routing import BucketTree
from .protocol import DHTProtocol

import asyncio
import argparse
import random
import string
import logging


class DHT:

    def __init__(self, listen_port, initial_node=None):
        self.initial_node = initial_node
        self.listen_port = listen_port

        logging.debug("Listening on {}".format(self.listen_port))

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
            local_addr=('0.0.0.0', self.listen_port)
        )

        self.loop.run_until_complete(listen)

    def connect_to_initial_node(self):
        """ Connect to the initial node if one is known. """

        logging.debug("Connecting to initial node: {}".format(self.initial_node))

        connect = self.loop.create_datagram_endpoint(
            lambda: DHTProtocol(self.bucket_tree, self.loop),
            remote_addr=self.initial_node
        )

        _, protocol = self.loop.run_until_complete(connect)

        protocol.find_node(self.self_key)

    def run(self):
        """ Run the loop to start everything. """

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

        self.loop.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='A python DHT')
    parser.add_argument('--initial-node', '-n', help='The initial node to connect to (1.2.3.4:5678).')
    parser.add_argument('--listen-port', '-p', default=9999, help='The port to listen on.')

    args = parser.parse_args()

    if args.initial_node is not None:
        initial_node = tuple(args.initial_node.split(":"))
    else:
        initial_node = None

    dht = DHT(args.listen_port, initial_node)
    dht.run()
