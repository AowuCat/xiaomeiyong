import time

from ASRT import asrt
import tencent_stt
import tts
import core
import connection


class VirtDevices:
    def __init__(self):
        self.stt_local = asrt.SttLocal()
        self.stt_network = tencent_stt.TencentStt()
        self.tts = tts.TTS()
        self.core = core.Core()


class Recorder:
    def __init__(self):
        self.port = ("127.0.0.1", 9527)
        self._server = connection.Connection(source=self.port)

    def is_online(self):
        return self._server.dest != connection.default

    def mute(self):
        if not self.is_online():
            return False
        cmd = "action&mute"
        self._server.send_str(cmd)
        return True

    def unmute(self):
        if not self.is_online():
            return False
        cmd = "action&unmute"
        self._server.send_str(cmd)
        return True

    def update(self):
        msg, port = self._server.get_str()
        if msg is None:
            return None
        if msg == "action&register":
            self._server.dest = port
            self._server.send_str("action&ACK")
            return None
        if msg.startswith("action&new_record"):
            cmd = msg.split("|")
            option = cmd[1].split("&")[0]
            if option == "filepath":
                filepath = cmd[1].split("&")[1]
                return filepath
            else:  # base64模式，待完善
                return None
        return None

    def is_mute(self):
        self._server.send_str("action&is_mute")
        while True:
            msg, port = self._server.get_str()
            if msg is None:
                time.sleep(0.05)
                continue
            if msg == "False":
                return False
            if msg == "True":
                return True

    def kill(self):
        self._server.send_str("action&bye")


class Player:
    def __init__(self):
        self.port = ("127.0.0.1", 9528)
        self._server = connection.Connection(source=self.port)

    def is_online(self):
        return self._server.dest != connection.default

    def play(self, filepath):
        if not self.is_online():
            return False
        cmd = "action&play|filepath&" + filepath
        self._server.send_str(cmd)
        return True

    def clear(self):
        if not self.is_online():
            return False
        cmd = "action&clear"
        self._server.send_str(cmd)
        return True

    def update(self):
        msg, port = self._server.get_str()
        if msg == "action&register":
            self._server.dest = port
            self._server.send_str("action&ACK")

    def is_busy(self):
        self._server.send_str("action&is_busy")
        while True:
            msg, port = self._server.get_str()
            if msg is None:
                time.sleep(0.05)
                continue
            if msg == "False":
                return False
            if msg == "True":
                return True

    def kill(self):
        self._server.send_str("action&bye")


class UiServer:
    def __init__(self):
        self.port = ("0.0.0.0", 9529)
        self._server = connection.Connection(source=self.port)

    def update(self):
        msg, port = self._server.get_str()
        if msg is None:
            return None, None
        self._server.dest = port
        return msg, port

    def reply(self, text):
        self._server.send_str(text)
