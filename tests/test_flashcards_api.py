import requests
from urllib.parse import quote
import cv2
import numpy as np
import base64

# Testing /send_string/ endpoint
query = 'Generate a pair of words with maximally contrasting phonemes that differ at the initial sound and one of the sounds is /b/'
encoded_query = quote(query)
response = requests.get(f"http://127.0.0.1:8000/generate/{encoded_query}")
response_json = response.json()
# print("Response from /generate/:", response_json)

item1 = response_json['pair']['item1']
item2 = response_json['pair']['item2']

print(item1['visual_prompt'])
print(item2['visual_prompt'])

def write_image(word, b64):
    # Decode the Base64 string, getting a bytes type result
    decoded_bytes = base64.b64decode(b64)

    # Convert bytes to NumPy array
    nparr = np.frombuffer(decoded_bytes, np.uint8)

    # Decode the NumPy array to an image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite(f'{word}.jpg', image)

write_image(item1['word'], item1['b64_image'])
write_image(item2['word'], item2['b64_image'])
