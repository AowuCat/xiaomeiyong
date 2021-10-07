import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models
import base64

from asrt.main import ASRT

_asrt_static = None
wakeup_word = "小没用"
sleep_word = "小没用爬"


def wav2text(filepath):
    return _tencent(filepath)


def is_keyword(filepath):
    pinyin = _asrt(filepath)
    # print(pinyin)
    if _sleep_word_recognize(pinyin):
        return sleep_word
    if _wakeup_word_recognize(pinyin):
        return wakeup_word
    return None


def _sleep_word_recognize(pinyin):
    # 识别“小没用爬”
    if len(pinyin) < 3:
        return False
    flag = False
    if 'm' in pinyin[0]:
        flag = _wakeup_word_recognize(pinyin[0:2])
    else:
        flag = _wakeup_word_recognize(pinyin[0:3])
    # print("sleep_word: " + str(flag))
    if flag:
        key_list = ["pa", "ha", "hua", "wa"]
        for i in key_list:
            if i in pinyin[-1] or i in pinyin[-2]:
                return True
    return False


def _wakeup_word_recognize(pinyin):
    # 识别“小没用”
    score = 0
    if len(pinyin) <= 1:
        return False
    elif 'm' in pinyin[0] and len(pinyin) <= 3:
        if 'me' in pinyin[0] or 'ei' in pinyin[1]:
            score += 30
        if 'yo' in pinyin[1] or 'ya' in pinyin[1]:
            score += 30
    elif 3 <= len(pinyin) <= 4:
        if 'xia' in pinyin[0]:
            score += 40
        elif 'jia' in pinyin[0] or 'ao' in pinyin[0] or 'ang' in pinyin[0]:
            score += 30
        else:
            score -= 10
        if 'me' in pinyin[1] or 'ei' in pinyin[1]:
            score += 30
        if 'yo' in pinyin[2] or 'ya' in pinyin[2]:
            score += 30
    return score >= 60


def _tencent(filepath):
    # 优先使用腾讯语音识别，每月免费5000次，足够了。
    try:
        secret_id = 
        secret_key = 
        cred = credential.Credential(secret_id, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "asr.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = asr_client.AsrClient(cred, "", clientProfile)

        req = models.SentenceRecognitionRequest()
        # 读取文件以及base64
        f = open(filepath, 'rb').read()
        dataLen = len(f)
        base64Wav = base64.b64encode(f).decode('utf8')
        params = {
                  "ProjectId": 0,
                  "SubServiceType": 2,
                  "EngSerViceType": "16k_zh",
                  "SourceType": 1,
                  "VoiceFormat": "wav",
                  "UsrAudioKey": "test",
                  "Data": base64Wav,
                  "DataLen": dataLen
                  }
        req.from_json_string(json.dumps(params))
        resp = client.SentenceRecognition(req)
        return resp.Result
    except TencentCloudSDKException as err:
        print(err)
        return None


def _asrt(filepath):
    # 开源、离线的语音识别，用作关键词识别
    global _asrt_static
    if _asrt_static is None:
        _asrt_static = ASRT()
    return _asrt_static.run(filepath)
