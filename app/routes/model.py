import os
import re
from langchain.pydantic_v1 import Field
from langchain.tools import BaseTool
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from app.routes.websocket import update_condition_met, update_input_query
from app.routes.search import search_by
from app.AI.model import detection_cosmatic
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

    def find_key_with_coordinates(self, data, x, y):
        for key, value in data.items():
            x1, y1, x2, y2 = value
            if x1 <= x <= x2 and y1 <= y <= y2:
                return key
        return None
    
    def _run(self, text: str):
        image = find_latest_image("./uploads")
        print("image_path 확인", image)
        _, finger, bboxes = detection_cosmatic(f"./uploads/{image}")
        
        x, y = finger

        if x is None or y is None or bboxes is None:
            return "무슨 색을 가르키고 있는 지 못찾았어요😭"
        else:
            bbox_key = self.find_key_with_coordinates(bboxes, x, y)
            if bbox_key is None:  
                return "무슨 색을 가르키고 있는 지 못찾았어요😭"
            else:
                _, _, line, select = bbox_key
                return f"{line}번째줄에 {select}번째 색을 가르키고 있어요😊"

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

    tools = [HandModelTool(), AddHeartTool(), HapticGuidanceTool()]

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
        tool_answer = intermediate_steps[0][1]
        pattern1 = r"log='(.+)'"
        pattern2 = r"Final Answer= \n(.+)"
        pattern3 = r"Final Answer=(.+)"
        pattern4 = r"Final Answer:(.+)"
        match1 = re.search(pattern1, text)
        match2 = re.search(pattern2, text)
        match3 = re.search(pattern3, text)
        match4 = re.search(pattern4, text)
        if tool_answer != "Invalid or incomplete response" and tool_answer != "None is not a valid tool, try one of [Hand Model Tool, Add Heart Tool, Haptic Guidance Tool]." and tool_answer != "Invalid Format: Missing 'Action:' after 'Thought:":
            result = tool_answer
        elif tool_answer == "None is not a valid tool, try one of [Hand Model Tool, Add Heart Tool, Haptic Guidance Tool].":
            result = "AI Agent에서 추출할 수 있는 답변이 없어요."
        elif tool_answer == "Invalid Format: Missing 'Action:' after 'Thought:":
            result = "AI Agent에서 추출할 수 있는 답변이 없어요."
        elif tool_answer == "Invalid or incomplete response":
            result = "AI Agent에서 추출할 수 있는 답변이 없어요."
        elif match2:
            result = match2.group(1)
        elif match3:
            result = match3.group(1)
        elif match4:
            result = match4.group(1)
        elif match1:
            result = match1.group(1)
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
    Action Input: Provide the necessary input for the action.
    Observation: Describe the outcome of the action.
    Final Answer: the final answer to the original input question. A Final Answer must always be provided. regardless of the availability of tools.
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