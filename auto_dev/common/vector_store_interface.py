import abc

from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.vectorstores.pinecone import Pinecone
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from auto_dev import config


class VectorStoreInterface(abc.ABC):
    def __init__(self):
        openai_config = config['open-ai']
        self._embeddings = AzureOpenAIEmbeddings(
            api_key=openai_config['api-key'],
            azure_endpoint=openai_config['endpoint'],
            azure_deployment=openai_config['embeddings-deployment'],
            api_version=openai_config['api-version']
        )

    @abc.abstractmethod
    async def save_documents_to_index(self, documents: list[Document]):
        pass

    @abc.abstractmethod
    def get_vector_store(self) -> VectorStore:
        pass


class Neo4jVectorStoreInterface(VectorStoreInterface):
    def __init__(self):
        super().__init__()
        neo4j_config = config['neo4j']
        self.__index_name = neo4j_config['vector-store']['index-name']
        self.__neo4j_conn_settings = neo4j_config['connection']

    async def save_documents_to_index(self, documents: list[Document]):
        return await Neo4jVector.afrom_documents(
            documents,
            self._embeddings,
            index_name=self.__index_name,
            **self.__neo4j_conn_settings
        )

    def get_vector_store(self) -> VectorStore:
        return Neo4jVector.from_existing_index(
            self._embeddings,
            self.__index_name,
            **self.__neo4j_conn_settings
        )
