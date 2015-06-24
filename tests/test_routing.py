import unittest

from dht.node import Node, SelfNode
from dht.routing import BucketTree
from dht.utils import hash_string

from dht.bucket import NodeAlreadyAddedException, BucketIsFullException
from dht import settings


class BucketTreeTest(unittest.TestCase):
    """
    BucketTree.find_node(key)
    BucketTree.add_node(node)
    """

    def get_new_tree(self):
        """ Helper function to get a new BucketTree. """
        tree = BucketTree(SelfNode(key='0'))
        assert len(tree.bucket_node_list) == 1
        return tree

    def test_add_neighbour(self):
        """ Test add_node on BucketTree with the neighbour of SelfNode. This should
        create settings.KEY_SIZE + 1 nodes. """

        tree = self.get_new_tree()

        # This node is right next to the SelfNode, this creates lots of Buckets.
        node = Node(key='1')
        tree.add_node(node)
        assert len(tree.bucket_node_list) == settings.KEY_SIZE + 1

    def test_add_node_twice(self):
        """ Add a Node twice. This should raise a NodeAlreadyAddedException. """

        tree = self.get_new_tree()
        key = hash_string('test')

        node1 = Node(key=key)
        node2 = Node(key=key)

        tree.add_node(node1)

        # Adding a Node with a key that is already in the tree should raise an Exception.
        with self.assertRaises(NodeAlreadyAddedException):
            tree.add_node(node2)

    def test_find_node(self):
        """ Find a Node in the BucketTree. """

        tree = self.get_new_tree()
        key = hash_string('test')

        node1 = Node(key=key)
        tree.add_node(node1)

        # Looking for the key again should return the same Node.
        node2 = tree.find_node(key)

        self.assertEquals(node1, node2)

    def test_full_bucket(self):
        """ A Bucket should raise an BucketIsFullException when the Bucket's Node list and
        replacement cache are full. """

        tree = self.get_new_tree()

        # This begins with a 1 in binary.
        key = hash_string('test')
        dec_key = int(key, 16)

        # Add keys in the same Bucket.
        for i in range(0, settings.BUCKET_SIZE + settings.BUCKET_REPLACEMENT_CACHE_SIZE):
            key = hex(dec_key + i)[2:]
            node = Node(key=key)
            tree.add_node(node)

        i += 1
        key = hex(dec_key + i)[2:]
        node = Node(key=key)

        # Bucket should be full by now.
        with self.assertRaises(BucketIsFullException):
            tree.add_node(node)
