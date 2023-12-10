import asyncio
import sys

from auto_dev.common.vector_store_interface import Neo4jVectorStoreInterface
from auto_dev.context_generator.generator import ContextGenerator


async def build_context():
    vector_store = Neo4jVectorStoreInterface()
    context_generator = ContextGenerator(vector_store)
    await context_generator.generate()


async def main():
    print('Building context for assistant...')
    await build_context()
    print('Done')


if __name__ == '__main__':
    asyncio.run(main())