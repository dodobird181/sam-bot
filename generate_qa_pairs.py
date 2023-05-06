import json

from app.db import ObjectCollection, init_db
from app.embeddings import QAPair

init_db()
file = open('knowledge/extra-content.json', 'r')
data = json.loads(file.read())['data']
pairs = [QAPair(dict['question'], dict['answer']) for dict in data]
pairs = ObjectCollection(QAPair, *pairs)
pairs.save('qa_pairs')
file.close()
