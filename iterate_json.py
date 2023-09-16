import json
import base64
from PIL import Image
from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt

# Read the JSON file
with open("responses_filtered_1.json", "r") as f:
    data = json.load(f)

# Create a new list to hold the items you want to keep
new_data = []

# Iterate through JSON items
for i, item in enumerate(data):
    image_base64_1 = item['pair']['item1']['b64_image']
    image_base64_2 = item['pair']['item2']['b64_image']
    # del item['pair']['item1']['b64_image']
    # del item['pair']['item2']['b64_image']
    

    # Decode and display the image
    image_bytes_1 = base64.b64decode(image_base64_1)
    image_bytes_2 = base64.b64decode(image_base64_2)
    image_1 = Image.open(BytesIO(image_bytes_1))
    image_2 = Image.open(BytesIO(image_bytes_2))
    
    # Create a single figure
    plt.figure()

    # First subplot (1 row, 2 columns, index 1)
    plt.subplot(1, 2, 1)
    plt.imshow(image_1)
    plt.title("Image 1")

    # Second subplot (1 row, 2 columns, index 2)
    plt.subplot(1, 2, 2)
    plt.imshow(image_2)
    plt.title("Image 2")

    item1 = item['pair']['item1']
    word1 = item1['word']
    sound1 = item1['sound']
    ipa1 = item1['ipa']
    place1 = item1['place']
    manner1 = item1['manner']
    voicing1 = item1['voicing']

    item2 = item['pair']['item2']
    word2 = item2['word']
    sound2 = item2['sound']
    ipa2 = item2['ipa']
    place2 = item2['place']
    manner2 = item2['manner']
    voicing2 = item2['voicing']

    other_data = [word1, sound1, ipa1, place1, manner1, voicing1,
                  word2, sound2, ipa2, place2, manner2, voicing2]
    print(f"image {i} - pair: {other_data}")
    plt.show()

    # item['pair']['item1']['b64_image'] = image_base64_1
    # item['pair']['item2']['b64_image'] = image_base64_2

    # Ask the user if they want to delete this item
    should_delete = input("Do you want to delete this item? (y/n): ")
    if should_delete.lower() == 'n':
        # Delete the item from your data structure (you'll still need to write it back to JSON)
        new_data.append(data[i])

# Write the modified JSON back to the file
with open("responses_filtered_1.json", "w") as f:
    json.dump(new_data, f)
