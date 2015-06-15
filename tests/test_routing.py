import unittest

from dht.node import Node
from dht.routing import BucketTree


class BucketTreeTest(unittest.TestCase):

    def test_add_node(self):
        tree = BucketTree()

        assert len(tree.bucket_node_list) == 1

        node = Node(key='testkey')
        tree.add_node(node)

        assert len(tree.bucket_node_list) == 2
