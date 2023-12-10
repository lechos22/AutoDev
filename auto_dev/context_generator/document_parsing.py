import json

import tiktoken
from langchain_core.documents import Document

from auto_dev.context_generator.types import CodeFragmentData


def parse_code_fragment_document(fragment: CodeFragmentData, tiktoken_encoding: tiktoken.Encoding
):
    page_content = json.dumps({
        'file_path': fragment.path,
        'content': fragment.content,
        'description': fragment.description
    })
    document = Document(
        page_content=page_content,
        metadata={
            'doc_type': 'code-fragment',
            'source': fragment.path,
            'fragment_id': fragment.fragment_id,
            'start_line': fragment.line_start,
            'end_line': fragment.line_end,
            'tokens_count': len(tiktoken_encoding.encode(page_content))
        }
    )

    with open('docs-log.txt', 'a') as logfile:
        logfile.write(json.dumps(document.to_json()))
        logfile.write(',\n')

    return document
