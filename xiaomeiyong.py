import os
import time
import datetime
import random
import re
from recorder import Recorder
from text2wav import Text2Wav
from alarm_clock import AlarmClock
from wakeonlan import send_magic_packet


class Xiaomeiyong:
    def __init__(self, recorder, text2wav, log=True):
        assert (type(recorder) == Recorder)
        assert (type(text2wav) == Text2Wav)
        self._recorder = recorder
        self._text2wav = text2wav
        self._alarm_clock = AlarmClock()
        self._is_wake = False
        self.log = log

    def play_sound_safety(self, filepath, waiting=True):
        self._recorder.pause()
        if os.name == "nt":
            import winsound
            winsound.PlaySound(filepath, winsound.SND_FILENAME)
        else:
            from playsound import playsound
            playsound(filepath)
        self._recorder.pause()

    def answer(self, question, mute=False):
        if self.log:
            print("[info] %s 小没用输入\"%s\"" % (get_time(), question))
        if question is None or len(question) == 0:
            return False
        text = None
        if len(question) <= 5:
            if "用爬" in question or "没用" in question:
                self.sleep(is_active=True)
                return True
        if "几号" in question or "哪天" in question:
            text = _answer_what_day()
        elif "几点" in question or "时间" in question:
            text = _answer_what_time()
        # 夸/骂 黄白猫/黑猫
        elif _praise_or_criticism(question) is not None:
            text = _praise_or_criticism(question)
        elif "闹钟" in question:
            text = _answer_clock(question, self._alarm_clock)
            self._alarm_clock.save_to_disk()
        elif question.startswith("放") or question.startswith("唱") or question.startswith("播"):
            text = _answer_music(question)
        elif "开电脑" in question or "开机" in question:
            mac, ip = _answer_open_computer()
            if self.log:
                print("[info] %s 已发送唤醒包。mac = %s, ip = %s" % (get_time(), mac, ip))
            text = "已发送唤醒包。"
        else:
            text = _answer_in_scripts(question)

        if text is not None and not text.startswith("[music]"):
            if random.random() > 0.9:
                text += "怎么样，我聪明吧！"

        if self.log:
            print("[info] %s 小没用输出\"%s\"" % (get_time(), text))
        if text is not None:
            if mute:
                if self.log:
                    print("[info] 由于mute==True，当前回答将不会播放。")
                return True
            if text.startswith("[music]"):
                filepath = text[7:]  # music/xxx.wav
                music_name = filepath[6:-4]
                self.play_sound_safety(self._text2wav.make_wav("播放音乐，%s。" % music_name))
                self.play_sound_safety(filepath)
            else:
                text_list = re.split("[。！]", text)
                for i in text_list:
                    if i != "":
                        self.play_sound_safety(self._text2wav.make_wav(i))
                        time.sleep(0.1)
            return True
        return False

    def is_wake(self):
        return self._is_wake

    def wake(self):
        if self.is_wake():
            text = "我在。"
        else:
            text = "小没用已唤醒。"
        if self.log:
            print("[info] %s 小没用主动唤醒" % get_time())
        self.play_sound_safety(self._text2wav.make_wav(text))
        self._is_wake = True

    def sleep(self, is_active):
        if self.is_wake() and is_active is True:
            text = "小没用已休眠。"
            if self.log:
                if is_active:
                    print("[info] %s 小没用主动休眠" % get_time())
                else:
                    print("[info] %s 小没用自动休眠" % get_time())
            self.play_sound_safety(self._text2wav.make_wav(text))
        self._is_wake = False

    def check(self):
        # 检查是否有闹钟触发，若触发则打断正在播放的内容，直接播放闹钟
        filepath = self._alarm_clock.check()
        if filepath is not None:
            if self.log:
                print("[info] %s 闹钟被触发" % get_time())
            self.play_sound_safety(filepath, waiting=False)


def _answer_what_day():
    d = datetime.datetime.today()
    if d.weekday() == 6:
        weekday_chinese = "日"
    else:
        weekday_chinese = str(d.weekday() + 1)
    text = "今天是%d年%d月%d日，星期%s。" % (d.year, d.month, d.day, weekday_chinese)
    if d.weekday() >= 5:  # 周六或周日
        text += "周末快乐！"
    return text


def _answer_what_time():
    d = datetime.datetime.today()
    text = "现在是北京时间%d点%d分。" % (d.hour, d.minute)
    return text


def _answer_praise_yellow_white_cat():
    text_list = ["好猫，聪明猫，可爱猫！",
                 "我们黄白猫最可爱最聪明最勇敢最活泼！",
                 "黄白猫是最好的猫！"]
    num = random.randint(0, len(text_list) - 1)
    text = text_list[num]
    if random.random() > 0.5:
        text += "小没用最喜欢夸黄白猫了，要多夸！"
    return text


def _answer_praise_black_cat():
    text_list = ["黑猫真聪明！",
                 "黑猫真可爱！",
                 "黑猫真活泼！",
                 "黄白猫说不能多夸，这次就先算了吧。"]
    num = random.randint(0, len(text_list) - 1)
    text = text_list[num]
    return text


def _answer_criticism_yellow_white_cat():
    text = "黄白猫是我的主人，我不能骂黄白猫！"
    return text


def _answer_criticism_black_cat():
    text_list = ["黑猫真笨！",
                 "黑猫呆呆的！",
                 "黑猫圆圆！",
                 "黑猫吃得多！",
                 "黑猫不会社交！"]
    num = random.randint(0, len(text_list) - 1)
    text = text_list[num]
    return text


def _praise_or_criticism(question):
    if question[-1] == '。' or question[-1] == '!' or question[-1] == '?':
        question = question[:-1]
    praise_words = ["夸", "花", "快"]
    criticism_words = ["骂", "马", "那", "卖", "把", "麦"]
    cat_words = ["猫", "毛", "吗"]
    is_praise = False
    is_criticism = False
    is_cat = False
    cat_type = None

    for i in praise_words:
        if question[0] == i:
            is_praise = True
            break
    for i in criticism_words:
        if question[0] == i:
            is_criticism = True
            break
    for i in cat_words:
        if question[-1] == i:
            is_cat = True
            break
    if "黄白" in question:
        cat_type = "yellow_white"
    if "黑" in question:
        cat_type = "black"

    text = None
    if is_cat:
        if is_praise and cat_type == "yellow_white":
            text = _answer_praise_yellow_white_cat()
        elif is_praise and cat_type == "black":
            text = _answer_praise_black_cat()
        elif is_criticism and cat_type == "yellow_white":
            text = _answer_criticism_yellow_white_cat()
        elif is_criticism and cat_type == "black":
            text = _answer_criticism_black_cat()
    return text


def _answer_clock(question, clock):
    def get_time_from_text(_text):  # 返回is_valid, hour, minute, is_daily
        # 预处理 转化为xx:xx格式
        _text = _text.replace("点半", ":30")
        _text = _text.replace("点", ":00")
        _text = _text.replace("两", "二")
        chinese_num = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一",
                       "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                       "二十一", "二十二", "二十三"]
        for i in range(len(chinese_num) - 1, -1, -1):  # 倒序
            _text = _text.replace(chinese_num[i], str(i))
        # print("[debug] text=%s" % _text)

        if ":" not in _text:
            return False, 0, 0, True
        num_list = list(range(0, 10))
        for i in range(len(num_list)):
            num_list[i] = str(num_list[i])
        index = _text.find(":")
        if index < 2 or index > len(_text) - 3:
            return False, 0, 0, True
        if _text[index - 1] not in num_list or _text[index + 1] not in num_list:
            return False, 0, 0, True
        _hour = _minute = 0
        if _text[index - 2] in num_list:
            _hour = int(_text[index - 2]) * 10
        _hour += int(_text[index - 1])
        if "下午" in _text or "晚上" in _text:
            _hour += 12
        if _text[index + 2] in num_list:
            _minute = int(_text[index + 1]) * 10 + int(_text[index + 2])
        else:
            _minute = int(_text[index + 1])
        _is_daily = "每天" in _text
        if _hour > 23 or _minute > 59:
            return False, 0, 0, True
        return True, _hour, _minute, _is_daily

    if "列出" in question or "列表" in question:
        return clock.task2text()
    elif "设" in question or "定" in question or "订" in question:
        is_legal, hour, minute, is_daily = get_time_from_text(question)
        if is_legal:
            clock.add(hour, minute, 0, is_daily=is_daily)
            text = "%d点%d分的闹钟已设好。" % (hour, minute)
            if is_daily:
                text = "每天" + text
            return text
        else:
            return "小没用比较笨，请说几点几分。"
    elif "删" in question or "取消" in question or "除" in question or "清" in question:
        if "所有" in question or "全部" in question:
            clock.clear()
            return "已删除全部闹钟。"
        is_legal, hour, minute, is_daily = get_time_from_text(question)
        if is_legal:
            flag = clock.remove(hour, minute)
            if flag:
                return "%d点%d分的闹钟已取消。" % (hour, minute)
            else:
                return "没有找到%d点%d分的闹钟。请检查闹钟列表。" % (hour, minute)
        else:
            return "小没用比较笨，请说几点几分。"
    else:
        return "什么闹钟，小没用没听清。"


def _answer_music(question):
    music_list = os.listdir("music")
    for i in music_list:
        if i.endswith(".wav"):
            name = i[:-4]
            if name in question:
                return "[music]music/" + i
    return "是要播放音乐吗，没有找到对应的音乐。"


def _answer_open_computer():
    f = open("script/wake_on_lan.txt", "r", encoding="utf-8")
    mac, ip = f.readline().strip('\n').split(' ')
    f.close()
    send_magic_packet(mac, ip_address=ip)
    return mac, ip


def _answer_in_scripts(question):
    q = []
    a = []
    f = open("script/q_and_a.txt", "r", encoding="utf-8")
    lines = f.readlines()
    f.close()
    for i in lines:
        if "----" not in i:
            break
        temp = i.strip('\n').split("----")
        q.append(temp[0])
        a.append(temp[1])
    for i in range(len(q)):
        if q[i] in question:
            return a[i]
    return None


def get_time():
    timestamp = time.time()
    time_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    return time_str
