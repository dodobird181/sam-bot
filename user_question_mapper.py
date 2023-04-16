import json
from dataclasses import dataclass
from typing import Dict, Iterable
from uuid import UUID, uuid4

from chat_gpt_request import ChatGPTRequest


@dataclass
class Question:
    id: UUID
    question: str
    answer: str


class QuestionFactory:
    @staticmethod
    def create(q, a) -> Question:
        return Question(question=q, answer=a, id=uuid4())
    

class QuestionBucket:

    def __init__(self):
        self._qs = {}
    
    def __str__(self):
        b = ''
        for id in self._qs.keys():
            q: Question = self.get(id)
            b += str(q.id) + ': ' + q.question + '\n'
        return b
    
    def add(self, q, a):
        q = QuestionFactory.create(q, a)
        self._qs[q.id] = q
    
    def get(self, id):
        return self._qs.get(id)


class QuestionMapper:
    """
    Maps user questions to predetermined answers using ChatGPT.
    """
    UNKNOWN_QUESTION = QuestionFactory.create(None, None)

    def __init__(self):
        self.bucket = QuestionBucket()

    def _get_prompt(self, sentence) -> str:
        p = 'Rate the following questions from 0 to 100 in their similarity to the given sentence.'
        p += 'And give a score about your overall confidence in these ratings.\n'
        p += f'[QUESTIONS]\n{str(self.bucket)}[QUESTIONS]\n'
        p += f'[SENTENCE]\n{sentence}\n[SENTENCE]\n'
        p += f'[RATINGS]\n{self.UNKNOWN_QUESTION.question}: 0\n{sentence}: 100\n...'
        return p
    
    def _get_ratings_from_gpt_response(self, response) -> Dict[UUID, int]:
        rating_lines = response.split('\n')
        print(rating_lines)
        for line in rating_lines:
            print(f'LINE: {line}')
            splitted = line.split(':')
            if len(splitted) == 2:
                id = str(splitted[0]).strip()
                rating = int(str(splitted[1]).strip())
                print(f'id: {id}, question: {self.bucket.get(id)}, rating: {rating}')

    def map(self, sentence, must_rate_above=70) -> UUID:
        response = ChatGPTRequest(self._get_prompt(sentence)).send()
        print(self._get_prompt(sentence))
        print(response.strip())

if __name__ == '__main__':
    mapper = QuestionMapper()
    jsonl_file = open('chat-content.jsonl', 'r')
    lines = list(jsonl_file)
    for line in lines:
        json_line = json.loads(line)
        question = json_line['prompt']
        answer = json_line['completion']
        mapper.bucket.add(question, answer)
    while True:
        sentence = input()
        mapper.map(sentence)