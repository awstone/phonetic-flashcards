# from transformers import AutoTokenizer, AutoModelForCausalLM, PyTorchBenchmark, PyTorchBenchmarkArguments
# args = PyTorchBenchmarkArguments(models=["stabilityai/StableBeluga-7B"], batch_sizes=[8], sequence_lengths=[8, 32, 128, 512])
# benchmark = PyTorchBenchmark(args)
# print(benchmark.run())
# tokenizer = AutoTokenizer.from_pretrained("stabilityai/StableBeluga-7B", use_fast=False)
# model = AutoModelForCausalLM.from_pretrained("stabilityai/StableBeluga-7B")

import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# device = torch.device('cuda')  # use 'cpu' if you want to benchmark on CPU

# initialize the model and the tokenizer
tokenizer = AutoTokenizer.from_pretrained("stabilityai/StableBeluga-7B", use_fast=False, legacy=False)
model = AutoModelForCausalLM.from_pretrained("stabilityai/StableBeluga-7B")

# prepare the input
input_text = "Write a poem in the style of Robert Frost for the college introductory physics class. \
    The response should be approximately 100 words long and written in a snappy and punchy style, \
    using short sentences and non-standard, conversational grammar. \
    I want you to write in the same way you would write to a friend."
input_tokens = tokenizer.encode(input_text, return_tensors='pt')
num_tokens = input_tokens.shape[1]  # count the number of tokens

for i in range(1):
    # time the inference
    start_time = time.time()
    with torch.no_grad():
        outputs = model(input_tokens)
        print(tokenizer.decode(outputs[0], skip_special_tokens=True))
    end_time = time.time()

    # calculate and print tokens per second
    tokens_per_sec = num_tokens / (end_time - start_time)
    print(f'Number of Tokens: {num_tokens}. Tokens per second: {tokens_per_sec}')
