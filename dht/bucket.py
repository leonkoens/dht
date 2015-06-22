from dht import settings
from dht.node import SelfNode


class BucketHasSelfException(Exception):
    pass


class NodeNotFoundException(Exception):
    pass


class NodeAlreadyAddedException(Exception):
    pass


class BucketIsFullException(Exception):
    pass


class Bucket:
    """ A Bucket is a list of sorted Nodes by last_seen. """

    def __init__(self,
                 nodes_size=settings.BUCKET_SIZE,
                 replacement_cache_size=settings.BUCKET_REPLACEMENT_CACHE_SIZE):
        """ Init the Bucket. """
        self.nodes = []
        self.nodes_size = nodes_size
        self.replacement_cache = []
        self.replacement_cache_size = replacement_cache_size
        self.has_self = False

    def add_node(self, node):
        """ Add a node to this bucket. """

        if self.has_self:
            raise BucketHasSelfException('This Bucket has SelfNode, split this Bucket.')

        if isinstance(node, SelfNode):
            self.has_self = True

        try:
            self.find_node(node.key)
            raise NodeAlreadyAddedException()
        except NodeNotFoundException:
            pass

        if len(self.nodes) < self.nodes_size:
            self.nodes.append(node)
            self.sort()
        elif len(self.replacement_cache) < self.replacement_cache_size:
            self.add_replacement(node)
        else:
            raise BucketIsFullException()

    def find_node(self, key):
        """ Find and return a Node by key in this Bucket. """
        try:
            return next(node for node in self.nodes if node.key == key)
        except StopIteration:
            raise NodeNotFoundException()

    def remove_node(self, key):
        """ Remode and return a Node from this Bucket. """
        (node, index) = next(
            (self.nodes[i], i) for i in range(len(self.nodes)) if self.nodes[i].key == key)
        del self.nodes[index]
        return node

    def sort(self):
        """ Sort the nodes of this Bucket by last_seen. """
        self.nodes.sort(key=lambda node: node.last_seen)

    def add_replacement(self, node):
        self.replacement_cache.append(node)
