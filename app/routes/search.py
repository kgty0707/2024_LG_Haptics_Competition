# 모든 데이터를 저장하고, 디비 서치를 하는 파일입니다.
# 사진 이름을 디비에 넣어서 벡터 서치 후 반환
from openai import OpenAI
from dotenv import load_dotenv

import os

load_dotenv()

api_key = os.getenv('GPT_API_KEY')

client = OpenAI(api_key=api_key)

def search_by(Palette_num):
    file_path = f"./{Palette_num}.txt"

    with open(file_path, 'r', encoding='utf-8') as file:
        info = file.read()

    return info