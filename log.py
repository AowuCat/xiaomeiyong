import time
import datetime


def get_time():
    timestamp = time.time()
    time_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d-%H-%M-%S")
    return time_str


class Log:
    def __init__(self):
        self.filepath = "log/log_" + get_time() + ".txt"
        self.f = open(self.filepath, "w", encoding="utf-8")
        self.write("日志记录开始")

    def write(self, text, level="info", show=True):
        s = "%s [%s]: %s\n" % (get_time(), level, text)
        self.f.write(s)
        self.f.flush()
        if show:
            print(s, end="")
