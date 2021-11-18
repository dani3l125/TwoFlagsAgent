import socket
import sys

port_ip = 10000  # TODO: get from Shay
MSGLEN = sys.getsizeof('aaaa')

class Socket:
    """
    Comunicate with server
    """

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host='localhost', port=port_ip):
        server_address = (host, port)
        self.sock.connect(server_address)
        print(sys.stderr, 'starting up on %s port %s' % server_address)
        self.sock.bind(server_address)
        msg = "Welcome"
        if self.recieve(msg) != msg:  # maybe unnecessary
            raise RuntimeError("Welcome message expected")

    def recieve(self, msg = None):  # TODO: find correct messages sizes
        chunks = []
        bytes_recd = 0
        if msg is None:
            msg_len = MSGLEN
        else:
            msg_len = sys.getsizeof(msg)
        while bytes_recd < msg_len:
            # Recieve data in small chunks
            chunk = self.sock.recv(min(msg_len - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("Socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

    def send(self, msg):
        totalsent = 0
        while totalsent < sys.getsizeof(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def disconnect(self):
        self.sock.close()




