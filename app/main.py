import json

from gpt.requests.embedding import EmbeddingRequest
from gpt.serialization.embedding import (EmbeddingDeserializer,
                                         EmbeddingSerializer)
from questions import ContextStore, QuestionNode
from questions.context import ContextGenerator
from sklearn.neighbors import KDTree


def load_question_answer_pairs(path):
    nodes = []
    with open(path, 'r') as file:
        json_lines = json.load(file)
        for line in json_lines:
            response = EmbeddingRequest([line['prompt']]).send()
            vector = response['data'][0]['embedding']
            nodes.append(QuestionNode(
                line['prompt'],
                line['response'],
                vector,
            ))
    return nodes

path = 'data/knowledge/extra-content.json'
nodes = load_question_answer_pairs(path)
print(nodes)

exit(0)


qnodes = [
    QuestionNode(qtext='Hey how\'s it going?', atext='Good, how are you?', vector=[1, 1, 1]),
    QuestionNode(qtext='What is your favoriter color?', atext='Blue!', vector=[0, 0, 0]),
]

store = ContextStore(qnodes)
store.save_to_file('my_context.json')
store = ContextStore.load_from_file('my_context.json', QuestionNode)
generator = ContextGenerator(store)

response = EmbeddingRequest([input('User: ')]).send()
vector = response['data'][0]['embedding']
generator_res = generator.generate(vector)
print(generator_res)

exit(0)

questions = [
    "Hey how's it going?",
    "What is your favoriter color?", 
    "What is your job experience?", 
    "What are your hobbies?"]

path = 'test_embeddings.json'


import numpy as np

#request = EmbeddingRequest(questions)
#embedding = EmbeddingDeserializer.from_request(request)
#EmbeddingSerializer.save_to_file(path, embedding)
embedding = EmbeddingDeserializer.from_file(path)


while True:
    user_sentence = input()
    user_request = EmbeddingRequest([user_sentence])
    user_embedding = EmbeddingDeserializer.from_request(user_request)
    user_arr = np.array(user_embedding.vectors[0])
    q_input = np.array([user_arr])
    print(f'User shape: {user_arr.shape}')

    arr = np.array(embedding.vectors)
    print(arr.shape)
    tree = KDTree(arr)

    dist, ind = tree.query(q_input)
    print(f'Distance: {dist}, indices: {ind}')
    print(f'Result: {embedding.nodes[ind[0][0]].text()}')