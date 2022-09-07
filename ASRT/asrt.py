import os

from ASRT.speech_model import ModelSpeech
from ASRT.speech_model_zoo import SpeechModel251
from ASRT.speech_features import Spectrogram
from ASRT.LanguageModel2 import ModelLanguage


class SttLocal:
    def __init__(self):
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        audio_length = 1600
        audio_feature_length = 200
        channels = 1
        # 默认输出的拼音的表示大小是1428，即1427个拼音+1个空白块
        output_size = 1428
        sm251 = SpeechModel251(
            input_shape=(audio_length, audio_feature_length, channels),
            output_size=output_size
        )
        feat = Spectrogram()
        self.ms = ModelSpeech(sm251, feat, max_label_length=64)
        self.ms.load_model('ASRT/save_models/' + sm251.get_model_name() + '.model.h5')
        self.ml = ModelLanguage('ASRT/model_language')
        self.ml.LoadModel()

    def run(self, filepath, need_pinyin=False, debug=False):
        pinyin = self.ms.recognize_speech_from_file(filepath)
        if need_pinyin:
            if debug:
                print('[debug]]stt_local_pinyin：', pinyin)
            return pinyin
        else:
            text = self.ml.SpeechToText(pinyin)
            if debug:
                print('[debug]stt_local_text', text)
            return text

    def is_keyword(self, filepath, debug=False):
        pinyin = self.ms.recognize_speech_from_file(filepath)
        if debug:
            print(pinyin)
        # 识别“小没用”
        pinyin_len = len(pinyin)
        if pinyin_len < 2:
            return False
        for i in range(min(pinyin_len - 1, 2)):
            if "me" in pinyin[i] and ("2" in pinyin[i] or "3" in pinyin[i]):
                if "yo" in pinyin[i + 1] or "yao" in pinyin[i + 1]:
                    return True
        return False
