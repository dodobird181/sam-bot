from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import uuid4

from questions.context import ContextNode


@dataclass
class QuestionNode(ContextNode):
    """
    A string question-answer pair, along with a vector-embedding of the question, and a unique ID.
    """
    qtext: str # Question text
    atext: str # Answer text
    vector: List[float] # Embedding vector
    id: str = str(uuid4()) # ID, generated on init by default

    def __str__(self) -> str:
        rows = ''
        for row in self.vector:
            rows += str(row)
        print(rows)
        vector_hash =  hashlib.sha256(rows.encode('UTF-8')).hexdigest()
        result = ''
        result_lines = [
            f'[Question Node - {self.id} - {vector_hash}]\n',
            f'Q: {self.qtext}\n',
            f'A: {self.atext}\n',
        ]
        longest_line_length = 0
        for line in result_lines:
            result += line
            if len(line) > longest_line_length:
                longest_line_length = len(line)
        line_sep = '-' * longest_line_length
        return line_sep + '\n' + result + '\n' +  line_sep
    
    def get_vector(self) -> List[float]:
        """
        Implement abstract method.
        """
        return self.vector

    def to_dict(self) -> Dict[str, Any]:
        """
        Dictionary representation of the `QuestionNode`.
        """
        return {
            'id': self.id,
            'qtext': self.qtext,
            'atext': self.atext,
            'vector': self.vector,
        }
    
    @classmethod
    def from_dict(cls, dict) -> QuestionNode:
        """
        Conversion from dictionary to a `QuestionNode` instance.
        """
        return QuestionNode(
            id=dict['id'],
            qtext=dict['qtext'],
            atext=dict['atext'],
            vector=dict['vector'],
        )