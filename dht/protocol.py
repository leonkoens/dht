import asyncio
import json
import logging

from node import Node


class Message:

    MESSAGE_ID = 0

    def __init__(self, msg_id, data, command=None):
        self.id = msg_id
        self.data = data
        self.command = command

        if command:
            self.future = asyncio.Future()

    def get_bytes(self):
        """ Get the bytes of the message, include the command if it is defined.

        :return: str
        """
        message = {
            "id": self.id,
            "data": self.data,
        }

        if self.command:
            message["command"] = self.command

        message_json = json.dumps(message)
        message_encoded = message_json.encode()

        return message_encoded

    @staticmethod
    def create(command, data):
        """ Create a new Message with the given command and data.

        :param command: str
        :param data: str
        :return: Message
        """
        message = Message(Message.MESSAGE_ID, data, command)
        Message.MESSAGE_ID += 1
        return message

    @staticmethod
    def from_bytes(data):
        """ Create a Message from the given data.

        :param data: str
        :return: Message
        """
        data = json.loads(data.decode())

        if 'command' not in data:
            data['command'] = None

        message = Message(data['id'], data['data'], data['command'])
        return message

    @staticmethod
    def create_reponse(message, data):
        """ Create a response on the given Message.

        :param message: Message
        :param data: str
        :return: Message
        """
        message = Message(message.id, data)
        return message


class DHTProtocol(asyncio.Protocol):

    def __init__(self, self_key, bucket_tree, value_store):
        self.self_key = self_key
        self.routing = bucket_tree
        self.value_store = value_store

        self.transport = None
        self.node = None

        self.messages = {}

    def send_message(self, message):
        """ Send a message to the other end, only send the id, command and
        data keys of the message. """

        self.messages[message.id] = message
        data = message.get_bytes()
        logging.debug("Sending: {:s}".format(data.decode()))
        self.transport.write(data)

    def data_received(self, data):
        """Receive data from the other end, determine if it is a command or a
        response and act accordingly. """

        message = Message.from_bytes(data)

        logging.debug("Data received: ")
        logging.debug(data)

        if message.command:
            self.command_received(message)

        else:
            self.response_received(message)

    def command_received(self, message):
        """ Receive a command, call the right handle and write the response. """
        commands = {
            "identify": self.handle_identify,
            "find_node": self.handle_find_node,
            "find_value": self.handle_find_value,
            "store": self.handle_store,
        }

        # Get the appropriate command.
        command = commands[message.command]

        # Call the command to get the response.
        response = command(message.data)

        if response is not None:
            # Create a response message with the data from the command.
            message = Message.create_reponse(message, response)
            data = message.get_bytes()

            logging.debug("Sending response: {:s}".format(data.decode()))

            self.transport.write(data)

    def response_received(self, message):
        """ Receive a response, set the result of the Future. """

        orig_message = self.messages[message.id]
        orig_message.future.set_result(message.data)

        response_handlers = {
            "identify": self.handle_identify_response,
            "find_node": self.handle_find_response,
            "find_value": self.handle_find_response,
        }

        if orig_message.command in response_handlers:
            response_handlers[orig_message.command](message.data)

        del self.messages[message.id]

    def identify(self):
        message = Message.create('identify', {
            "key": self.self_key,
            "request_key": self.node is None,
        })

        self.send_message(message)

    def find_node(self, key):
        message = Message.create('find_node', key)
        self.send_message(message)
        return message.future

    def find_value(self, key):
        message = self.create_message("find_value", key)
        self.send_message(message)
        return message['future']

    def store(self, value):
        message = self.create_message("store", value)
        self.send_message(message)
        return message['future']

    def handle_identify(self, data):
        socket = self.transport.get_extra_info('peername')
        self.node = Node(data["key"], socket[0], socket[1], self)
        self.routing.add_node(self.node)

        if data["request_key"]:
            return {
                "key": self.self_key,
                "request_key": False,
            }

        else:
            return False

    def handle_find_node(self, key):
        """ Give back the closest nodes to the given key. """
        return [node.get_data() for node in self.routing.find_nodes(key)]

    def handle_find_value(self, key):
        try:
            value = self.value_store.retrieve(key)

        except KeyError:
            value = self.routing.find_nodes(key)

        return value

    def handle_store(self, data):
        self.value_store.store(data)

    def handle_identify_response(self, data):
        """
        Handle the response on our identify() request, add the Node.

        :param data: dict
        """
        socket = self.transport.get_extra_info('peername')
        self.node = Node(data["key"], socket[0], socket[1], self)
        self.routing.add_node(self.node)

    def handle_find_response(self, data):
        """
        Handle the response on our find_value or find_node request.
        :param data: mixed
        """

        # When the data is from find_value it can be just the value.
        if type(data) != list:
            return

        for node in data:
            node = Node(node[0], node[1], node[2])
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

