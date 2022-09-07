import os
import pickle
import datetime


class _Task:
    def __init__(self, hour, minute, second, is_daily):
        self.hour = hour
        self.minute = minute
        self.second = second
        self.is_daily = is_daily
        self.is_valid = True


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

    def _save_to_disk(self):
        f = open(self._dump_filepath, "wb")
        pickle.dump(self._task_list, f)
        f.close()

    def add(self, hour, minute, second=0, is_daily=False):
        for i in self._task_list:
            if i.hour == hour and i.minute == minute and i.second == second:
                if is_daily:
                    i.is_daily = True
                self._save_to_disk()
                return True
        self._task_list.append(_Task(hour, minute, second, is_daily))
        self._save_to_disk()
        return True

    def remove(self, hour, minute, second=0):
        for i in self._task_list[::-1]:
            if i.hour == hour and i.minute == minute and i.second == second:
                self._task_list.remove(i)
                self._save_to_disk()
                return True
        return False

    def clear(self):
        self._task_list.clear()
        self._save_to_disk()
        return True

    def update(self):
        self._refresh()
        t = datetime.datetime.today()
        second = t.hour * 3600 + t.minute * 60 + t.second
        for i in self._task_list:
            i_second = i.hour * 3600 + i.minute * 60 + i.second
            if i.is_valid and 0 <= second - i_second <= 5:
                i.is_valid = False
                self._save_to_disk()
                return True
        return False

    def _refresh(self):
        is_modified = False
        for i in self._task_list[::-1]:
            if not i.is_valid and not i.is_daily:
                self._task_list.remove(i)
                is_modified = True
        if datetime.datetime.today().day != self._day:
            self._day = datetime.datetime.today().day
            for i in self._task_list:
                if not i.is_valid:
                    is_modified = True
                    i.is_valid = True
        if is_modified:
            self._save_to_disk()

    def task2text(self):
        self._refresh()
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
