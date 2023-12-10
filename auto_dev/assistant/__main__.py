from auto_dev import assistant

while True:
    query = input("Question: ")
    answer = assistant.answer_question(query)
    print(f"Answer: {answer}")
