from fastapi import FastAPI, File, UploadFile, Form, Path, Query
import base64
from fastapi.responses import FileResponse
from PIL import Image
import io
import pathlib
import numpy as np
import cv2
import random
from hf_hub_ctranslate2 import TranslatorCT2fromHfHub, GeneratorCT2fromHfHub
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from diffusers import DiffusionPipeline
import math
from PIL import Image, ImageFont, ImageDraw
import re
import uuid
import json
import itertools
from io import BytesIO

import openai
import os
from dotenv import load_dotenv

# load both base & refiner
def load_diffusion_model():
    base = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True
            ).to("cuda")
    refiner = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-refiner-1.0",
            text_encoder_2=base.text_encoder_2,
            vae=base.vae,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16",
            ).to("cuda")
    return base, refiner


def call_model(llm_json, base, refiner):
    objects = [llm_json['pair']['item1']['word'],
               llm_json['pair']['item2']['word']]
    print("Objects are: ", objects)
    art_style='cartoon'
    images = []
    for i, obj in enumerate(objects):
        prompt = f"a {art_style} of a {obj}"
        # Define how many steps and what % of steps to be run on each experts (80/20) here
        n_steps = 40
        high_noise_frac = 0.8

        # run both experts
        image = base(
            prompt=prompt,
            num_inference_steps=n_steps,
            # denoising_end=high_noise_frac,
            output_type="latent",
        ).images
        image = refiner(
            prompt=prompt,
            num_inference_steps=n_steps,
            # denoising_start=high_noise_frac,
            image=image,
        ).images[0]
        images.append(image)
        # image.save(f"/home/awstone/phonetic-flashcards/images/{obj}.png")
    return images

# def get_text_dimensions(text_string, font):
#     # https://stackoverflow.com/a/46220683/9263761
#     ascent, descent = font.getmetrics()

#     text_width = font.getmask(text_string).getbbox()[2]
#     text_height = font.getmask(text_string).getbbox()[3] + descent

#     return (text_width, text_height)

# def add_text_to_image(image_path, text, x, y, font_size=1.0, font_color=(0, 0, 0), thickness=2):
#     # Read the image
#     image = image_path

#     # Define the font properties
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     font_scale = font_size
#     font_thickness = thickness
#     # Calculate the size of the text to get its width and height
#     # (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, font_thickness)
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     pil_image = Image.fromarray(image)
#     draw = ImageDraw.Draw(pil_image)
#     font = ImageFont.truetype('/home/awstone/dejavu-fonts-ttf-2.37/ttf/DejaVuSerif.ttf', size=30, encoding='unic')
#     text_width, text_height = get_text_dimensions(text, font)

#     # Calculate the coordinates to center the text at the specified (x, y) point
#     text_x = x - text_width // 2
#     text_y = y - text_height // 2

#     # Draw the text on the image
#     # cv2.putText(image, text, (text_x, text_y), font, font_scale, font_color, font_thickness)

    
    
#     # draw.text((text_x, text_y), text, font=font)
#     print(f'text to go on card {text}')
#     draw.text((text_x, text_y), text, font=font, fill='black')
#     image = np.asarray(pil_image)
#     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#     return image

# def overlay_images(base_image_path, overlay_image_path, x1, y1, x2, y2, name):
#     # Read the base and overlay images
#     # base_image = cv2.imread(base_image_path)
#     # Create a blank white image
#     width, height = 400, 600
#     image = np.ones((height, width, 3), np.uint8) * 255

#     # Add a border with rounded edges

#     # Parameters
#     border_color = (0, 0, 0)  # Black
#     border_thickness = 10  # Thickness of the border
#     radius = 30  # Radius for the rounded corners

#     # Top left corner
#     cv2.ellipse(image, (radius, radius), (radius, radius), 180, 0, 90, border_color, border_thickness)
#     # Top right corner
#     cv2.ellipse(image, (width - radius, radius), (radius, radius), 270, 0, 90, border_color, border_thickness)
#     # Bottom left corner
#     cv2.ellipse(image, (radius, height - radius), (radius, radius), 90, 0, 90, border_color, border_thickness)
#     # Bottom right corner
#     cv2.ellipse(image, (width - radius, height - radius), (radius, radius), 0, 0, 90, border_color, border_thickness)

#     # Draw the straight edges
#     cv2.line(image, (radius, 0), (width - radius, 0), border_color, border_thickness)  # Top edge
#     cv2.line(image, (radius, height), (width - radius, height), border_color, border_thickness)  # Bottom edge
#     cv2.line(image, (0, radius), (0, height - radius), border_color, border_thickness)  # Left edge
#     cv2.line(image, (width, radius), (width, height - radius), border_color, border_thickness)  # Right edge

#     base_image = image
    
#     overlay_image = overlay_image_path

#     # Get the dimensions of the overlay image
#     overlay_height, overlay_width = overlay_image.shape[:2]

#     # Calculate the width and height of the region to overlay
#     width = x2 - x1
#     height = y2 - y1

#     # Resize the overlay image to match the size of the region to overlay
#     resized_overlay = cv2.resize(overlay_image, (width, height))

#     # Use the cv2.addWeighted function to blend the overlay image onto the base image
#     alpha = 0  # Change this value to adjust the transparency of the overlay
#     blended_image = cv2.addWeighted(base_image[y1:y2, x1:x2], alpha, resized_overlay, 1 - alpha, 0)

#     # Replace the region of interest on the base image with the blended image
#     base_image[y1:y2, x1:x2] = blended_image

#     image_path = base_image
#     text = name
#     x_coordinate = 208
#     y_coordinate = 450

#     result_image = add_text_to_image(image_path, text, x_coordinate, y_coordinate)

#     return result_image


# def generate_images(llm_json, base, refiner):
#     list_of_images = call_model(llm_json, base, refiner)
#     print("Objects to be displayed", list_of_images)
#     output_list = []
#     for i in range(len(list_of_images)):
#         image_name = list_of_images[i]
        
#         tempimg = cv2.imread("/home/awstone/phonetic-flashcards/images/" + image_name + ".png")
#         print("reading", "/home/awstone/phonetic-flashcards/images/" + image_name + ".png")
#         overlay_image_path = cv2.resize(tempimg, (tempimg.shape[0], tempimg.shape[0]))
#         # overlay_image_path = make_image_circular(overlay_image_path)
        
#         img_1 = np.zeros([60,140,1],dtype=np.uint8)
#         img_1.fill(255)
#         templatedirectory = "/home/awstone/phonetic-flashcards/templates/"
#         random_idx = random.randint(1, 8)

#         # Example usage
#         base_image_path = templatedirectory + 'template_' + str(random_idx) +'.png'
#         x1, y1 = 90, 100
#         x2, y2 = x1 + 235, y1 + 208  # Calculate the second coordinate based on width and height

#         result_image = overlay_images(base_image_path, overlay_image_path, x1, y1, x2, y2, image_name)
#         resized_image = cv2.resize(result_image, (415, 550))
#         color_flipped_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
#         output_list.append(color_flipped_image)
#     return output_list

def generate_images(llm_json, base, refiner):
    images = call_model(llm_json, base, refiner)
    return images

def run_llm(input_string):
    with open('/home/awstone/phonetic-flashcards/system-prompt.txt', 'r') as file:
        system_prompt = file.read()
    with open('/home/awstone/phonetic-flashcards/unified-prompt.txt', 'r') as file:
        unified_prompt = file.read()
    # append the user input to the unified prompt
    unified_prompt += input_string
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": unified_prompt}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
    )

    return response['choices'][0]['message']['content']
    

# Function to convert PIL image to Base64 string
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")  # Change PNG to JPEG if you prefer
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
    

def generate(input_string: str, c: str, l: str, s: str):

    if len(input_string) > 1024:
        return {"error": "Path too long"}
    print(f'input string: {input_string}')
    llm_json = run_llm(input_string)
    try:
        llm_json = json.loads(llm_json)
    except:
        return -1

    print(f'llm output: \n\n {llm_json}')
    
    base, refiner = load_diffusion_model()
    image_list = generate_images(llm_json, base, refiner)

    # encode the images
    b64_images = []
    for image in image_list:
        image = image.resize((512,512))
        b64_image = image_to_base64(image)
        b64_images.append(b64_image)
    item1 = llm_json['pair']['item1']
    item2 = llm_json['pair']['item2']
    unique_id = str(uuid.uuid4())
    word1 = item1['word']
    word2 = item2['word']
    sound1 = item1['sound']
    sound2 = item2['sound']
    ipa1 = item1['ipa']
    ipa2 = item2['ipa']
    place1 = item1['place']
    place2 = item2['place']
    manner1 = item1['manner']
    manner2 = item2['manner']
    voice1 = item1['voicing']
    voice2 = item2['voicing']
    explanation = llm_json['pair']['explanation']
    
    # Fake image (you should generate or load an actual image)
    # fake_image_bytes = output
    # output_image_base64 = base64.b64encode(fake_image_bytes).decode("utf-8")

    return {
        'uuid': unique_id,
        'prompt': input_string,
        'contrast': c,
        'location': l,
        'sound': s,
        'pair':{
            'item1':{
                'word': word1,
                'sound': sound1,
                'ipa': ipa1,
                'place': place1,
                'manner': manner1,
                'voicing': voice1,
                'b64_image': b64_images[0]
                },
            'item2':{
                'word': word2,
                'sound': sound2,
                'ipa': ipa2,
                'place': place2,
                'manner': manner2,
                'voicing': voice2,
                'b64_image': b64_images[1]
                }
            },
        'explanation': explanation
        }



if __name__ == '__main__':
    load_dotenv('/home/awstone/.bashrc')
    openai.api_key = os.environ["OPENAI_API_KEY"]

    contrasts = [ 'maximally']
    sounds = ['/s/', '/r/', '/l/']
    locations = ['initial', 'final']

    # Read the existing JSON data into a Python list
    try:
        with open("responses.json", 'r') as f:
            json_responses = json.load(f)
    except FileNotFoundError:
        # If the file does not exist, initialize an empty list
        json_responses = []
    except json.JSONDecodeError:
        # If the file exists but is empty or contains invalid JSON, initialize an empty list
        print("Error decoding JSON. Starting with an empty list.")
        json_responses = []
    for c, l, s in itertools.product(contrasts, locations, sounds):
        input_string = f'Generate a pair of words with {c} contrasting phonemes that differ at the {l} location and one of the sounds is {s}'
        output_json = generate(input_string, c, l, s)
        if output_json != -1:
            json_responses.append(output_json)
        
    json_string = json.dumps(json_responses, indent=4)
    # Write the JSON-formatted string to a file
    with open("responses.json", "w") as f:
        f.write(json_string)
        
