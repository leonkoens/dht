import unittest
from unittest import mock

from node import Node
from protocol import DHTProtocol


class DHTProtocolTest(unittest.TestCase):

    @staticmethod
    def create_protocol(self_key=None):
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
        """ Test the find_node flow between two protocols. """

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

        # Check that the response is written to the transport.
        self.assertTrue(transport_b.write.called)

        # Get the response.
        output = transport_b.write.call_args[0][0]

        # Feed the response to the original protocol.
        protocol_a.data_received(output)

        self.assertTrue(len(protocol_a.messages) == 0)

        self.assertTrue(tree_a.add_node.called)
        self.assertTrue(len(tree_a.add_node.call_args_list) == 3)

    def test_find_value_without_result(self):
        """ Test the find_value flow between two protocols when the value isn't at the protocol
        receiving the request. """

        protocol_a, transport_a, tree_a, _ = self.create_protocol('protocol_a')
        protocol_b, transport_b, tree_b, store_b = self.create_protocol('protocol_b')

        self.assertTrue(len(protocol_a.messages) == 0)

        future = protocol_a.find_value('testkey')

        # Check that a message has been sent.
        self.assertTrue(transport_a.write.called)
        self.assertTrue(len(protocol_a.messages) == 1)

        # Get the message.
        output = transport_a.write.call_args[0][0]

        # Let the value store raise an Key error, so that handle_find_value returns nodes.
        store_b.retrieve.side_effect = KeyError
        tree_b.find_nodes.return_value = [
            Node('first', '127.0.0.1', 1234),
            Node('second', '127.0.0.1', 5678),
            Node('third', '127.0.0.1', 9100),
        ]

        # Feed the message to the other protocol.
        protocol_b.data_received(output)

        # Check that the value store is called.
        self.assertTrue(store_b.retrieve.called)
        self.assertTrue(store_b.retrieve.call_args[0][0] == 'testkey')

        # Value store should've raised a KeyError, therefor the routing tree should've been called.
        self.assertTrue(tree_b.find_nodes.called)
        self.assertTrue(tree_b.find_nodes.call_args[0][0] == 'testkey')

        # Check that the response is written to the transport.
        self.assertTrue(transport_b.write.called)

        # Get the response.
        output = transport_b.write.call_args[0][0]

        # Feed the response to the original protocol.
        protocol_a.data_received(output)

        # There shouldn't be any messages left.
        self.assertTrue(len(protocol_a.messages) == 0)

        # Because there is no value returned, store the returned nodes in the routing tree.
        self.assertTrue(tree_a.add_node.called)
        self.assertTrue(len(tree_a.add_node.call_args_list) == 3)

        # The result on the future should be the returned nodes.
        self.assertTrue(len(future.result()) == 3)

    def test_find_value_with_result(self):
        """ Test the find_value flow between two protocols when the value is at the protocol
        receiving the request. """

        protocol_a, transport_a, tree_a, _ = self.create_protocol('protocol_a')
        protocol_b, transport_b, tree_b, store_b = self.create_protocol('protocol_b')

        self.assertTrue(len(protocol_a.messages) == 0)

        future = protocol_a.find_value('testkey')

        # Check that a message has been sent.
        self.assertTrue(transport_a.write.called)
        self.assertTrue(len(protocol_a.messages) == 1)

        # Get the message.
        output = transport_a.write.call_args[0][0]

        # Let the value store return a value.
        store_b.retrieve.return_value = 'value'

        # Feed the message to the other protocol.
        protocol_b.data_received(output)

        # Check that the value store is called.
        self.assertTrue(store_b.retrieve.called)
        self.assertTrue(store_b.retrieve.call_args[0][0] == 'testkey')

        # Routing tree should not be called.
        self.assertTrue(not tree_b.find_nodes.called)

        # Check that the response is written to the transport.
        self.assertTrue(transport_b.write.called)

        # Get the response.
        output = transport_b.write.call_args[0][0]

        # Feed the response to the original protocol.
        protocol_a.data_received(output)

        # There shouldn't be any messages left.
        self.assertTrue(len(protocol_a.messages) == 0)

        # Check that add_node isn't called, there are no nodes to be added.
        self.assertTrue(not tree_a.add_node.called)

        self.assertTrue(future.result() == 'value')

    def test_store(self):
        """ Test the store flow of DHTProtocol """

        protocol_a, transport_a, tree_a, _ = self.create_protocol('protocol_a')
        protocol_b, transport_b, tree_b, store_b = self.create_protocol('protocol_b')

        self.assertTrue(len(protocol_a.messages) == 0)

        future = protocol_a.store('testvalue')

        # Check that a message has been sent.
        self.assertTrue(transport_a.write.called)
        self.assertTrue(len(protocol_a.messages) == 1)

        # Get the message.
        output = transport_a.write.call_args[0][0]

        # Feed the message to the other protocol.
        protocol_b.data_received(output)

        # Check that the value store is called.
        self.assertTrue(store_b.store.called)
        self.assertTrue(store_b.store.call_args[0][0] == 'testvalue')

        # Check that the response is written to the transport.
        self.assertTrue(transport_b.write.called)

        # Get the response.
        output = transport_b.write.call_args[0][0]

        # Feed the response to the original protocol.
        protocol_a.data_received(output)

        # There shouldn't be any messages left.
        self.assertTrue(len(protocol_a.messages) == 0)
        self.assertTrue(future.done())





