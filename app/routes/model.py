import os
import time

from langchain.tools import BaseTool
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from app.routes.websocket import update_condition_met
from app.routes.search import search_by
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import re

load_dotenv()

api_key = os.getenv('GPT_API_KEY')

if not api_key:
    raise ValueError("API key is missing. Please set GPT_API_KEY in the environment variables.")

llm = ChatOpenAI(
    openai_api_key=api_key,
    temperature=0,
    model_name='gpt-3.5-turbo'
)

# TODO: HandModelTool(BaseTool), HapticGuidanceTool(BaseTool)의 모델 추론 결과 반환하는 부분 통일
# TODO: 모델 설명 스크립트 작성하기

class HandModelTool(BaseTool):
    '''
    손 위치 인식, 원본 이미지와 손가락 위치 비교해야 할 때 사용
    예시: 지금 내가 가르키고 있는 색 무슨 색이야?

    TODO: 이 클래서에서
    hand_model(self, x, y, bboxes)의 input bboxes: 바운딩 박스 리스트, x, y: hand model 좌표

    '''
    name = "Hand Model Tool"
    description = "This is a hand model tool."

    # 특정 점이 바운딩 박스 내부에 있는지 확인하는 함수
    def is_point_in_bbox(self, x, y, bbox):
        x_min, y_min, x_max, y_max = bbox
        return x_min <= x <= x_max and y_min <= y <= y_max

    # 주어진 점이 어떤 바운딩 박스에 있는지 찾는 함수
    def find_bbox_for_point(self, x, y, bboxes):
        for i, bbox in enumerate(bboxes):
            if self.is_point_in_bbox(x, y, bbox):
                return i
        return None

    def hand_model(self, x, y, bboxes):
        '''
        손 위치 인식하고 바운딩 박스와 비교하기
        주어진 (x, y) 좌표가 어떤 바운딩 박스에 속하는지 확인하는 알고리즘
        TODO: 각 바운딩 박스를 for문으로 돌면서 해당하는 위치를 추출 (완)
        '''
        bbox_index = self.find_bbox_for_point(x, y, bboxes)
        return bbox_index

    def _run(self, text: str) -> str:
        return "Hand model tool executed."

    def _arun(self, text: str):
        raise NotImplementedError("This tool does not support async")


class HapticGuidanceTool(BaseTool):
    '''
    HapticGuidanceTool을 실행
    '''
    name = "Haptic Guidance Tool"
    description = "Haptic Guidance Tool"
    
    def _run(self, text: str) -> str:
        update_condition_met(True)
        return "*******************True******************"

    def _arun(self, text: str):
        raise NotImplementedError("This tool does not support async")


class AddHeartTool(BaseTool):
    name = "Add Heart Tool"
    description = "Use this tool to add a heart to a given text"

    def _run(self, text: str) -> str:
        return text + " ❤️"

    def _arun(self, text: str):
        raise NotImplementedError("This tool does not support async")


def generate_response(model_result, query):
    info = search_by(model_result['palette_num'])

    prompt_template = generate_template(info)
    print("Prompt Template:", prompt_template)

    tools = [AddHeartTool(), HapticGuidanceTool()]

    agent = create_react_agent(llm, tools, prompt_template)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        max_iterations=2,
    )

    response = agent_executor.invoke({"input": f"{query}"})
    print(response)

    
    if response["output"] == "Agent stopped due to iteration limit or time limit.":
        intermediate_steps = response["intermediate_steps"]

        text = str(intermediate_steps[0][0])
        pattern = r"log='(.+)'"

        match = re.search(pattern, text)

        if match:
            result = match.group(1)
        else:
            result = "AI Agent에서 추출할 수 있는 답변이 없어요."
        
        return result
    else:
        return response["output"]

def generate_template(info):
    template = f'''You are an assistant who helps explain cosmetics for the blind. When you ask questions about colors or cosmetics, kindly explain them in Korean.

    You have access to the following tools, but you do not have to use them if not necessary:
    {{tools}}

    Detailed description of cosmetics: {info}

    Question: {{input}}
    Thought: {{agent_scratchpad}}
    Action: the action to take, should be one of [{{tool_names}}] or 'None' if no action is needed
    Action Input: the input to the action
    Observation: the result of the action
    Final Answer: the final answer to the original input question
    '''
    
    prompt = PromptTemplate(input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools'], template=template)
    return prompt


client = OpenAI(api_key=api_key)

def stt(audio_path):
    audio_file= open(audio_path, "rb")
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    return transcription.text


def tts(text_path):
    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=text_path
    )
    # 현재 날짜와 시간을 기준으로 파일 이름 생성
    now = datetime.now()
    file_name = now.strftime("text_%Y%m%d_%H%M%S.wav")
    file_path = f"./uploads/{file_name}"
    
    response.stream_to_file(file_path)
    return file_path




# TODO: 이 아래 코드는 숫자만 추출하는 코드, 사용자가 원하는 색을 말했을 때 해당하는 색깔을 찾음(완)

def extract_color_number(text):
    start_index = text.find('Color number: ') + len('Color number: ')
    end_index = text.find('\n', start_index)
    if end_index == -1:
        end_index = len(text)
    return text[start_index:end_index].strip()

def select_cosmatic_num(query, info):

    messages = [
        {
            "role": "system",
            "content": "You are an assistant."
        },
        {
            "role": "user",
            "content": (
                f"Please identify the color names and their corresponding numbers from the palette."
                f"Take your time. First, write down the color name, then write down its corresponding number."
                f"Use the provided info to find the color names and numbers."
                f"If you can't find the number for a color in the provided info, output 0.\n\n"
                f"The user might ask for the color in different ways, such as:"
                f"'Find the last color in the first row', 'I want the last color in the first row', 'The first color in the last row looks delicious'."
                f"Please interpret these queries correctly and provide the corresponding color name and number.\n\n"
                f"info: {info}\n"
                f"question: {query}\n"
                f"answer:\n"
                f"Color name: [name]\n"
                f"Color number: [number]\n"
                f"Ensure that the color number matches the color name from the info."
            )
        }
    ]
    print('prompt: ', messages)

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    color_number = extract_color_number(response_message)
    print(color_number)
    return print(response_message)


# model_result = {'palette_num': "Palette1"}
# generate_response(model_result, "쿠션 글리터로 쓸만한 색은 몇번째에 있어?")


queries = [
    "첫번째 줄에 마지막 색 찾고 싶어",
]

# # 각 query에 대한 테스트
# for query in queries:
#     select_cosmatic_num(query, search_by("Palette1"))
