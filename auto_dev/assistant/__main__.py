from auto_dev.assistant import questions_assistant, tasks_assistant
from langchain.chat_models import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from auto_dev import config, llm
from auto_dev.assistant import llm_prompt_templates
from auto_dev.assistant.graph_db_proxy import GraphDBProxy

graph_db = GraphDBProxy()
project_description = graph_db.receive_description_from_project_node()
system_message = llm_prompt_templates.system_message_prompt_template.format(
    project_description=project_description,
    django_description=graph_db.receive_description_from_django_node()
)


def display_welcome_message():
    print(llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content=llm_prompt_templates.prepare_information_about_the_project_prompt)
    ]).content)


def run(user_input: str):
    response = llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content=llm_prompt_templates.classify_user_input_prompt_template.format(user_input=user_input))
    ]).content
    if response == 'PROJECT_QUESTION':
        print(questions_assistant.answer_question(user_input))
    elif response == 'PROJECT_DEV_TASK':
        pass
        print(tasks_assistant.perform_task(user_input))
    else:
        print(response)


display_welcome_message()

while True:
    run(input('> '))
