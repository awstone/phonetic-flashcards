# phonetic-flashcards
Phonetic Flashcard Generation - AI Institute for Exceptional Education

Setting up: 

Install requirements:
`python3 -m pip install -r requirements.txt`

To run the flashcards API use: 

`uvicorn flashcards_api:app --reload`

Send a GET request to `/generate/your_query_here`

See `test/test_flashcards_api.py` for example useage.

