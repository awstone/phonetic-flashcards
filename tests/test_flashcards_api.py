import requests
from urllib.parse import quote
import cv2
import numpy as np
import base64

# Testing /send_string/ endpoint
query = 'medial sound /r/'
encoded_query = quote(query)
response = requests.post(f"http://127.0.0.1:8000/generate/{encoded_query}")
response_json = response.json()
print("Response from /generate/:", response_json)

base64_encoded = response_json['output_image_base64']
# Decode the Base64 string, getting a bytes type result
decoded_bytes = base64.b64decode(base64_encoded)

# Convert bytes to NumPy array
nparr = np.frombuffer(decoded_bytes, np.uint8)

# Decode the NumPy array to an image
image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

