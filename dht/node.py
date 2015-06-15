import datetime
from dht import settings


class Node:

    def __init__(self, key, last_seen=None):
        self.key = key

        if last_seen is None:
            current_time = datetime.datetime.now()
            last_seen = current_time.timestamp()

        self.last_seen = last_seen

    def get_bin_key(self):
        return bin(int(self.key, 16))[2:].zfill(settings.KEY_SIZE)


class SelfNode(Node):
    pass
