import datetime


class Node:

    def __init__(self, key, last_seen=None):
        self.key = key

        if last_seen is None:
            current_time = datetime.datetime.now()
            last_seen = current_time.timestamp()

        self.last_seen = last_seen
