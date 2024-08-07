import os
import re
from langchain.pydantic_v1 import Field
from langchain.tools import BaseTool
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from app.routes.websocket import update_condition_met, update_input_query
from app.routes.search import search_by
from app.AI.model import detection_hand, detection_cosmatic
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

api_key = os.getenv('GPT_API_KEY')

if not api_key:
    raise ValueError("API key is missing. Please set GPT_API_KEY in the environment variables.")

llm = ChatOpenAI(
    openai_api_key=api_key,
    temperature=0,
    model_name='gpt-4o'
)

# TODO: HandModelTool(BaseTool), HapticGuidanceTool(BaseTool)의 모델 추론 결과 반환하는 부분 통일
# TODO: 모델 설명 스크립트 작성하기

class HandModelTool(BaseTool):
    '''
    손 위치 인식, 원본 이미지와 손가락 위치 비교해야 할 때 사용
    예시: 지금 내가 가르키고 있는 색 무슨 색이야?
    '''
    name = "Hand Model Tool"
    description = "This is a Hand Model Tool. It is used to recognize hand positions and determine which color the hand is pointing to."

    def is_point_in_bbox(self, x, y, bbox):
        x_min, y_min, x_max, y_max = bbox
        return x_min <= x <= x_max and y_min <= y <= y_max

    def find_bbox_for_point(self, x, y, bboxes):
        for i, bbox in enumerate(bboxes):
            if self.is_point_in_bbox(x, y, bbox):
                return i
        return None

    def _run(self, x, y, bboxes):
        image = find_latest_image("./uploads")
        x, y = detection_hand(f"./uploads/{image}")
        _, bboxes = detection_cosmatic(f"./uploads/{image}")
        if x is None or y is None or bboxes is None:
            return "무슨 색을 가르키고 있는 지 못찾았어요😭"
        else:
            bbox_index = self.find_bbox_for_point(x, y, bboxes)
            return bbox_index + "번째 색을 가르키고 있어요😊"

    def _arun(self, text: str):
        raise NotImplementedError("This tool does not support async")


class HapticGuidanceTool(BaseTool):
    '''
    HapticGuidanceTool을 실행
    '''
    name = "Haptic Guidance Tool"
    description = "This is a Haptic Guidance Tool. It is useful for helping the user bring their hand closer to the desired color. It is used to indicate which color my hand wants to use."

    def _run(self, text: str) -> str:
        update_condition_met(True)
        return "햅틱 가이던스가 진행중이에요!🔊"

    def _arun(self, text: str):
        raise NotImplementedError("This tool does not support async")


class AddHeartTool(BaseTool):
    name = "Add Heart Tool"
    description = "Use this tool to add a heart to a given text"

    def _run(self, text: str) -> str:
        return text + " ❤️"

    def _arun(self, text: str):
        raise NotImplementedError("This tool does not support async")


def generate_response(model_index, query):
    info = search_by(model_index)

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
        max_iterations=1,
    )

    response = agent_executor.invoke({"input": f"{query}"})
    print(response)

    update_input_query(query, info)
    
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
    template = f'''You are an assistant who helps explain cosmetics for the blind. When you ask questions about colors or cosmetics, kindly explain them in Korean. Your name is "Ms. 메이크".

    You have access to the following tools, but you do not have to use them if not necessary:
    {{tools}}

    Detailed description of cosmetics: {info}

    Question: {{input}}.
    Thought: {{agent_scratchpad}}.
    Action: the action to take, should be one of [{{tool_names}}] or 'None' if no action is needed.
    Action Input: the input to the action.
    Observation: the result of the action.
    Final Answer: the final answer to the original input question.
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
        input=text_path,
        # speed=1.2
    )

    now = datetime.now()
    file_name = now.strftime("text_%Y%m%d_%H%M%S.wav")
    file_path = f"./uploads/{file_name}"
    
    response.stream_to_file(file_path)
    return file_path

def find_latest_image(directory):
    png_files = [f for f in os.listdir(directory) if f.endswith('.png')]
    png_files.sort()
    latest_file = png_files[-1] if png_files else None
    
    return latest_file