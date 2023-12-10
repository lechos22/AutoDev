from langchain_core.prompts import PromptTemplate

system_message_prompt_template = PromptTemplate.from_template('''
You are a developer that will process
tasks given you by the user and modify fragments of code.
understand a Django project and implement new features in it.

Here is a description of the project:
{project_description}
''')

split_user_task_prompt_template = PromptTemplate.from_template('''
Split the task below into some smaller tasks.
"{task}"

Respond only with a JSON list that contains objects
in format {{ "task": <a smaller task generated from the main task> }}
If the task given by the user is small
do not split and return it as the only object in the JSON list.
Do not put the output JSON in ```.
''')
