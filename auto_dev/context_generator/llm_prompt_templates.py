from langchain_core.prompts import PromptTemplate

system_message_prompt = PromptTemplate.from_template('''
You are a python Django developer.
Your task will be to describe some files that are part of a Django project.
''')

describe_python_fragment_prompt = PromptTemplate.from_template('''
You are going to describe a fragment of python code that is part of a Python Django project.
This fragment is defined in file "{path}".
Write a detailed description for the code below:

```python
{code}
```

Respond only with the description.
''')

describe_text_file_prompt = PromptTemplate.from_template('''
You are going to describe a file that is part of a Python Django project.
This file's path is "{path}".
Write a detailed description for the file below:

```
{code}
```

Respond only with the description.
''')


describe_project_prompt = PromptTemplate.from_template('''
Describe the project based on the content of the README file.
Focus on what the project is used for and 
what technologies, libraries, frameworks are used in it.
The README is written in Markdown, its content is:
```markdown
{readme_md}
```
Respond only with a JSON in format:
{{
    "project_name": <name of the project>,
    "project_description": <description of the project>
}}
Do not wrap the output JSON in ```.
''')

generate_py_file_description_prompt = PromptTemplate.from_template(
    '''Generate a very detailed description.
Create docstring with description for every class, method and function in the code.
Create a list of a list of classes and methods used for every class, method and function in the code
Do not change any existing docstring.
Respond with JSON in format {{ "description": "This file is used to <place for description>", "code_with_docstrings": "value" }},
remember to close the JSON object.
Do not use ``` before and after the code.
Do not change the code, only add docstrings.
Do not make up an answer.
Use this python code fragment:
```
{code}
```
'''
)

describe_python_file_prompt = PromptTemplate.from_template('''
Describe me the following python code:
```python
{code}
```
This code is defined in file: {file_path}
Remember to use your knowledge about Django's naming conventions.
Respond only with the generated description and quit.
''')


describe_text_file_prompt_old = PromptTemplate.from_template('''
Describe me the following file:
```
{file_content}
```
Path of this file: {code_frag_path}
Remember to use your knowledge about Django's naming conventions.
Respond only with the generated description and quit.
''')
