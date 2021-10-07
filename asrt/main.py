from asrt.SpeechModel251 import ModelSpeech
from asrt.LanguageModel2 import ModelLanguage
from keras import backend as K
import os


class ASRT:
    def __init__(self):
        if os.name == "nt":
            slash = "\\"
        else:
            slash = '/'
        self.ms = ModelSpeech("asrt" + slash)
        self.ms.LoadModel('asrt' + slash + 'model_speech' + slash + 'speech_model251_e_0_step_625000.model')
        self.ml = ModelLanguage('asrt' + slash + 'model_language')
        self.ml.LoadModel()

    def run(self, filepath):
        str_pinyin = self.ms.RecognizeSpeech_FromFile(filepath)
        pinyin = []
        for i in str_pinyin:
            if i != '_':
                pinyin.append(i)
        K.clear_session()
        # text = self.ml.SpeechToText(pinyin)
        return pinyin
