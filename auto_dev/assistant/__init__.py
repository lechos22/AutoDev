import auto_dev
from auto_dev import llm
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.embeddings.azure_openai import AzureOpenAIEmbeddings

from auto_dev.assistant.tools.vectorstore import ExtendedVectorStoreQATool

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
