import json
import math
from dataclasses import dataclass
from typing import Dict, Iterable, List
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
    
    def __len__(self):
        return len(self._qs.keys())

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

    @dataclass
    class Response:
        """
        Internal question-mapper response.
        """
        confidence_score: int
        similarity_score: int
        questions: List[str] # List because questions can tie for highest score.

        def __str__(self):
            s = '|=== QuestionMapper Response Object ===|\n'
            s += f'Confidence: {self.confidence_score}\n'
            s += f'Similarity: {self.similarity_score}\n'
            s += f'Question(s): {self.questions}\n'
            return s

    @dataclass
    class Rating:
        """
        The rating for a specific question.
        """
        question: str
        score: int
    
    class NoMappingFound(Exception):
        """
        No mapping could be found.
        """
        pass

    class ParseResponseError(NoMappingFound):
        """
        Something went wrong when parsing ChatGPT's response.
        """
        pass

    def __init__(self):
        self.bucket = QuestionBucket()

    def _get_prompt(self, sentence) -> str:
        p = 'Rate the following questions from 0 to 100 in their similarity to the given sentence.'
        p += 'And give a numeric score from 0 to 100 about your overall confidence in these ratings.\n'
        p += f'[QUESTIONS]\n{str(self.bucket)}[QUESTIONS]\n'
        p += f'[SENTENCE]\n{sentence}\n[SENTENCE]\n'
        p += f'[RATINGS]\n{self.UNKNOWN_QUESTION.question}: 0\n{sentence}: 100\n...'
        return p
    
    def _parse_ratings(self, rating_data: str) -> List[Rating]:
        try:
            ratings = []
            for rating_line in rating_data.split('\n'):
                line_data = rating_line.split(':')
                if len(line_data) >= 2:
                    question = line_data[0]
                    score = int(line_data[1])
                    ratings.append(self.Rating(question, score))
            assert len(ratings) == len(self.bucket) # Should be same number of ratings as questions
            return ratings
        except AssertionError as e:
            msg = 'Number of ratings parsed does not match the number of questions in the question '
            msg += f'mapper [{len(ratings)} ratings, {len(self.bucket)} questions].'
            raise self.ParseResponseError(msg) from e
        except Exception as e:
            msg = 'Could not parse rating data.'
            raise self.ParseResponseError(msg) from e
    
    def _parse_confidence(self, confidence_data: str) -> int:
        try:
            [_, confidence] = confidence_data.split(':')
            confidence = confidence.strip()
            confidence = confidence.replace('%', '') # Remove percentage signs
            if '/' in confidence:
                # GPT probably returned a fraction because it felt a little creative...
                [numerator, denominator] = confidence.split('/')
                assert int(denominator) == 10
                return int(numerator) * 10
            else:
                return int(confidence)
        except Exception as e:
            msg = f'Could not parse confidence data [{confidence_data}] from response.'
            raise self.ParseResponseError(msg) from e
    
    def _parse_response(self, response: str, confidence_cutoff: int, similarity_cutoff: int) -> Response:
        """
        Parse the question-mapping response from ChatGPT
        """
        try:
            response = response.strip()
            [rating_data, confidence_data] = response.split('[RATINGS]') # raises ValueError
            ratings = self._parse_ratings(rating_data)
            confidence = self._parse_confidence(confidence_data)
            
            # Find the highest-rated question(s)
            best_rating = -math.inf
            best_questions = []
            for rating in ratings:
                if rating.score > best_rating:
                    best_rating = rating.score
                    best_questions = [rating.question]
                elif rating.score == best_rating:
                    best_questions.append(rating.question)
                else:
                    pass
            
            if best_rating < similarity_cutoff:
                msg = f'Highest-rated question(s) {best_questions} with rating {best_rating} '
                msg += f'fell short of the similarity cutoff >= {similarity_cutoff}.'
                raise self.NoMappingFound(msg)
            
            if confidence < confidence_cutoff:
                msg = f'Confidence score [{confidence}] fell short of the confidence '
                msg += f'cutoff >= {confidence_cutoff}.'
                raise self.NoMappingFound(msg)
            
            # All good! Return response.
            return self.Response(
                confidence_score=confidence,
                similarity_score=best_rating,
                questions=best_questions)

        except ValueError as e:
            msg = 'Could not separate ratings from confidence score.'
            raise self.ParseResponseError(msg) from e

    def map(self, sentence, confidence_cutoff=70, similarity_cutoff=70) -> UUID:
        response = ChatGPTRequest(self._get_prompt(sentence)).send()
        print(self._get_prompt(sentence))
        print(response.strip())
        print(self._parse_response(response, confidence_cutoff, similarity_cutoff))

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