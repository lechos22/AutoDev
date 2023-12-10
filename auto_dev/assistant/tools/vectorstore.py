from typing import Optional
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools.vectorstore.tool import BaseVectorStoreTool
from langchain.tools import BaseTool

class ExtendedVectorStoreQATool(BaseVectorStoreTool, BaseTool):
    """Tool for the VectorDBQA chain. To be initialized with name and chain."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_description(name: str, description: str) -> str:
        template: str = (
            "Useful for when you need to answer questions about {name}. "
            "Whenever you need information about {description} "
            "you should ALWAYS use this. "
            "Input should be a fully formed question."
        )
        return template.format(name=name, description=description)
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        from langchain.chains.retrieval_qa.base import RetrievalQA

        chain = RetrievalQA.from_chain_type(
            self.llm,
            retriever=self.vectorstore.as_retriever(k=32),
            verbose=True
        )
        return chain.run(
            query, callbacks=run_manager.get_child() if run_manager else None
        )