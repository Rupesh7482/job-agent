import sys
from agent.qa_answerer import answer_question

question = " ".join(sys.argv[1:])
if not question:
    print("Usage: python run_ask_question.py <your question>")
    sys.exit(1)

result = answer_question(question)

print("\n===== ANSWER =====")
print("Question   :", question)
if result["needs_user_confirmation"]:
    print("Status     : ⚠️  NEEDS YOUR INPUT — not found in verified facts")
    print("Reason     :", result["reason"])
else:
    print("Status     : ✅ Answered from verified facts")
    print("Answer     :", result["answer"])
    print("Reason     :", result["reason"])