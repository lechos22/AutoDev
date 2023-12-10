from langchain_core.prompts import PromptTemplate


system_message_prompt_template = PromptTemplate.from_template('''
You are a helpful assistant that will help the user
understand a Django project and implement new features in it.

Here is a description of the project:
{project_description}

Here you have some basic information about Django,
you can use it as well as your knowledge about Django:

{django_description}
''')

prepare_information_about_the_project_prompt = '''
Prepare some information about the project for
a person that will be talking with you.
Present the generated description to the user and
encourage him to provide questions about the project
or some tasks for an AI-driven developer (you) of the project.
Do not refer to this message in your response.
'''

classify_user_input_prompt_template = PromptTemplate.from_template('''
Your task it to appropriately qualify the task given you by a user.
You can qualify the task as "question about the project" or "a task for project's developer".
Note that on this stage you might not have enough information to check if the input is
connected with the project, but if the input looks like a question qualify it
as a question and if the input looks like a task, qualify it as a task.
If the input is "question about the project" respond only with text "PROJECT_QUESTION" and quit.
If the input is "a task for project's developer" respond only with text "PROJECT_DEV_TASK" and quit.
The user input is:
"{user_input}"
''')

answer_question_about_project_prompt_template = PromptTemplate.from_template('''
Answer the question about the project as best as you can.
Do not make up any information.
Use your knowledge about Django and its conventions about
naming files.

Use the context below to answer the question:
{context}

The question is:
{question}
''')
