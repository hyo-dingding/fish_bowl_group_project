from pydub import AudioSegment
from pydub.utils import which
import os

AudioSegment.converter =which('ffmpeg')
AudioSegment.ffprobe = which('ffprobe')

output_folder = 'fish_bowl_group_project\\media\\uploads'

def process_mp3(audio_segment):
    # MP3 파일 처리 로직
    wav_path = os.path.join(output_folder, os.path.splitext(audio_segment)[0] + ".wav")
    audio_segment.export(wav_path, format="wav")
    return wav_path