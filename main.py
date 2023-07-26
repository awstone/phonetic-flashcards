from diffusers import DiffusionPipeline
import torch


pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-0.9",
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16")
# pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
pipe.to("cuda")

prompt = "An astronaut riding a green horse"

images = pipe(prompt=prompt).images[0]
