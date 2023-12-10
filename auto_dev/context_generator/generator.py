import ast
import json
import pathlib

import tiktoken
from langchain.chat_models import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from auto_dev.common.custom_blob_loaders.improved_file_system_blob_loader import ImprovedFileSystemBlobLoader
from auto_dev.common.vector_store_interface import VectorStoreInterface
from auto_dev.context_generator import document_parsing, llm_prompt_templates
from auto_dev.context_generator.graph_db_proxy import GraphDBProxy
from auto_dev.context_generator.context_types import CodeFragmentData

from auto_dev import config


class ContextGenerator:
    def __init__(self, vector_store: VectorStoreInterface):
        openai_config = config['open-ai']
        self.__repo_path = config['dev-assistant']['project-path']

        self.__vector_store = vector_store
        self.__graph_db = GraphDBProxy()

        self.__chat_model = AzureChatOpenAI(
            api_key=openai_config['api-key'],
            azure_endpoint=openai_config['endpoint'],
            azure_deployment=openai_config['deployment'],
            api_version=openai_config['api-version'],
            temperature=0.0
        )

        self.__tiktoken_encoding = tiktoken.encoding_for_model(self.__chat_model.model_name)
        self.__docs_to_embed = []

    async def generate(self):
        self.__prepare_project_node()
        self.__prepare_apps()
        self.__prepare_project_config_files()

        print(f'embedding {len(self.__docs_to_embed)} documents')

        await self.__vector_store.save_documents_to_index(self.__docs_to_embed)

    def __prepare_project_node(self):
        with open(f'{self.__repo_path}/README.md', encoding='utf-8') as readme_file:
            readme_content = readme_file.read()

        with open(f'django-description.md', encoding='utf-8') as django_desc_file:
            django_desc = django_desc_file.read()

        self.__graph_db.create_django_description_node(django_desc)

        project_info = json.loads(str(self.__invoke_llm_with_sys_msg(
            llm_prompt_templates.describe_project_prompt.format(readme_md=readme_content)
        )))

        self.__graph_db.create_project_node(
            project_info['project_name'],
            project_info['project_description']
        )

    def __prepare_apps(self):
        app_paths = filter(
            lambda path: not path.stem.startswith('__'),
            pathlib.Path(f'{self.__repo_path}/apps/').glob('*')
        )

        for app_path in app_paths:
            app_name = app_path.stem
            app_files = self.__prepare_files(app_path, ['**/[.]*/**/*', '**/__*/**/*'])
            self.__graph_db.create_django_app_node(app_name)
            self.__graph_db.connect_files_to_django_app(app_files, app_name)

    def __prepare_project_config_files(self):
        project_config_files = self.__prepare_files(
            pathlib.Path(self.__repo_path),
            ['**/[.]*/**/*', '**/__*/**/*', 'venv/**/*', 'static/**/*', 'apps/**/*']
        )
        self.__graph_db.connect_files_to_project(project_config_files)

    def __prepare_files(self, path: pathlib.Path, paths_to_ignore: list[str]) -> list[str]:
        files_blobs = ImprovedFileSystemBlobLoader(
            path=path,
            glob='**/*',
            exclude=paths_to_ignore,
            suffixes=['.py', '.md', '.html']
        ).yield_blobs()

        files_info = []
        for blob in files_blobs:
            file_content = blob.as_string()
            file_lines_count = len(file_content.splitlines())
            files_info.append(CodeFragmentData(
                blob.source or "",
                0,
                file_content,
                1,
                file_lines_count
            ))

        text_files_fragments = []
        python_code_fragments = []

        for file_info in files_info:
            self.__graph_db.create_file_node(
                file_info.path,
                file_info.content
            )

            if file_info.path.endswith('.py'):
                module_ast = ast.parse(file_info.content)

                classes = []
                structural_code_ranges = []
                structural_code_range = None

                for ast_element in module_ast.body:
                    if isinstance(ast_element, ast.Import) or isinstance(ast_element, ast.ImportFrom):
                        continue

                    if isinstance(ast_element, ast.ClassDef):
                        if structural_code_range is not None:
                            structural_code_ranges.append(structural_code_range)
                        classes.append(ast_element)
                        structural_code_range = None
                    else:
                        if structural_code_range is None:
                            structural_code_range = [ast_element.lineno, ast_element.lineno]
                        else:
                            structural_code_range[1] = ast_element.end_lineno or -1

                file_lines = file_info.content.splitlines()
                code_fragment_id = 0

                for lines_range in structural_code_ranges:
                    code = '\n'.join(file_lines[lines_range[0] - 1:lines_range[1]])
                    code_fragment_id += 1
                    python_code_fragments.append(
                        CodeFragmentData(file_info.path, code_fragment_id, code, lines_range[0], lines_range[1])
                    )

                for class_declaration in classes:
                    code = '\n'.join(file_lines[class_declaration.lineno - 1:class_declaration.end_lineno])
                    code_fragment_id += 1
                    python_code_fragments.append(
                        CodeFragmentData(
                            file_info.path,
                            code_fragment_id,
                            code,
                            class_declaration.lineno,
                            class_declaration.end_lineno
                        )
                    )
            else:
                text_files_fragments.append(file_info)

        self.__describe_text_files_batch(text_files_fragments)
        for text_file_fragment in text_files_fragments:
            self.__docs_to_embed.append(
                document_parsing.parse_code_fragment_document(
                    text_file_fragment,
                    self.__tiktoken_encoding
                )
            )

        self.__describe_python_code_fragments_batch(python_code_fragments)
        for python_code_fragment in python_code_fragments:
            self.__graph_db.create_python_code_fragment_node(
                python_code_fragment.path,
                python_code_fragment.fragment_id,
                python_code_fragment.content,
                python_code_fragment.description,
                python_code_fragment.line_start,
                python_code_fragment.line_end
            )
            self.__docs_to_embed.append(document_parsing.parse_code_fragment_document(
                python_code_fragment,
                self.__tiktoken_encoding
            ))

        return [file_info.path for file_info in files_info]

    def __describe_python_code_fragments_batch(self, fragments: list[CodeFragmentData]):
        llm_prompts = []

        for fragment in fragments:
            llm_prompts.append(
                llm_prompt_templates.describe_python_fragment_prompt.format(
                    path=fragment.path,
                    code=fragment.content
                )
            )

        raw_responses = self.__batch_llm_with_sys_msg(llm_prompts)

        for i, response in enumerate(raw_responses):
            description = response
            fragments[i].set_description(str(description))

        print(f'described {len(raw_responses)} python fragments')

    def __describe_text_files_batch(self, fragments: list[CodeFragmentData]):
        llm_prompts = []

        for fragment in fragments:
            llm_prompts.append(
                llm_prompt_templates.describe_text_file_prompt.format(
                    path=fragment.path,
                    code=fragment.content
                )
            )

        raw_responses = self.__batch_llm_with_sys_msg(llm_prompts)

        for i, response in enumerate(raw_responses):
            description = response
            fragments[i].set_description(str(description))

        print(f'described {len(raw_responses)} text files')

    def __invoke_llm_with_sys_msg(self, prompt: str):
        return self.__chat_model.invoke([
            SystemMessage(content=llm_prompt_templates.system_message_prompt.format()),
            HumanMessage(content=prompt)
        ]).content

    def __batch_llm_with_sys_msg(self, prompts: list[str]):
        return [response.content
                for response in self.__chat_model.batch([[
                    SystemMessage(content=llm_prompt_templates.system_message_prompt.format()),
                    HumanMessage(content=prompt)
                ] for prompt in prompts])]
