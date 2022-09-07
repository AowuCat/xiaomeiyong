import zhtts
import os
from hashlib import md5


def _text_encode(text):
    return md5(text.encode("utf-8")).hexdigest()


class TTS:
    def __init__(self):
        self._tts = zhtts.TTS()
        self.wav_path = "cache/"
        # 先运行一次以初始化，减少后续等待时间。手动运行，不要用缓存。text可任意修改。
        text = "初始化完成"
        self.run(text, use_cache=False)

    def run(self, text, use_cache=True):
        if text is None or len(text) == 0:
            return None
        filepath = self.wav_path + _text_encode(text) + ".wav"
        if not os.access(filepath, os.R_OK) or not use_cache:
            self._tts.text2wav(text, self.wav_path + "_tts_cache.wav")
            sox_path = r".\sox\sox.exe"
            cmd = "-b 16 -r 16000 -c 1 -e signed-integer"
            os.system("%s %s %s %s" % (sox_path, self.wav_path + "_tts_cache.wav", cmd, filepath))
        return filepath
