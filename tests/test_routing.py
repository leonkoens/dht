import unittest

from dht import settings

from dht.bucket import NodeAlreadyAddedException, BucketIsFullException
from dht.node import Node, SelfNode
from dht.routing import BucketTree, BucketNode
from dht.utils import hash_string


class BucketTreeTest(unittest.TestCase):
    """
    BucketTree.find_node(key)
    BucketTree.find_nodes(key)
    BucketTree.add_node(node)
    """

    def get_new_tree(self):
        """ Helper function to get a new BucketTree. """
        tree = BucketTree(SelfNode('0', '127.0.0.1', '9999'))
        assert len(tree.bucket_node_list) == 3
        return tree

    def test_add_neighbour(self):
        """ Test add_node on BucketTree with the neighbour of SelfNode. This should
        create settings.KEY_SIZE + 1 nodes. """

        tree = self.get_new_tree()

        # This node is right next to the SelfNode, this creates lots of Buckets.
        node = Node('1', None, None)
        tree.add_node(node)

        # KEY_SIZE * 2 because of left and right nodes, plus one because of the root.
        expected_amount = settings.KEY_SIZE * 2 + 1
        assert len(tree.bucket_node_list) == expected_amount

    def test_add_node_twice(self):
        """ Add a Node twice. This should raise a NodeAlreadyAddedException. """

        tree = self.get_new_tree()
        key = hash_string('test')

        node1 = Node(key, None, None)
        node2 = Node(key, None, None)

        tree.add_node(node1)

        # Adding a Node with a key that is already in the tree should raise an Exception in add_node
        # and it should return False.
        self.assertFalse(tree.add_node(node2))

    def test_find_node(self):
        """ Find a Node in the BucketTree. """

        tree = self.get_new_tree()
        key = hash_string('test')

        node1 = Node(key, None, None)
        tree.add_node(node1)

        # Looking for the key again should return the same Node.
        node2 = tree.find_node(key)

        self.assertEqual(node1, node2)

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
            node = Node(key, None, None)
            tree.add_node(node)

        i += 1
        key = hex(dec_key + i)[2:]
        node = Node(key, None, None)

        # Bucket should be full by now.
        self.assertFalse(tree.add_node(node))

    def test_find_nodes(self):

        tree = self.get_new_tree()

        for i in range(18):
            key = hash_string(str(i))
            node = Node(key, None, None)
            tree.add_node(node)

        nodes = tree.find_nodes(hash_string('test'))

        # 18 other nodes + self = 19.
        self.assertEqual(len(nodes), 19)

        tree.add_node(Node(hash_string('extra'), None, None))
        nodes = tree.find_nodes(hash_string('test'))

        # 19 other nodes + self = 20.
        self.assertEqual(len(nodes), 20)

        tree.add_node(Node(hash_string('more than 20'), None, None))
        nodes = tree.find_nodes(hash_string('test'))

        # 20 other nodes + self = 20 because of the bucket size.
        self.assertEqual(len(nodes), 20)


class BucketNodeTest(unittest.TestCase):

    def test_split(self):

        bucket_node = BucketNode()

        self.assertTrue(bucket_node.bucket is not None)
        self.assertEqual(bucket_node.left, None)
        self.assertEqual(bucket_node.right, None)

        left, right = bucket_node.split()

        self.assertEqual(left.parent, bucket_node)
        self.assertEqual(right.parent, bucket_node)

        self.assertEqual(left.route, '1')
        self.assertEqual(right.route, '0')

        self.assertTrue(bucket_node.bucket is None)
        self.assertEqual(bucket_node.left, left)
        self.assertEqual(bucket_node.right, right)


    def test_range(self):

        max_range = pow(2, settings.KEY_SIZE) - 1

        bucket_node = BucketNode()
        bucket_node.route = '0'

        bucket_node_range = bucket_node.get_range()

        self.assertEqual(bucket_node_range[0], 0)
        self.assertEqual(float(bucket_node_range[1]), max_range / 2)

        bucket_node = BucketNode()
        bucket_node.route = '1'

        bucket_node_range = bucket_node.get_range()

        self.assertEqual(float(bucket_node_range[0]), max_range / 2)
        self.assertEqual(bucket_node_range[1], max_range)

