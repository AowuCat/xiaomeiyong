import datetime
import time
from recorder import Recorder, get_noise_intensity
import wav2text
import os
import sys
from text2wav import Text2Wav
from xiaomeiyong import Xiaomeiyong


def get_time():
    timestamp = time.time()
    time_str = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    return time_str


if __name__ == "__main__":
    os.close(sys.stderr.fileno())
    welcome_text = "你好，我叫小没用。"
    wav2text.is_keyword("music/init.wav")
    text2wav = Text2Wav()
    text2wav.make_wav(welcome_text)
    recorder = Recorder()
    recorder.run()
    ave_noise, max_noise = get_noise_intensity()
    xiaomeiyong = Xiaomeiyong(recorder, text2wav, log=True)
    xiaomeiyong.play_sound_safety(text2wav.make_wav(welcome_text))
    print("[info] %s 初始化完成，你好，我叫小没用！" % get_time())
    print("[info] 平均噪音：%d 最大噪音：%d" % (ave_noise, max_noise))
    if max_noise > 2000:
        text = "环境噪音较大，语音识别困难，请检查录音设备。"
        print("[warn] " + text)
        xiaomeiyong.play_sound_safety(text2wav.make_wav(text))

    online_recognize_life = 60
    online_recognize_timestamp = 0
    while True:
            # 小没用有需要在主循环中更新的任务，例如闹钟
            xiaomeiyong.check()

            # 检查是否有新录音
            if recorder.is_new_msg():
                keyword_answer = wav2text.is_keyword(recorder.filepath)
                if keyword_answer == wav2text.wakeup_word:
                    xiaomeiyong.wake()
                    online_recognize_timestamp = time.time()
                elif keyword_answer == wav2text.sleep_word:
                    xiaomeiyong.sleep(is_active=True)
                else:  # 未匹配到关键词，则检查联网状态，若允许联网则联网识别
                    if xiaomeiyong.is_wake():
                        question = wav2text.wav2text(recorder.filepath)
                        if xiaomeiyong.answer(question):
                            online_recognize_timestamp = time.time()

            # 超过online_recognize_live未使用，则关闭联网识别
            if xiaomeiyong.is_wake() and time.time() - online_recognize_timestamp > online_recognize_life:
                xiaomeiyong.sleep(is_active=False)
        
            time.sleep(0.1)
