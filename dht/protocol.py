
from rudp.protocol import RUDPProtocol


class DHTProtocol(RUDPProtocol):

    def __init__(self, bucket_tree, loop):
        self.loop = loop
        self.bucket_tree = bucket_tree

        super().__init__()

    def data_received(self, data):
        print(data)
