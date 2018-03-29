import unittest
from unittest import mock

from node import Node
from protocol import DHTProtocol


class DHTProtocolTest(unittest.TestCase):

    def create_protocol(self, self_key=None):
        """ Create a protocol for testing. """

        if self_key is None:
            self_key = 'selfkey'

        bucket_tree = mock.Mock()
        value_store = mock.Mock()

        protocol = DHTProtocol(self_key, bucket_tree, value_store)
        transport = mock.Mock()
        protocol.transport = transport

        return protocol, transport, bucket_tree, value_store

    def test_identify(self):
        """ Test the identify flow. Create 2 protocols and let them identify with each other. The
        methods identify(), handle_identify() and handle_identify_response() are called. """

        protocol_a, transport_a, tree_a, _ = self.create_protocol('protocol_a')
        protocol_b, transport_b, tree_b, _ = self.create_protocol('protocol_b')

        transport_a.get_extra_info.return_value = ('127.0.0.1', 1000)
        transport_b.get_extra_info.return_value = ('127.0.0.2', 1000)

        self.assertTrue(len(protocol_a.messages) == 0)

        protocol_a.identify()

        # Check that a message has been sent.
        self.assertTrue(transport_a.write.called)
        self.assertTrue(len(protocol_a.messages) == 1)

        # Get the message and check for the key.
        output = transport_a.write.call_args[0][0]
        self.assertTrue(protocol_a.self_key in output.decode())

        # Feed the message to the other protocol.
        protocol_b.data_received(output)

        # Check that the routing tree has been called to add a Node with the right key.
        self.assertTrue(tree_b.add_node.called)
        self.assertTrue(tree_b.add_node.call_args[0][0].key == 'protocol_a')

        # Check that the response on the identify is written to the transport.
        self.assertTrue(transport_b.write.called)

        # Get the response, check the key.
        output = transport_b.write.call_args[0][0]
        self.assertTrue(protocol_b.self_key in output.decode())

        # Feed the response to the original protocol.
        protocol_a.data_received(output)

        # The routing tree should've been called to add the Node with the right key.
        self.assertTrue(tree_a.add_node.called)
        self.assertTrue(tree_a.add_node.call_args[0][0].key == 'protocol_b')

        # The messages dict should now be empty again.
        self.assertTrue(len(protocol_a.messages) == 0)

    def test_find_node(self):

        protocol_a, transport_a, tree_a, _ = self.create_protocol('protocol_a')
        protocol_b, transport_b, tree_b, _ = self.create_protocol('protocol_b')

        self.assertTrue(len(protocol_a.messages) == 0)

        protocol_a.find_node('testkey')

        # Check that a message has been sent.
        self.assertTrue(transport_a.write.called)
        self.assertTrue(len(protocol_a.messages) == 1)

        # Get the message.
        output = transport_a.write.call_args[0][0]

        tree_b.find_nodes.return_value = [
            Node('first', '127.0.0.1', 1234),
            Node('second', '127.0.0.1', 5678),
            Node('third', '127.0.0.1', 9100),
        ]

        # Feed the message to the other protocol.
        protocol_b.data_received(output)

        self.assertTrue(tree_b.find_nodes.called)
        self.assertTrue(tree_b.find_nodes.call_args[0][0] == 'testkey')

        # Check that the response on the identify is written to the transport.
        self.assertTrue(transport_b.write.called)

        # Get the response.
        output = transport_b.write.call_args[0][0]

        # Feed the response to the original protocol.
        protocol_a.data_received(output)

        self.assertTrue(len(protocol_a.messages) == 0)

        self.assertTrue(tree_a.add_node.called)
        self.assertTrue(len(tree_a.add_node.call_args_list) == 3)
