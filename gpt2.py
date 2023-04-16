import uuid

import openai

import settings

openai.api_key = settings.CHAT_GPT_API_KEY


class Snippet:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer
        self.key = uuid.uuid4()

snippets = [
    Snippet(question='Hey dude.', answer='Hey, I\'m Sam! Ask me anything.'),
    Snippet(question='Who are you?', answer='I\'m Sam! Ask me anything.'),
    Snippet(question='What is your GPA?', answer='I graduated with a 3.55 GPA out of 4.0.'),
    Snippet(question='Do you like coffee?', answer='Of course!'),
    Snippet(question='What was your first job?', answer='My first job was working as a dishwasher at a local restaurant in Victoria, BC, called the Surly Mermaid. It was a super formative experience that taught me a lot about working together with a team in a very high-stress environment.'),
    Snippet(question='Where are you?', answer='I currently live in Montreal, Canada.'),
    Snippet(question='What are your hobbies?', answer='I really enjoy board games like Chess and Settlers of Catan (there\'s even a super nerdy one called \'Game of Thrones, the Card Game\'.) But, I also love getting outside to play games like Pickleball, Spikeball, Badminton, Volleyball and Tennis.')
]

question_prompt = '''
The following is a list of possible user questions. After reading the questions, please select which
one is most similar to the given sentence and output the question. Think step by step through each of 
the questions to see which one fits best. If none of the questions seem to fit the sentence, then answer 
by saying: "I DONT KNOW".\n\nList of questions:
'''
for i in range(0, len(snippets)):
    question_prompt += f'Question {i}. {snippets[i].question}\n'
question_prompt += '\nSentence: '

answer_prompt = lambda q, a: f'''
The following is a question posed and an answer. Please paraphrase the answer while being as concise as possible
and in a friendly manner. Please also take into consideration the context of the question while paraphrasing.

Question: {q}
Answer: {a}

Paraphrased Answer:
'''

GPT_KWARGS = {
    'model': 'text-davinci-003',
    'temperature': 0.6,
    'max_tokens': 150,
    'frequency_penalty': 0,
    'presence_penalty': 0.6,
}

class CouldNotQueryGPT(Exception):
    pass

def query_gpt(prompt):
    """
    Get a completion response from Chat-GPT.
    """
    try:
        completion = openai.Completion.create(prompt=prompt, **GPT_KWARGS)
        return str(completion.choices[0]['text'])
    except Exception as e:
        raise CouldNotQueryGPT from e
    
class CouldNotInterpretQuestion(Exception):
    pass
    
def get_user_snippet(user_question):
    q_prompt = question_prompt + user_question
    gpt_interpreted_user_q = query_gpt(q_prompt)
    print(f'Interpreted user question: {gpt_interpreted_user_q}')
    if 'I DONT KNOW' in gpt_interpreted_user_q:
        return Snippet('', answer='I\'m sorry, I didn\'t understand your question.')
    for i in range(0, len(snippets)):
        q_str = f'Question {i}.'
        if q_str in gpt_interpreted_user_q:
            return snippets[i]
    raise CouldNotInterpretQuestion

def get_sambot_answer(snippet):
    return query_gpt(answer_prompt(snippet.question, snippet.answer))
        
def generate_response(user_question):
    snippet = get_user_snippet(user_question)
    answer = get_sambot_answer(snippet)
    return answer

while True:
    print('Human: ', end='')
    user_question = input()
    answer = generate_response(user_question)
    print(answer)

exit(0)
while True:
    print('Human: ', end='')
    user_input = input()
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=question_prompt + f'{user_input}',
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
    )
    response_text = str(response.choices[0]['text'])
    for i in range(0, len(snippets)):
        q_str = f'Question {i}.'
        if q_str in response_text:
            snippet = snippets[i]
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=answer_prompt(snippet.question, snippet.answer),
                temperature=0.9,
                max_tokens=150,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6,
            )
            response_text = str(response.choices[0]['text'])
            print(response_text)
            break
        elif i == len(snippets) - 1:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=answer_prompt('', 'I\'m sorry, I didn\'t quite understand your question.'),
                temperature=0.9,
                max_tokens=150,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6,
            )
            response_text = str(response.choices[0]['text'])
            print(response_text)