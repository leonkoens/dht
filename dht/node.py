import datetime

from utils import hex_to_bin


class Node:
    """ A node (peer) in the DHT. """

    def __init__(self, key, protocol=None, last_seen=None):
        self.key = key
        self.protocol = protocol

        # Set last_seen to now()
        if last_seen is None:
            current_time = datetime.datetime.now()
            last_seen = current_time.timestamp()

        self.last_seen = last_seen

    def get_bin_key(self):
        """ Return the binary representation of the key. The key should always be a
        hexadecimal. """
        return hex_to_bin(self.key)


class SelfNode(Node):
    """ SelfNode is the representation of the users' own node. """
    pass
