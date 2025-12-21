import sys
sys.path.insert(0, r'c:/Users/Seratul Mustakim/Downloads/College_chatbot/College_chatbot')
import new_app
from app.core import retriever as ret

q = "Who is our hod?"
res = ret.retrieve(q, 'general', new_app.VECTOR_INDEX, new_app.ALL_DOCS)
print('FOUND=', len(res))
if res:
    print('\n---TOP RESULT (first 800 chars)---\n')
    print(res[0][:800])
else:
    print('No results')
