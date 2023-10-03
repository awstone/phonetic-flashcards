import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from diffusers import DiffusionPipeline


tokenizer = AutoTokenizer.from_pretrained("stabilityai/StableBeluga2", use_fast=False, legacy=False)
model = AutoModelForCausalLM.from_pretrained("stabilityai/StableBeluga2", load_in_4bit=True, low_cpu_mem_usage=True)

# TODO huggingface quantization

# load both base & refiner
base = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, variant="fp16", use_safetensors=True
)
base.to("cuda")
refiner = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-refiner-1.0",
    text_encoder_2=base.text_encoder_2,
    vae=base.vae,
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16",
)
refiner.to("cuda")

def parse_output(output):
    lines = output.split('\n')
    for line in lines:
        if line.startswith('text-to-image:') or line.startswith(' text-to-image:'):
            prompt = line.split(':')[1]
        else:
            output += line
    return prompt, output

def inference_tti(prompt):
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
    return image

def generate_story(system_prompt, user_prompt):
    prompt = f"### System:\n{system_prompt} \n\n ### User:\n{user_prompt} \n\n### Assistant:\n"
    inputs = tokenizer(prompt, return_tensors='pt').to('cuda:1')
    with torch.no_grad():
        output = model.generate(**inputs, do_sample=True, top_p=0.95, top_k=0, max_new_tokens=1024)
        output = tokenizer.decode(output[0], skip_special_tokens=True)
    print('output: ', output)
    prompt, story = parse_output(output)
    img = inference_tti(prompt)
    return story, img

with gr.Blocks() as demo:
    system_prompt = gr.Textbox(label='system prompt')
    user_prompt = gr.Textbox(label='user prompt')
    gen_story_btn = gr.Button('generate story')
    story = gr.Textbox(label='story')
    image = gr.Image()
    gen_story_btn.click(fn=generate_story, inputs=[system_prompt, user_prompt], outputs=[story, image])
    
demo.launch()