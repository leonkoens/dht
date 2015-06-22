from dht.bucket import Bucket, BucketHasSelfException
from dht import settings
from dht.utils import hex_to_bin



class BucketNode:
    """ A BucketNode is a node in a BucketTree which can hold a bucket as
    value. """

    def __init__(self):
        self.left = None
        self.right = None
        self.bucket = Bucket()


class BucketTree:
    """ The routing tree of Kademlia. This routing tree holds the (K-)Buckets. """

    def __init__(self, self_node):
        self.root_bucket_node = BucketNode()
        self.bucket_node_list = [self.root_bucket_node]

        self.add_node(self_node)

    def find_node(self, key):
        """ Find a node in the BucketTree. Raises NodeNotFound if the node isn't in
        the BucketTree. """
        bucket_node = self._find_bucket_node(hex_to_bin(key))
        node = bucket_node.bucket.find_node(key)
        return node

    def add_node(self, node):
        """ Add a Node (peer) to the tree. """

        key = node.get_bin_key()
        bucket_node = self._find_bucket_node(key)

        try:
            bucket_node.bucket.add_node(node)
        except BucketHasSelfException:
            # Split the Bucket(Node) and add the node again.
            self._split_bucket_node(bucket_node)
            self.add_node(node)

    def _find_bucket_node(self, bin_key):
        """ Find a BucketNode in the tree by the binary value of a key. """
        bucket_node = self.root_bucket_node
        i = 0

        while bucket_node.bucket is None and i < settings.KEY_SIZE:
            if bin_key[i] == '1':
                bucket_node = bucket_node.left
            else:
                bucket_node = bucket_node.right

            i += 1

        return bucket_node

    def _split_bucket_node(self, bucket_node):
        """ Split a BucketNode and its Bucket. """

        bucket = bucket_node.bucket
        bucket_node.bucket = None

        left = BucketNode()
        right = BucketNode()

        self.bucket_node_list.remove(bucket_node)
        self.bucket_node_list.append(left)
        self.bucket_node_list.append(right)

        bucket_node.left = left
        bucket_node.right = right

        for node in bucket.nodes:
            self.add_node(node)
