import json

from langchain.agents import initialize_agent, AgentType

from auto_dev import llm
from auto_dev.assistant.tasks_assistant import llm_prompt_templates
from auto_dev.assistant.questions_assistant import answer_question
from auto_dev.assistant.tools.filesystem import list_path, file_part, file_summary, read_class

tools = [
    answer_question,
    list_path,
    file_part,
    read_class,
    file_summary
]

agent = initialize_agent(
    tools=tools,  # type: ignore
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True
)
agent.handle_parsing_errors = True

SYSTEM_PROMPT = """
You are a developer that will process
tasks given you by the user and modify fragments of code.
understand a Django project and implement new features in it.
"""

SPLIT_TASK_PROMPT = """
Split the task below into some smaller tasks.
"{task}"

Respond only with a JSON list that contains objects
in format {{ "task": <a smaller task generated from the main task> }}
If the task given by the user is small
do not split and return it as the only object in the JSON list.
Respond only with the tasks that require changing some code
Do not put the output JSON in ```.
"""

PERFORM_SUBTASK_PROMPT = """
Complete the task below and give a description of what you do in order to complete it.
The task is: "{task}"
Instruct the user with code required for the task and a path to the file where it should go.
"""


def perform_task(task: str) -> None:
    """Perform tasks related to the project"""
    subtasks_json = agent.run({
        "chat_history": [
            {"system": SYSTEM_PROMPT},
            {"system": SPLIT_TASK_PROMPT.format(task=task)}
        ],
        "input": task
    })
    subtasks = json.loads(subtasks_json)
    responses = []
    for subtask in subtasks:
        response = agent.run({
            "chat_history": [
                {"system": SYSTEM_PROMPT},
                *({"model": response} for response in responses),
                {"system": PERFORM_SUBTASK_PROMPT.format(**subtask)}
            ],
            "input": task
        })
        responses.append(response)

    pretty_response = ''

    for response in responses:
        for response_part in response:
            pretty_response += "#" * 20 + f"\n{response_part}\n" + "#" * 20 + "\n\n"
