import socket
import sys

port_ip = 0000  # TODO: get from Shay
MSGLEN = sys.getsizeof('Setup WB4 WA3 WC2 BG7 WD4 BG6 BE7 WB4 WA3 WC2 BG7 WD4 BG6 BE7 BG6 BE7 BLACK')

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
        server_address = (host, int(port))
        self.sock.connect(server_address)
        print(sys.stderr, 'starting up on %s port %s' % server_address)
        #self.sock.bind(server_address)
        msg = "Welcome"
        if self.recieve(msg) != msg:  # maybe unnecessary
            raise RuntimeError("Welcome message expected")

    def recieve(self, msg=None):
        if msg is None:
            msg_len = MSGLEN
        else:
            msg_len = sys.getsizeof(msg)
        chunk = self.sock.recv(msg_len)
        if chunk == b'':
            raise RuntimeError("Socket connection broken")
        return chunk.decode("utf-8").rstrip("\n")

    def send(self, msg):
        msg += '\n'
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(bytes(msg[totalsent:], 'UTF-8'))
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def disconnect(self):
        self.sock.close()




