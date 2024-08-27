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
import azure.cognitiveservices.speech as speechsdk
# from dotenv import load_dotenv
import environ
import json
# load_dotenv()  # .env 파일에서 환경 변수 로드



def azure_stt_from_audio_file(audio_file_path):
    # Define the API endpoint, subscription key, and region  
    api_endpoint = "https://eastus.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe?api-version=2024-05-15-preview"  
    subscription_key = "125cc0bfdd294e478f2d73641d52281e"  
    #audio_file_path = "YourAudioFile"  
    # Headers for the request  
    headers = {  
        "Accept": "application/json",  
        "Ocp-Apim-Subscription-Key": subscription_key  
    }  
    # Form data for the request  
    form_data = {  
        "audio": ("audio.wav", open(audio_file_path, "rb"), "audio/wav"),  
        "definition": (None, json.dumps({  
            "locales": ["ko-KR"],  
            "profanityFilterMode": "Masked",  
            "channels": [0, 1]  
        }), "application/json")  
    }  
    # Make the POST request  
    response = requests.post(api_endpoint, headers=headers, files=form_data)  
    # Check response status and parse JSON  
    if response.status_code == 200:  
        transcription_result = response.json()  
        print(json.dumps(transcription_result, indent=4))  
        temp = response.json()
        text = temp['combinedPhrases'][0]['text']
        return text
    else:  
        print(f"Error: {response.status_code}, {response.text}")
        return None  
    
    '''
    speech_config = speechsdk.SpeechConfig(subscription='fc46077d8bd240d9a1a0597020a2f8d4', region='eastus')
    speech_config.endpoint_id = "https://eastus.api.cognitive.microsoft.com/"
    speech_config.speech_recognition_language="ko-KR"

    audio_config = speechsdk.AudioConfig(filename=audio_file_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
        return speech_recognition_result.text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    '''
