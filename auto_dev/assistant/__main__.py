from auto_dev.assistant import questions_assistant

while True:
    query = input("Question: ")
    answer = questions_assistant.answer_question(query)
    print(f"Answer: {answer}")
