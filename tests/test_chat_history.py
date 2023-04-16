import unittest

from chat_history import ChatHistory


class TestChatHistory(unittest.TestCase):

    def setUp(self):
        self.h = ChatHistory('TEST PROMPT')

    def test_peek_history(self):
        self.h.user_speaks('Hi!')
        self.h.ai_speaks('Hey there!')
        self.h.user_speaks('Sup dawg!')
        self.assertEqual(
            'TEST PROMPT\nUSER: Hi!\nAI: Hey there!\nUSER: Sup dawg!',
            self.h.peek_history())
        
    def test_peek_history_with_limit(self):
        self.h.user_speaks('Hi!')
        self.h.ai_speaks('Hey there!')
        self.h.user_speaks('Sup dawg!')
        self.assertEqual(
            'TEST PROMPT\nUSER: Hi!\nAI: Hey there!\nUSER: Sup dawg!',
            self.h.peek_history(50000))
        self.assertEqual(
            'TEST PROMPT\nUSER: Hi!\nAI: Hey there!\nUSER: Sup dawg!',
            self.h.peek_history(4))
        self.assertEqual(
            '\nUSER: Hi!\nAI: Hey there!\nUSER: Sup dawg!',
            self.h.peek_history(3))
        self.assertEqual(
            '\nAI: Hey there!\nUSER: Sup dawg!',
            self.h.peek_history(2))
        self.assertEqual(
            '\nUSER: Sup dawg!',
            self.h.peek_history(1))

    def test_initial_prompt_in_history(self):
        self.assertEqual('TEST PROMPT', self.h.peek_history())

    def test_turn_swapping(self):
        self.h.user_speaks('User speaks!')
        self.assertEqual(ChatHistory.Turn.AI, self.h._turn)
        self.h.ai_speaks('AI speaks!')
        self.assertEqual(ChatHistory.Turn.USER, self.h._turn)

    def test_speaking_out_of_turn_raises(self):
        with self.assertRaises(AssertionError):
            self.h.ai_speaks('Out of turn!')
        self.h.user_speaks('User speaks!')
        with self.assertRaises(AssertionError):
            self.h.user_speaks('Out of turn!')

    def test_speaking_out_of_turn_does_not_add_to_history(self):
        self.assertEqual(len(self.h._history), 1)
        with self.assertRaises(AssertionError):
            self.h.ai_speaks('Out of turn!')
        self.assertEqual(len(self.h._history), 1)
        self.h.user_speaks('User speaks!')
        self.assertEqual(len(self.h._history), 2)
        self.h.ai_speaks('AI speaks!')
        self.assertEqual(len(self.h._history), 3)


if __name__ == '__main__':
    unittest.main()