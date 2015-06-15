from dht.bucket import Bucket, BucketHasSelfException


class BucketNode:

    def __init__(self):
        self.left = None
        self.right = None
        self.bucket = Bucket()


class BucketTree:

    def __init__(self, self_node):
        self.root_bucket_node = BucketNode()
        self.bucket_node_list = []

        self.add_node(self_node)

    def find_bucket(self, bin_key):
        i = 0
        bucket_node = self.root_bucket_node

        while bucket_node.bucket is None:
            if bin_key[i] == '1':
                bucket_node = bucket_node.left
            else:
                bucket_node = bucket_node.right

            i += 1

        bucket = bucket_node.bucket

        return bucket

    def add_node(self, node):
        bin_key = node.get_bin_key()
        bucket = self.find_bucket(bin_key)

        try:
            bucket.add_node(node)
        except BucketHasSelfException:
            # split
            pass
