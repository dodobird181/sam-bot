from chat_gpt_request import ChatGPTRequest
from chat_history import ChatHistory
from user_question_mapper import QuestionMapper

print('Starting program...')

questions = {
    'Hey there how is it going?', 
    'What is your GPA?', 
    'Where did you go to high-school?', 
    'What is your favorite color?',
    'What was your first job?',
    'What are your hobbies?',
    'Who are you?',
    'What are you?',
    'Where are you?',
    'How are you?',
    'Do you like coffee?',
    }

initial_prompt = '''The following is a conversation between Samuel Morris and an unidentified user. Samuel
is polite, helpful, likes to answer questions about himself, and very friendly.'''

history = ChatHistory(initial_prompt)

while True:
    print('User: ', end='')
    user_input = input()
    if user_input == '/h':
        print(history.peek_history_with_initial(5))
        continue
    history.user_speaks(user_input)
    ai_response = ChatGPTRequest(history.peek_history_with_initial(5)).send()
    history.ai_speaks(ai_response)
    print('AI: ', end='')
    print(history.last_ai_sentence())
