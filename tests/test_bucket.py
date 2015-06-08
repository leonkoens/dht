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

        bucket.add(node)

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

        bucket.add(node1)
        bucket.add(node2)
        bucket.add(node3)
        bucket.add(node4)

        for i in range(len(bucket.nodes) - 1):
            self.assertTrue(bucket.nodes[i].last_seen < bucket.nodes[i + 1].last_seen)

    def test_search_node(self):
        """ Test the searching of a Node in a Bucket. """

        key = "b8942cb015e4905e643d07d5492e46178a1ebe29f8d8ac0da493f2ad1c4f3ced4fabf5e6642e014" \
             "efd6b226c13fb6c94"

        bucket = Bucket()
        node1 = Node(key=key)
        node2 = Node(key='nokey')

        bucket.add(node1)
        bucket.add(node2)

        node3 = bucket.search(key)

        self.assertEquals(node3, node1)

    def test_remove_node(self):
        """ Test the removing of a Node from a Bucket, removing a Node should also return
        that Node. """

        key = "b8942cb015e4905e643d07d5492e46178a1ebe29f8d8ac0da493f2ad1c4f3ced4fabf5e6642e014" \
             "efd6b226c13fb6c94"

        bucket = Bucket()
        node1 = Node(key=key)
        node2 = Node(key='nokey')

        bucket.add(node1)
        bucket.add(node2)

        node3 = bucket.remove(key)

        self.assertEquals(node1, node3)
