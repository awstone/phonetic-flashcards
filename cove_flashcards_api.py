# huggingface imports 
from diffusers import DiffusionPipeline

# torch imports
import torch

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
    # function to inference base and refiner
    def diffusion_inference(prompt):
        image = base(
            prompt=prompt,
            num_inference_steps=50,
            output_type="latent",
        ).images
        image = refiner(
            prompt=prompt,
            num_inference_steps=50,
            image=image,
        ).images[0]
        return image
    return diffusion_inference

def main():

    # load the diffusion mode
    diffusion_inference = load_diffusion_model()

    # prompt LLM as follows
    # 1. Create minimal pair, phonetic transcription, place of articulation,
    #    voicing, manner of articulation, text-to-image prompt.
    # 2. Consider baseline response and query to generate verification questions.
    # 3. Batch verification questions:
    #      a. Are the words foo and bar a minimally opposing pair?
    #      b. What is the phonetic transcription of "foo"?
    #      c. What is the phonetic transcription of "bar"?
    #      d. Do IPA1 and IPA2 have the same number of phonemes and differ by 1?
    #      e. What is the place of articulation, voicing, and manner of articulation of "foo"?
    #      f. What is the place of articulation, voicing, and manner of articulation of "bar"?
    #      g. Is the prompt: ____ a good visual representation of the word "foo"?
    #      h. Is the prompt: ____ a good visual representation of the word "bar"?
    # 4. Consider the response to all verification questions, baseline response, and queries to
    #    look for inconsistencies.

    # 1.
    
    

    # inference the diffusion model
    image = diffusion_inference(prompt)
    image.show()
    

if __name__ == '__main__':
    main()
