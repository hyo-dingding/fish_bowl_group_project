# llm/scripts/stt.py

# import requests
# import os
# import re

# def azure_stt_from_audio_file(audio_file_path):
#     subscription_key = os.getenv("AZURE_SPEECH_KEY")
#     endpoint = "https://eastus.api.cognitive.microsoft.com/speechtotext/v3.1/transcriptions"
#     headers = {
#         'Ocp-Apim-Subscription-Key': subscription_key
#     }
    
#     # API 호출로 STT 시작
#     files = {'file': open(audio_file_path, 'rb')}
#     response = requests.post(endpoint, headers=headers, files=files)
    
#     if response.status_code != 200:
#         raise Exception("STT API 호출에 실패했습니다.")
    
#     transcription = response.json()
#     result_text = transcription.get("DisplayText", "")
    
#     return result_text

# llm/scripts/stt.py

import os
import time
import requests
from azure.cognitiveservices.speech import SpeechConfig, SpeechRecognizer, AudioConfig
from azure.cognitiveservices.speech import ResultReason
# from dotenv import load_dotenv
import environ

# load_dotenv()  # .env 파일에서 환경 변수 로드



def azure_stt_from_audio_file(audio_file_path):
    speech_key = "fc46077d8bd240d9a1a0597020a2f8d4"
    service_region = "eastus" #  os.getenv("AZURE_SERVICE_REGION")
    
    
    if not speech_key or not service_region:
        raise Exception("AZURE_SPEECH_KEY 또는 AZURE_SERVICE_REGION 환경 변수가 설정되지 않았습니다.")
    
    speech_config = SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = AudioConfig(filename=audio_file_path)
    
    recognizer = SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    print("오디오 파일에서 음성을 인식 중입니다...")
    result = recognizer.recognize_once()
    
    if result.reason == ResultReason.RecognizedSpeech:
        print("인식된 텍스트:", result.text)
        return result.text
    elif result.reason == ResultReason.NoMatch:
        print("음성을 인식하지 못했습니다.")
        return ""
    elif result.reason == ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"음성 인식이 취소되었습니다. 이유: {cancellation_details.reason}")
        return ""
