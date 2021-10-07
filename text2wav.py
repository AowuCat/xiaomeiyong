import zhtts
import os
from hashlib import md5


def _text_encoding(text):
    return md5(text.encode("utf-8")).hexdigest()


class Text2Wav:
    def __init__(self):
        self._tts = None
        self.wav_path = "cache/"

    def make_wav(self, text):
        if self._tts is None:
            self._tts = zhtts.TTS()
        filename = _text_encoding(text)
        filepath = self.wav_path + filename + ".wav"
        if not os.access(filepath, os.R_OK):
            self._tts.text2wav(text, filepath)
        return filepath

    def get_path(self, text):
        filename = _text_encoding(text)
        filepath = self.wav_path + filename + ".wav"
        return filepath
