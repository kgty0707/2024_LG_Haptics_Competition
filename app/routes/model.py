import os
from dotenv import load_dotenv
from langchain.tools import BaseTool, Tool
from math import pi
from typing import Union
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents.agent_types import AgentType
from langchain.agents import AgentExecutor, create_react_agent
from app.routes.search import search_by

load_dotenv()

api_key = os.getenv('GPT_API_KEY')

def generate_response(model_result, query):
    info = search_by(model_result['palette_num'])
    response = agent({"input": f"{query}"})
    return response["output"]

class HandModelTool(BaseTool):
    name = ""
    description = ""
    ...

class HapticGuidanceTool(BaseTool):
    name = ""
    description = ""
    ...

class AddHeartTool(BaseTool):
    name = "Add Heart Tool"
    description = "Use this tool to add a heart to a given text"

    def _run(self, text: str) -> str:
        return text + " ❤️"

    def _arun(self, text: str):
        raise NotImplementedError("This tool does not support async")

# Initialize LLM
llm = ChatOpenAI(
    openai_api_key=api_key,
    temperature=0,
    model_name='gpt-3.5-turbo'
)

info = "리얼 아이 팔레트는 활용도 높은 데일리 컬러와 영롱한 글리터 조합으로 매일 다채로운 메이크업을 쉽게 완성할 수 있는 제품입니다. 5호 애프리콧 미는 뽀얗게 물드는 살구결 생기를 주는 #살구팔레트로, 스틸(화려한 글리터), 애프리콧 하트(맑은 애프리콧), 기도(여리한 살구 음영), 팔로우(피치 톤 베이스), 영&리치(코랄 글리터), 피넛(코랄 브라운), 리액션(빈티 브라운) 등의 컬러로 구성되어 있어, 눈가를 정돈하고 다양한 메이크업 룩을 완성할 수 있습니다."

template = f'''ou are an assistant who helps explain cosmetics for the blind. When you ask questions about colors or cosmetics, kindly explain them in Korean.:

{{tools}}

The action to take of [{{tool_names}}]
Detailed description of cosmetics: {info}

Question: {{input}}
Thought:{{agent_scratchpad}}'''

prompt = PromptTemplate.from_template(template)

# Initialize agent with tools and custom chain
tools = [AddHeartTool()]

agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=True,
    handle_parsing_errors=True,
    max_iterations=2,
)
# Test the agent with a sample input
# response = agent_executor.invoke({"input": "화장품의 첫번째 섀도우는 무슨 색이야? 텍스트에 하트도 붙여줘"})
