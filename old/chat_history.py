import math
from functools import reduce


class ChatHistory:

    class Turn:
        AI = 'ai'
        USER = 'user'

    def __init__(self, initial_prompt: str, user_name='USER', ai_name='AI'):
        self._initial_prompt = initial_prompt
        self._user_name = user_name
        self._ai_name = ai_name
        self._turn = self.Turn.USER
        self._history = [self._initial_prompt + '\n']

    def _change_turn(self) -> None:
        if self._turn == self.Turn.USER:
            self._turn = self.Turn.AI
        else:
            self._turn = self.Turn.USER

    def _get_speaker_name(self, turn) -> str:
        """
        Get the name of the speaker given the turn.
        """
        return self._user_name if turn == self.Turn.USER else self._ai_name

    def _get_start_block(self, turn) -> str:
        return f'[START OF {self._get_speaker_name(turn)} SENTENCE]'
    
    def _get_end_block(self, turn) -> str:
        return f'[END OF {self._get_speaker_name(turn)} SENTENCE]'

    def _make_sentence(self, turn, sentence) -> str:
        return f'{self._get_start_block(turn)} {sentence} {self._get_end_block(turn)}'
    
    def _remove_ai_blocks(self, sentence) -> str:
        start_block = self._get_start_block(self.Turn.AI)
        end_block = self._get_end_block(self.Turn.AI)
        cleaned = sentence.replace(start_block, '')
        cleaned = cleaned.replace(end_block, '')
        cleaned = cleaned.strip(' \n')
        return cleaned

    def user_speaks(self, sentence) -> None:
        """
        Input a user sentence.
        """
        assert self._turn == self.Turn.USER
        user_sentence = self._make_sentence(self.Turn.USER, sentence)
        self._history.append(user_sentence)
        self._change_turn()

    def ai_speaks(self, sentence) -> None:
        """
        Input an AI sentence.
        """
        assert self._turn == self.Turn.AI
        ai_sentence = self._remove_ai_blocks(sentence) # Sometimes GPT will return chat history blocks...
        ai_sentence = self._make_sentence(self.Turn.AI, ai_sentence)
        self._history.append(ai_sentence)
        self._change_turn()
    
    def peek_history(self, limit=math.inf) -> str:
        """
        Show recent chat history.
        """
        max_limit = len(self._history)
        limit = limit if limit <= max_limit else max_limit
        history = self._history if limit is None else self._history[-limit:]
        return str(reduce(lambda s1, s2: s1 + '\n' + s2, history, ''))
    
    def peek_history_with_initial(self, limit=math.inf) -> str:
        return self._initial_prompt + '\n' + self.peek_history(limit=limit)
    
    def last_ai_sentence(self) -> str:
        assert self._turn == self.Turn.USER # AI spoke last
        return self._remove_ai_blocks(self.peek_history(1))
