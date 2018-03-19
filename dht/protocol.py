import asyncio
import json
import logging

from node import Node


class DHTProtocol(asyncio.Protocol):

    def __init__(self, self_key, bucket_tree, value_store):
        self.self_key = self_key
        self.routing = bucket_tree
        self.value_store = value_store

        self.transport = None
        self.node = None

        self.message_id = 0
        self.messages = {}

    def get_message_id(self):
        """ Get the next message id, just increment our counter. """
        self.message_id += 1
        return self.message_id

    def create_message(self, command, data):
        """ Create a new message. """
        message = {
            "id": self.get_message_id(),
            "command": command,
            "data": data,
            "future": asyncio.Future(),
        }
        return message

    def send_message(self, message):
        """ Send a message to the other end, only send the id, command and
        data keys of the message. """
        self.messages[message['id']] = message

        data = json.dumps({
            'id': message['id'],
            'command': message['command'],
            'data': message['data'],
        })

        logging.debug("Sending: {:s}".format(data))
        self.transport.write(data.encode())

    def data_received(self, data):
        """ Receive data from the other end, determine if it is a command or a
        response and act accordingly. """
        data = data.decode()

        logging.debug("Data received: ")
        logging.debug(data)

        data = json.loads(data)

        if 'command' in data:
            self.command_received(data)

        else:
            self.response_received(data)

    def command_received(self, data):
        """ Receive a command, call the right handle and write the response. """
        commands = {
            "identify": self.handle_identify,
            "find_node": self.handle_find_node,
            "find_value": self.handle_find_value,
            "store": self.handle_store,
        }

        # Get the appropriate command.
        command = commands[data['command']]

        response = command(data['data'])

        if response:

            # Create a response message with the data from the command.
            message = json.dumps({
                "id": data['id'],
                "data": response
            })

            logging.debug("Sending response: {:s}".format(message))

            self.transport.write(message.encode())

    def response_received(self, data):
        """ Receive a response, set the result of the Future. """
        message_id = data['id']
        message = self.messages[message_id]
        message['future'].set_result(data)

        response_handlers = {
            "find_node": self.handle_find_response,
            "find_value": self.handle_find_response,
        }

        if message['command'] in response_handlers:
            response_handlers[message['command']](data)

    def identify(self):
        message = self.create_message("identify", {
            "key": self.self_key,
            "request_key": self.node is None,
        })

        self.send_message(message)

    def find_node(self, key):
        message = self.create_message("find_node", key)
        self.send_message(message)
        return message['future']

    def find_value(self, key):
        message = self.create_message("find_value", key)
        self.send_message(message)
        return message['future']

    def store(self, value):
        message = self.create_message("store", value)
        self.send_message(message)
        return message['future']

    def handle_identify(self, data):
        self.node = Node(data["key"], self)
        self.routing.add_node(self.node)

        if data["request_key"]:
            return {
                "id": self.self_key,
                "request_key": False,
            }

        else:
            return False

    def handle_find_node(self, key):
        """ Give back the closest nodes to the given key. """
        return self.routing.find_nodes(key)

    def handle_find_value(self, key):
        try:
            value = self.value_store.retrieve(key)

        except KeyError:
            value = self.routing.find_nodes(key)

        return value

    def handle_store(self, data):
        self.value_store.store(data)

    def handle_find_response(self, data):

        # When the data is from find_value it can be just the value.
        if type(data) != list:
            return

        for node in data:
            node = Node(node['key'])
            self.routing.add_node(node)



class DHTServerProtocol(DHTProtocol):

    def connection_made(self, transport):
        logging.debug("Connection made with {}".format(transport))
        self.transport = transport


class DHTClientProtocol(DHTProtocol):

    def connection_made(self, transport):
        logging.debug("Connection made with {}".format(transport))
        self.transport = transport

        self.identify()

