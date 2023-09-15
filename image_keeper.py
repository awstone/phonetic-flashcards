import json
import base64
from PIL import Image, ImageTk
from io import BytesIO
import tkinter as tk

# Function to load image from base64
def load_image_from_base64(base64_str):
    image_bytes = base64.b64decode(base64_str)
    img = Image.open(BytesIO(image_bytes))
    img = img.resize((200, 200), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)

# Function to show next image pair
def next_pair():
    global current_index, data, canvas1, canvas2
    if current_index < len(data) - 1:
        current_index += 1
        display_current_pair()

# Function to delete current image pair
def delete_pair():
    global current_index, data, new_data
    if current_index >= 0 and current_index < len(data):
        # Do not append to new_data list, effectively deleting it
        next_pair()

# Function to keep current image pair
def keep_pair():
    global current_index, data, new_data
    if current_index >= 0 and current_index < len(data):
        new_data.append(data[current_index])
        next_pair()

# Function to display the current image pair
def display_current_pair():
    global current_index, data, canvas1, canvas2
    if current_index >= 0 and current_index < len(data):
        item = data[current_index]
        base64_1 = item['pair']['item1']['b64_image']
        base64_2 = item['pair']['item2']['b64_image']
        img1 = load_image_from_base64(base64_1)
        img2 = load_image_from_base64(base64_2)
        canvas1.itemconfig(image_on_canvas1, image=img1)
        canvas2.itemconfig(image_on_canvas2, image=img2)
        canvas1.image = img1
        canvas2.image = img2

# Initialize the Tkinter app
app = tk.Tk()
app.title("Image Keeper")

# Create two canvases to display the image pair
canvas1 = tk.Canvas(app, width=200, height=200)
canvas1.pack(side=tk.LEFT)
canvas2 = tk.Canvas(app, width=200, height=200)
canvas2.pack(side=tk.RIGHT)

# Initialize
current_index = 0

# Read the JSON file
with open("responses.json", "r") as f:
    data = json.load(f)

# Create images on canvas with empty images initially
image_on_canvas1 = canvas1.create_image(100, 100, image=None)
image_on_canvas2 = canvas2.create_image(100, 100, image=None)

# Create buttons
next_button = tk.Button(app, text="Next", command=next_pair)
next_button.pack(side=tk.LEFT, padx=10, pady=10)
delete_button = tk.Button(app, text="Delete", command=delete_pair)
delete_button.pack(side=tk.RIGHT, padx=10, pady=10)

# Display the first image pair
display_current_pair()

# Run the Tkinter event loop
app.mainloop()

# Save the remaining pairs back to the original JSON file
with open("responses_filtered.json", "w") as f:
    json.dump(data, f)
