import os
import time
from dotenv import load_dotenv
from langchain.tools import BaseTool
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from app.routes.search import search_by

load_dotenv()

api_key = os.getenv('GPT_API_KEY')

if not api_key:
    raise ValueError("API key is missing. Please set GPT_API_KEY in the environment variables.")

llm = ChatOpenAI(
    openai_api_key=api_key,
    temperature=0,
    model_name='gpt-3.5-turbo'
)

class HandModelTool(BaseTool):
    '''
    손 위치 인식, 원본 이미지와 손 가락 위치 비교 해야 할 때 사용
    example: 지금 내가 가르키고 있는 색 무슨 색이야?
    '''
    name = "Hand Model Tool"
    description = "This is a hand model tool."

    def hand_model():
        '''
        손 위치 인식하고 섀도우 바운딩 박스랑 비교하기
        섀도우 바운딩 박스에 몇번째랑 닿아 있는지 구하는 알고리즘.
        -> 생각상 바운딩 박스 for문으로 돌면서 해당하는 위치 추출하는 방식으로 해야할 듯
        '''
        ...

    def _run(self, text: str) -> str:
        return "Hand model tool executed."

    def _arun(self, text: str):
        raise NotImplementedError("This tool does not support async")

class HapticGuidanceTool(BaseTool):
    '''
    HapticGuidanceTool을 선택하면 현재 120초간 멈춤
    '''
    name = "Haptic Guidance Tool"
    description = "Haptic Guidance Tool"

    def haptic_guidance():
        '''
        손 위치 모델, 섀도우 위치 예측 모델 프레임 마다 비교 실행.
        알고리즘 구현은 def hand_model과 비슷할 듯.

        추가적으로 위치에 따라 firebase에 진동 전송하는 로직 필요함.
        '''
        ...

    def _run(self, text: str) -> str:
        time.sleep(120)
        return "120초간의 대기가 완료되었습니다."

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
        max_iterations=1,
    )

    response = agent_executor.invoke({"input": f"{query}"})
    print(response)
    return response["output"]

def generate_template(info):
    template = f'''You are an assistant who helps explain cosmetics for the blind. When you ask questions about colors or cosmetics, kindly explain them in Korean.

    You have access to the following tools:
    {{tools}}

    Detailed description of cosmetics: {info}

    Question: {{input}}
    Thought: {{agent_scratchpad}}
    Action: the action to take, should be one of [{{tool_names}}]
    Action Input: the input to the action
    Observation: the result of the action
    Final Answer: the final answer to the original input question
    '''
    
    prompt = PromptTemplate(input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools'], template=template)
    return prompt

# model_result = {'palette_num': "Palette1"}
# generate_response(model_result, "햅틱 가이던스 실행시켜줘")
