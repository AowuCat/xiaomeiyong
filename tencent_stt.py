import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models
import base64
import os


class TencentStt:
    def __init__(self):
        self.secret_id = ''
        self.secret_key = ''

    def is_available(self):
        exitcode = os.system("ping asr.tencentcloudapi.com -n 1 > nul")
        if exitcode == 0:
            return True
        else:
            return False

    def run(self, filepath):
        try:
            cred = credential.Credential(self.secret_id, self.secret_key)
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
        except TencentCloudSDKException as e:
            print(e)
            return None
        except Exception as e:
            print(e)
            return None
