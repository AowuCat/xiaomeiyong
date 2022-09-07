import socket
default = ("127.0.0.1", 0)


class Connection:
    def __init__(self, source=default, dest=default, msg_max_length=1024):
        self._client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._client.setblocking(False)
        self.source = source
        if source != default:
            self._client.bind(source)
        self.dest = dest
        self._MSG_MAX_LENGTH = msg_max_length

    def send_str(self, data):
        try:
            # print("send data=%s" % data)
            msg = bytes(data.encode("utf-8"))
            self._client.sendto(msg, self.dest)
            return True
        except BlockingIOError:
            return False

    def get_str(self):
        try:
            data = self._client.recvfrom(self._MSG_MAX_LENGTH)
            msg = data[0].decode("utf-8")
            # print("get msg=%s" % msg)
            return msg, data[1]
        except (BlockingIOError, ConnectionResetError):
            return None, 0
