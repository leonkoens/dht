import datetime
import unittest

from dht.node import Node
from dht.bucket import Bucket


class TestBucket(unittest.TestCase):
    """
    The the Bucket.
    """

    def test_add_node(self):
        """ The the adding of a node to a Bucket. """

        bucket = Bucket()
        node = Node(key='node')

        self.assertEquals(len(bucket.nodes), 0)

        bucket.add_node(node)

        self.assertEquals(len(bucket.nodes), 1)

    def test_add_multiple_nodes(self):
        """ Test the adding of multiple Nodes, the nodes should be sorted by
        last_seen. """

        bucket = Bucket()

        self.assertEquals(len(bucket.nodes), 0)

        current_time = datetime.datetime.now()
        unix_time = current_time.timestamp()

        node1 = Node(key='node1', last_seen=unix_time)
        node2 = Node(key='node2', last_seen=unix_time - 1)
        node3 = Node(key='node3', last_seen=unix_time + 2)
        node4 = Node(key='node4', last_seen=unix_time + 1)

        bucket.add_node(node1)
        bucket.add_node(node2)
        bucket.add_node(node3)
        bucket.add_node(node4)

        for i in range(len(bucket.nodes) - 1):
            self.assertTrue(bucket.nodes[i].last_seen < bucket.nodes[i + 1].last_seen)

    def test_search_node(self):
        """ Test the searching of a Node in a Bucket. """

        bucket = Bucket()

        node1 = Node(key='testkey1')
        node2 = Node(key='testkey2')

        bucket.add_node(node1)
        bucket.add_node(node2)

        node3 = bucket.search_node('testkey1')

        self.assertEquals(node3, node1)

    def test_remove_node(self):
        """ Test the removing of a Node from a Bucket, removing a Node should also return
        that Node. """

        bucket = Bucket()

        node1 = Node(key='testkey1')
        node2 = Node(key='testkey2')

        bucket.add_node(node1)
        bucket.add_node(node2)

        node3 = bucket.remove_node('testkey1')

        self.assertEquals(node1, node3)
