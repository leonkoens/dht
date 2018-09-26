import argparse
import asyncio
import importlib
import logging
import random
import settings
import string

from collections import deque

from dht.node import SelfNode
from dht.protocol import DHTServerProtocol, DHTClientProtocol
from dht.routing import BucketTree
from dht.utils import hash_string


class DHT:

    def __init__(self, listen_port, initial_node=None):
        self.initial_node = initial_node
        self.listen_port = listen_port

        logging.info("Listening on {}".format(self.listen_port))

        self.value_store = self.create_value_store()
        self.self_key = self.create_self_key()
        self.self_node = self.create_self_node()
        self.bucket_tree = self.create_bucket_tree()

        self.loop = asyncio.get_event_loop()

        self.create_server()

        if self.initial_node is not None:
            self.connect_to_initial_node()
            self.loop.create_task(self.refresh_nodes(key=self.self_key))

        self.loop.create_task(self.connect_to_unconnected_nodes())

    def create_value_store(self):
        """ Create a Store to store values in. """
        module = importlib.import_module('value_stores.' + settings.VALUE_STORE)
        value_store_class = getattr(module, 'MemoryStore')
        return value_store_class()

    def create_self_key(self):
        """ Create a key with which we will identify ourselves. """
        key = hash_string(
            ''.join([random.choice(string.ascii_letters) for _ in range(160)]))

        logging.info("Our key is {}".format(key))

        return key

    def create_self_node(self):
        """ Create a Node to represent ourselves. """
        self_node = SelfNode(key=self.self_key)
        return self_node

    def create_bucket_tree(self):
        """ Create the BucketTree to store Nodes. """
        tree = BucketTree(self.self_node)
        return tree

    def create_server(self):
        """ Create the server to listen for incoming connections. """

        listen = self.loop.create_server(
            lambda: DHTServerProtocol(
                self.self_key, self.bucket_tree, self.value_store, self.listen_port),
            '0.0.0.0',
            self.listen_port
        )

        self.loop.run_until_complete(listen)

    def connect_to_initial_node(self):
        """ Connect to the initial node if one is known. """

        logging.info("Connecting to initial node: {}".format(self.initial_node))

        connect = self.loop.create_connection(
            lambda: DHTClientProtocol(
                self.self_key, self.bucket_tree, self.value_store, self.listen_port),
            self.initial_node[0],
            int(self.initial_node[1])
        )

        self.loop.run_until_complete(connect)

    async def refresh_nodes(self, key=None, wait=None):

        to_check = deque([key])

        while True:

            if wait is None:
                wait = 3

            # TODO maximum wait in the settings
            wait = min(wait * 2, 30)

            logging.debug("refresh_node sleeping {:d} seconds".format(wait))
            await asyncio.sleep(wait)

            try:

                while True:
                    search_key = to_check.pop()

                    nodes = self.bucket_tree.find_nodes(search_key)
                    find_futures = []

                    for node in nodes:
                        if node == self.self_node or node.protocol is None:
                            continue

                        node.protocol.find_node(search_key)

            except IndexError:

                for bucket_node in self.bucket_tree.get_leaf_bucket_nodes(include_self=False):
                    bucket_node_range = bucket_node.get_range()
                    key = hex(random.randrange(bucket_node_range[0], bucket_node_range[1]))[2:]
                    to_check.appendleft(key)

    async def connect_to_unconnected_nodes(self):

        while True:

            await asyncio.sleep(1)

            for node in self.bucket_tree.get_unconnected_nodes():
                logging.debug(node)
                connect = self.loop.create_connection(
                    lambda: DHTClientProtocol(
                        self.self_key, self.bucket_tree, self.value_store, self.listen_port),
                    node.address,
                    int(node.port)
                )

                _, protocol = await connect

                node.protocol = protocol
                protocol.node = node

    def run(self):
        """ Run the loop to start everything. """

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

        self.loop.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='A python DHT')
    parser.add_argument(
        '--initial-node', '-n', help='The initial node to connect to (1.2.3.4:5678).')
    parser.add_argument(
        '--listen-port', '-p', default=9999, help='The port to listen on.')

    parser.add_argument('-v', action='store_true', dest='verbose_info', help='Verbose')
    parser.add_argument('-vv', action='store_true', dest='verbose_debug', help='More verbose')

    args = parser.parse_args()

    if args.verbose_debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.verbose_info:
        logging.basicConfig(level=logging.INFO)

    if args.initial_node is not None:
        initial_node = tuple(args.initial_node.split(":"))
    else:
        initial_node = None

    dht = DHT(args.listen_port, initial_node)
    dht.run()
