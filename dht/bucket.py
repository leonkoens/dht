from dht import settings


class Bucket:
    """ A Bucket is a list of sorted Nodes by last_seen. """

    def __init__(self, max_size=settings.BUCKET_SIZE):
        """ Init the Bucket. """
        self.nodes = []
        self.max_size = max_size

    def add(self, node):
        """ Add a node to this bucket. """
        self.nodes.append(node)
        self.sort()

    def search(self, key):
        """ Search and return a Node by key in this Bucket. """
        return next(node for node in self.nodes if node.key == key)

    def remove(self, key):
        """ Remode and return a Node from this Bucket. """
        (node, index) = next(
            (self.nodes[i], i) for i in range(len(self.nodes)) if self.nodes[i].key == key)
        del self.nodes[index]
        return node

    def sort(self):
        """ Sort the nodes of this Bucket by last_seen. """
        self.nodes.sort(key=lambda node: node.last_seen)
