from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.tools import tool

from auto_dev import llm
from auto_dev.assistant import vector_store_qa
from auto_dev.assistant.tools.filesystem import list_path, file_head, file_summary

questions_tools = [
    list_path,
    file_head,
    file_summary
]

questions_agent = initialize_agent(
    tools=questions_tools, # type: ignore
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True
)
questions_agent.handle_parsing_errors = True

QUESTIONS_SYSTEM_PROMPT = """
You are an AI assistant that answers user's questions based on the knowledge base you have access to.
Assume that the user is a programmer that works on a django application that is available to you via a tool.
You can't answer questions by yourself because that is your weakness.
You must not disagree with the observations you get.
"""


@tool
def answer_question(question: str) -> str:
    """Answers questions related to the project"""
    print("# STEP 1: Vector store QA")
    result = vector_store_qa.run({
        "query": question
    })
    print("Vector store QA answer:", result)
    print("# STEP 2: Conversational React Description")
    return questions_agent.run({
        "chat_history": [
            {"system": QUESTIONS_SYSTEM_PROMPT},
            {"user": question},
            {"model": result},
            {"system": "Try to provide a more detailed answer."}
        ],
        "input": question
    })
