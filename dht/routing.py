import logging

from dht.bucket import Bucket, BucketHasSelfException, NodeAlreadyAddedException, BucketIsFullException
from dht.settings import KEY_SIZE, BUCKET_SIZE
from dht.utils import hex_to_bin


class BucketNode:
    """ A BucketNode is a node in a BucketTree which can hold a bucket as
    value. """

    def __init__(self):
        self.parent = None
        self.left = None
        self.right = None
        self.bucket = Bucket()
        self.route = ""

    def split(self) -> tuple:
        """ Make this node a inner node and create two new leaf nodes, a right
        and left BucketNode """

        # Create a left BucketNode.
        left = BucketNode()
        left.route = self.route + "1"
        left.parent = self

        self.left = left

        # Create a right BucketNode.
        right = BucketNode()
        right.route = self.route + "0"
        right.parent = self

        self.right = right

        self.bucket = None

        return (left, right)

    def get_range(self) -> tuple:
        """ Get the range of this node. """
        self.route

        current = self.parent.right
        while len(current.bucket.nodes) == 0:
            current = current.left

        return (int(self.route.zfill(KEY_SIZE), 2), int(current.route.zfill(KEY_SIZE)), 2)


class BucketTree:
    """ The routing tree of Kademlia. This routing tree holds the (K-)Buckets. """

    def __init__(self, self_node) -> None:
        root = BucketNode()
        left, right = root.split()

        self.root_bucket_node = root
        self.bucket_node_list = [root, left, right]
        self.self_node = self_node

        self.add_node(self_node)

    def find_node(self, key) -> 'Node':
        """ Find a node in the BucketTree. Raises NodeNotFound if the node isn't in
        the BucketTree. """
        bucket_node = self._find_bucket_node(hex_to_bin(key))
        node = bucket_node.bucket.find_node(key)
        return node

    def find_nodes(self, key) -> list:
        """ Find nodes in the BucketTree closest to the key. """

        bucket_node = self._find_bucket_node(hex_to_bin(key))

        nodes = []
        visited = []
        current = bucket_node
        to_visit = []

        # Don't add the parent is this is the root.
        if bucket_node.parent is not None:
            to_visit.append(bucket_node.parent)

        while len(nodes) < BUCKET_SIZE:
            # Start a tree traversal to search for similar nodes.

            if current.bucket is not None:
                nodes.extend(current.bucket.nodes)
                visited.append(current)
            elif current.left not in visited:
                to_visit.append(current.left)
            elif current.right not in visited:
                to_visit.append(current.right)

            try:
                # Get the next node to check from the queue.
                current = to_visit.pop(0)
            except IndexError:
                if current.parent is None:
                    # We visited the whole tree so just stop looking any further.
                    break

                # Go up one level in the tree.
                current = current.parent
                visited.append(current)

        return nodes

    def add_node(self, node) -> None:
        """ Add a Node (peer) to the tree. """

        logging.info("Adding node to tree: {:s}".format(node.key))

        key = node.get_bin_key()
        bucket_node = self._find_bucket_node(key)

        try:
            bucket_node.bucket.add_node(node)
        except BucketHasSelfException:
            # Split the Bucket(Node) and add the node again.
            self._split_bucket_node(bucket_node)
            self.add_node(node)
        except (BucketIsFullException, NodeAlreadyAddedException):
            return False

        logging.info("Added node to tree: {:s}".format(node.key))
        return True

    def _find_bucket_node(self, bin_key) -> BucketNode:
        """ Find a BucketNode in the tree by the binary value of a key. """
        bucket_node = self.root_bucket_node
        i = 0

        while bucket_node.bucket is None and i < KEY_SIZE:
            if bin_key[i] == '1':
                bucket_node = bucket_node.left
            else:
                bucket_node = bucket_node.right

            i += 1

        return bucket_node

    def _split_bucket_node(self, bucket_node) -> None:
        """ Split a BucketNode and its Bucket. """

        logging.debug("Splitting a Bucket")

        bucket = bucket_node.bucket
        left, right = bucket_node.split()

        self.bucket_node_list.append(left)
        self.bucket_node_list.append(right)

        # Re-add all the nodes in Bucket that is now unreachable.
        for node in bucket.nodes:
            self.add_node(node)

    def get_unconnected_nodes(self) -> list:
        """ Get the unconnected nodes in this BucketTree. """

        unconnected = []

        for bucket_node in self.get_leaf_bucket_nodes(include_self=False):
            unconnected.extend(bucket_node.bucket.get_unconnected_nodes())

        return unconnected

    def get_leaf_bucket_nodes(self, include_self=False) -> list:
        """ Get the leaf bucket nodes; those that actually hold nodes.  """

        bucket_nodes = []

        for bucket_node in self.bucket_node_list:

            if bucket_node.bucket is not None:

                if bucket_node.bucket.has_self and not include_self:
                    continue

                bucket_nodes.append(bucket_node)

        return bucket_nodes
