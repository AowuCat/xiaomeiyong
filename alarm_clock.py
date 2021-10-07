import datetime
import pickle
import os


class _Task:
    def __init__(self, hour, minute, second, is_daily, wav_filepath):
        self.hour = hour
        self.minute = minute
        self.second = second
        self.is_daily = is_daily
        self.is_valid = True
        self.wav_filepath = wav_filepath


class AlarmClock:
    def __init__(self):
        self._day = datetime.datetime.today().day
        self._dump_filepath = "cache/_AlarmClock.dmp"
        self.default_wav_filepath = "music/起床号.wav"
        if os.path.isfile(self._dump_filepath):
            f = open(self._dump_filepath, "rb")
            self._task_list = pickle.load(f)
            f.close()
        else:
            self._task_list = []

    def add(self, hour, minute, second=0, is_daily=False, wav_filepath=None):
        if wav_filepath is None:
            wav_filepath = self.default_wav_filepath
        for i in self._task_list:
            if i.hour == hour and i.minute == minute and i.second == second:
                i.wav_filepath = wav_filepath
                if is_daily:
                    i.is_daily = True
                return

        task = _Task(hour, minute, second, is_daily, wav_filepath)
        self._task_list.append(task)

    def remove(self, hour, minute):
        flag = False
        temp = []
        for i in self._task_list:
            if not i.hour == hour or not i.minute == minute:
                temp.append(i)
            else:
                flag = True
        self._task_list = temp
        return flag

    def clear(self):
        self._task_list.clear()

    def check(self):
        self._clean()
        t = datetime.datetime.today()
        second = t.hour * 3600 + t.minute * 60 + t.second
        for i in self._task_list:
            i_second = i.hour * 3600 + i.minute * 60 + i.second
            if i.is_valid and 0 <= second - i_second <= 5:
                i.is_valid = False
                return i.wav_filepath
        return None

    def task2text(self):
        self._clean()
        if len(self._task_list) == 0:
            return "当前没有设置任何闹钟。"
        text = "当前闹钟数量，%d。" % len(self._task_list)
        for i in range(len(self._task_list)):
            item = self._task_list[i]
            if len(self._task_list) != 1:
                text += "第%d个闹钟，" % (i + 1)
            if item.is_daily:
                text += "每天"
            text += "%d点%d分。" % (item.hour, item.minute)
        return text

    def _clean(self):
        temp = []
        for i in self._task_list:
            if i.is_daily or i.is_valid:
                temp.append(i)
        self._task_list = temp

        if datetime.datetime.today().day != self._day:
            self._day = datetime.datetime.today().day
            for i in self._task_list:
                i.is_valid = True

    def save_to_disk(self):
        f = open(self._dump_filepath, "wb")
        pickle.dump(self._task_list, f)
        f.close()
