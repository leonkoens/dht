from dht import settings
from dht.node import SelfNode


class BucketHasSelfException(Exception):
    pass


class NodeNotFoundException(Exception):
    message = 'Node not found'


class NodeAlreadyAddedException(Exception):
    pass



class Bucket:
    """ A Bucket is a list of sorted Nodes by last_seen. """

    def __init__(self, max_size=settings.BUCKET_SIZE):
        """ Init the Bucket. """
        self.nodes = []
        self.max_size = max_size
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
            self.nodes.append(node)
            self.sort()

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
