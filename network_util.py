import time
import socket
import threading
from enum import Enum

class Notification(Enum):
    SERVER_DISCONNECTED = 0
    CLIENT_DISCONNECTED = 1
    SOCKET_MOVED = 2
    SOCKET_ADDED = 3

class Message(Enum):
    GENERAL = "dict(type='{type}', action='{action}', data={data})"

    @staticmethod
    def compile(message, **kwargs):
        return message.value.format(**kwargs)

class SocketManager:
    """Class for managing inputs/outputs of multiple sockets.

    This class provides a simple framework for managing incoming and outgoing data
    between TCP sockets on a specific port. After instantiating a SocketManager, the server or client
    code can read the incoming data from all of its socket connections and write outgoing
    data simply.

    SocketManager handles all incoming connections automatically with a built in listener. New sockets
    are added to its internal sockets list. Messages from those sockets are put in the 'inbox' in the order
    they arrive. These messages can be accessed by the 'read()' method, which will return a list of messages
    and notifications from the manager about new sockets and sockets that have been disconnected. Data can
    be sent to the sockets using the 'write()' method, where outgoing messages are added to the 'outbox'.
    The outbox is periodically checked by each socket for messages to be sent out."""

    def __init__(self, managerType, port):
        """
        Arguments:
        managerType (str): 'server' or 'client'
        port (int): Port number for listening and initial connection
        connectAddress (str): Client only, address to connect to
        """

        self.type = managerType
        self.port = port
        self.sockets = {'default' : []}
        self.socketMap = {}
        self.active = True

        # Server Only
        self.listeningSocket = None     # Socket to listen for connections
        self.listening = False          # Is the server listening?

        self.inbox = {'default' : []}   # List of incoming messages/notifications in format (isMessage, socket, message)
        self.outbox = {}                # socket : list of messages (str)

        self.lock = threading.RLock()   # Threading lock

    @classmethod
    def actAsServer(cls, port):
        """Constructor for SocketManager to run as a Server"""
        serverManager = cls('server', port)
        return serverManager

    @classmethod
    def actAsClient(cls, port):
        """Constructor for SocketManager to run as a Client"""
        clientManager = cls('client', port)
        return clientManager

    def addGroup(self, group):
        assert group not in ('all', 'default'), "Reserved Name Cannot Be Used"
        self.modifySockets('add', group=group)

    def addInbox(self, sock, message):
        """Add socket message to the inbox."""
        group = self.socketMap[sock]    # WARNING: Unlocked access to shared resource 'socketMap'
        self.modifyInbox(False, isMessage=True, sock=sock, message=message, group=group)

    def addNotification(self, notificationType, resource, group='default'):
        """Add notification to the inbox."""
        self.modifyInbox(False, isMessage=False, sock=resource, message=notificationType, group=group)

    def addSocket(self, sock, group='default'):
        """Add socket to list of sockets and start the send/receiver threads for that socket."""
        self.modifySockets('add', sock=sock, group=group)
        self.addNotification(Notification.SOCKET_ADDED, sock)
        threading.Thread(target=self.receiveSocket, args=(sock,)).start()
        threading.Thread(target=self.sendSocket, args=(sock,)).start()

    def connect(self, address, group='default'):
        """Open connection to the address. Client only."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((address, self.port))
        self.addSocket(sock, group)
        return sock

    def getOutbox(self, sock):
        """Get messages from outbox to send."""
        return self.modifyOutbox(True, socks=[sock])

    def listener(self):
        """Listen for connections and add them to the list of sockets. Server only."""
        self.listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Must use first socket in list
        self.listeningSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listeningSocket.bind(('', self.port))
        self.listeningSocket.listen(10)

        while True:
            try:
                clientSocket, address = self.listeningSocket.accept()
                self.addSocket(clientSocket)
            except OSError:
                break

    def modifyInbox(self, get, isMessage=True, message=None, sock=None, group=None):
        """Sentinel function to ensure autonomous modifications to shared resource 'inbox'"""
        with self.lock:
            if get:
                output = list(self.inbox[group])
                self.inbox[group].clear()
                return output
            else:
                self.inbox[group].append((isMessage, sock, message))

    def modifyOutbox(self, get, message=None, socks=None, group=None, exclude=None, terminate=False):
        """Sentinel function to ensure autonomous modifications to shared resource 'outbox'"""
        with self.lock:
            if get:     # remove from outbox
                output = list(self.outbox[socks[0]])
                self.outbox[socks[0]].clear()
                return output
            elif terminate:
                del self.outbox[socks[0]]
            else:       # add to outbox
                if group:
                    if group == 'all':
                        socks = list(self.socketMap.keys())
                    else:
                        socks = self.sockets[group]
                for sock in socks:
                    if sock not in exclude:
                        self.outbox[sock].append(message)

    def modifySockets(self, action, sock=None, group=None, callerID='unknown'):
        """Sentinel function to ensure autonomous modifications to shared resource 'sockets'"""
        if action == 'add':
            if sock:
                self.sockets[group].append(sock)
                self.socketMap[sock] = group
                self.outbox[sock] = []
            else:
                if group not in self.sockets:
                    self.sockets[group] = []
                    self.inbox[group] = []
        elif action == 'remove':
            originalSock = sock
            try:
                group = self.socketMap[sock]
            except KeyError:
                return
            if callerID != 'receive':
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
            try:
                sock.close()
            except OSError:
                pass
            try:
                self.modifyOutbox(False, socks=[sock], terminate=True)
                self.sockets[group].remove(sock)
                del self.socketMap[sock]
            except KeyError:
                pass
            if self.type == 'client':
                self.addNotification(Notification.SERVER_DISCONNECTED, (sock,), group)
            else:
                if callerID == 'receive':
                    self.addNotification(Notification.CLIENT_DISCONNECTED, (originalSock,), group)
        elif action == 'group':     # Place Socket into Group
            currentGroup = self.socketMap[sock]
            self.sockets[currentGroup].remove(sock)
            #if group not in self.sockets:
            #    self.sockets[group] = []
            self.sockets[group].append(sock)
            self.socketMap[sock] = group

    def moveSocket(self, sock, group):
        """Move socket into group"""
        self.modifySockets(action='group', group=group, sock=sock)
        self.addNotification(Notification.SOCKET_MOVED, sock)

    def read(self, group='default'):
        """Get all messages in a group's inbox."""
        return self.modifyInbox(True, group=group)

    def receiveSocket(self, sock):
        """Receive Data From Socket"""
        while True:
            try:
                message = FixedMessage.receive(sock)
                self.addInbox(sock, message)
            except socket.timeout:
                pass
            except BrokenPipeError:
                if self.active:
                    self.addNotification(Notification.CLIENT_DISCONNECTED, sock, "default")
                return
            except OSError:
                return

    def removeSocket(self, sock, callerID='not specified'):
        """Shutdown, close, and remove socket from manager."""
        self.modifySockets('remove', sock=sock, callerID=callerID)

    def sendSocket(self, sock):
        """Send Data To Socket from Outbox"""
        while True:
            try:
                out = self.getOutbox(sock)
                for message in out:
                    message = FixedMessage(data=message)
                    message.sendTo(sock)
            except AssertionError:
                pass
            except KeyError:
                #self.console("Key Error", "room")
                return
            except OSError:
                #self.removeSocket(sock, 'send')
                return
            time.sleep(.1)
        #sock.close()

    def startListener(self):
        """Start listener thread."""
        if self.listening:
            raise AttributeError("Server is already listening.")
        if self.type == 'server':
            threading.Thread(target=self.listener, daemon=True).start()
            self.listening = True
        else:
            raise AssertionError("Only Server Managers can Listen")

    def stopListener(self):
        """Close listener socket, thread will get an OSError and close."""
        if not self.listening:
            raise AttributeError("Server isn't Listening")
        if self.type == 'server':
            self.listeningSocket.close()
            self.listening = False
        else:
            raise AssertionError("Only Server Managers can Listen")

    def terminateGroup(self, group):
        sockList = list(self.sockets[group])
        for sock in sockList:
            self.removeSocket(sock, 'terminate')

    def terminateManager(self):
        """Stop listening and shutdown all sockets."""
        self.active = False
        if self.listening:
            self.stopListener()
        sockList = list(self.socketMap.keys())
        for sock in sockList:
            self.removeSocket(sock, 'terminate')

    def write(self, message, socks=list()):
        """Send message to list of sockets."""
        self.modifyOutbox(False, message=message, socks=socks, exclude=list())

    def writeAll(self, message, exclude=list()):
        self.modifyOutbox(False, message=message, group='all', exclude=exclude)

    def writeGroup(self, message, group, exclude=list()):
        self.modifyOutbox(False, message=message, group=group, exclude=exclude)

class FixedMessage:
    """Class for facilitating communication between clients using fixed length messages."""

    MESSAGE_LENGTH = 1024
    DELIMITER = '|'

    def __init__(self, recipients=None, data=None):
        self.payload = None                           # list of strings of length 1024
        self.recipients = None
        if recipients:
            if type(recipients) == list:
                self.recipients = recipients
            else:
                self.recipients = [recipients]
        if data:
            self.loadData(data)

    def getStrings(self):
        """Return list of strings in the message's payload."""
        return self.payload

    def loadData(self, data):
        """Replace Existing Payload with New Data. Data must be able to be represented by a string
        and reconstructed as such."""
        self.payload = []
        string = str(data).rstrip('\n')
        pack, remaining = string[:FixedMessage.MESSAGE_LENGTH], string[FixedMessage.MESSAGE_LENGTH:]
        while len(remaining) > 0:
            trailing = pack[FixedMessage.MESSAGE_LENGTH - 1]
            pack = pack[:FixedMessage.MESSAGE_LENGTH - 1] + FixedMessage.DELIMITER
            self.payload.append(pack)
            remaining = trailing + remaining
            pack, remaining = remaining[:FixedMessage.MESSAGE_LENGTH], remaining[FixedMessage.MESSAGE_LENGTH:]
        self.payload.append(FixedMessage.padMessage(pack))

    def sendTo(self, s):
        """Send payload to specified socket."""
        for packet in self.payload:
            length = len(packet)
            assert length == FixedMessage.MESSAGE_LENGTH
            try:
                s.send(packet.encode())
            except OSError:
                raise OSError

    def send(self):
        """Send payload to pre-loaded sockets."""
        for s in self.recipients:
            self.sendTo(s)

    @staticmethod
    def padMessage(message, padding=None):
        """Pad string message with whitespace up to length specified by padding"""
        if padding is None:
            padding = FixedMessage.MESSAGE_LENGTH
        length = padding - len(message)
        return message + ' '*length

    @staticmethod
    def receive(s, timeout=None):
        """Receive one complete TCP Message and output its string content."""
        if timeout is not None:
            s.settimeout(timeout)
        output = ''
        try:
            packet = s.recv(FixedMessage.MESSAGE_LENGTH).decode()
            if not packet:
                raise BrokenPipeError
            s.settimeout(10.0)
            while packet[FixedMessage.MESSAGE_LENGTH - 1] == FixedMessage.DELIMITER:
                output += packet[:FixedMessage.MESSAGE_LENGTH - 1]
                packet = s.recv(FixedMessage.MESSAGE_LENGTH).decode()
                if not packet:
                    raise BrokenPipeError
            output += packet.rstrip()
        except socket.timeout:
            raise socket.timeout
        finally:
            s.settimeout(None)
        return output