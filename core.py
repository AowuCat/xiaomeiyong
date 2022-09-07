import time
import datetime
import random
import alarm_clock


class Core:
    def __init__(self):
        self.history = []
        self.alarm_clock = alarm_clock.AlarmClock()

    def run(self, text):
        ans = ""
        if "几号" in text or "哪天" in text:
            ans = "text&" + _answer_what_day()
        elif "几点" in text or "时间" in text:
            ans = "text&" + _answer_what_time()
            # 夸/骂 黄白猫/黑猫
        elif _praise_or_criticism(text) is not None:
            ans = "text&" + _praise_or_criticism(text)
        elif "开电脑" in text or "开机" in text:
            _answer_wakeonlan()
            ans = "text&已发送唤醒包。"
        elif "闹钟" in text:
            ans = "text&" + _answer_clock(text, self.alarm_clock)

        if "没用" in text[:min(4, len(text))]:
            ans = "text&喵|" + ans
        if ans.endswith("|"):
            ans = ans[:-1]

        self.history.append((time.time(), text, ans))
        return ans

    def update(self):
        if self.alarm_clock.update():
            return "clear|wav&" + self.alarm_clock.default_wav_filepath
        return None


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
    text = "现在是%d点%d分。" % (d.hour, d.minute)
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
        if i in question:
            is_praise = True
            break
    for i in criticism_words:
        if i in question:
            is_criticism = True
            break
    for i in cat_words:
        if i in question:
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


def _answer_wakeonlan():
    from wakeonlan import send_magic_packet
    mac = "aa-bb-cc-dd-ee-ff"
    ip = "192.168.100.255"
    send_magic_packet(mac, ip_address=ip)


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
