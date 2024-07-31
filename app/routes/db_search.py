# 모든 데이터를 저장하고, 디비 서치를 하는 파일입니다.
# 사진 이름을 디비에 넣어서 벡터 서치 후 반환
from openai import OpenAI
from dotenv import load_dotenv

import os

load_dotenv()

api_key = os.getenv('GPT_API_KEY')
info_key = os.getenv('INFO_API_KEY')
img_key = os.getenv('IMG_API_KEY')

client = OpenAI(api_key=api_key)

def search_by(index, query, num):

    embedding = client.embeddings.create(
        model ="text-embedding-3-small",
        input = query
    ).data[0].embedding

    query_result=index.query(
    vector=embedding,
    top_k=num,
    include_values=False,
    include_metadata=True
    )

    text_list = []

    for result in query_result.matches:
        id = result.id
        text = result.metadata['text']
        score = result.score
        text_list.append(text)

    text_list = '\n'.join(text_list)
    print('rag 추출: ', text_list)

    return text_list


# def search_by_query(query):

#     index = info_pc.Index("yoo")
#     result = search_by(index, query, 1)
    
#     return result


# def search_by_result(answer):

#     index = img_pc.Index("yoo-img")
#     result = search_by(index, answer, 1)

#     return result