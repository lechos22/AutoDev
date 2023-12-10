import auto_dev
from auto_dev import llm
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.embeddings.azure_openai import AzureOpenAIEmbeddings
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.tools import tool

from auto_dev.assistant.tools.vectorstore import ExtendedVectorStoreQATool
from auto_dev.assistant.tools.filesystem import list_path, file_head, file_summary

embeddings = AzureOpenAIEmbeddings(
    api_key=auto_dev.config["open-ai"]["api-key"],
    api_version=auto_dev.config["open-ai"]["api-version"],
    azure_deployment=auto_dev.config["open-ai"]["embeddings-deployment"],
    azure_endpoint=auto_dev.config["open-ai"]["endpoint"],
)

vector = Neo4jVector(
    embedding=embeddings,
    url=auto_dev.config["neo4j"]["connection"]["url"],
    username=auto_dev.config["neo4j"]["connection"]["username"],
    password=auto_dev.config["neo4j"]["connection"]["password"],
    index_name=auto_dev.config["neo4j"]["vector-store"]["index-name"],
)

vector_store_qa = ExtendedVectorStoreQATool(
    name="code fragments",
    description="code fragments in the application",
    vectorstore=vector,
    llm=llm
)

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
