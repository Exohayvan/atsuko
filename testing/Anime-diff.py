from diffusers import StableDiffusionPipeline
import hashlib
import torch

model_id = "dreamlike-art/dreamlike-anime-1.0"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)

# Take user input for the prompt
prompt = "anime, masterpiece, high quality, high resolution " + input("Enter the prompt: ")

negative_prompt = 'simple background, duplicate, retro style, low quality, lowest quality, 1980s, 1990s, 2000s, 2005 2006 2007 2008 2009 2010 2011 2012 2013, bad anatomy, bad proportions, extra digits, lowres, username, artist name, error, duplicate, watermark, signature, text, extra digit, fewer digits, worst quality, jpeg artifacts, blurry'
image = pipe(prompt, negative_prompt=negative_prompt).images[0]

# Generate the MD5 hash of the image data
hash_object = hashlib.md5(image.tobytes())
filename = hash_object.hexdigest() + ".png"

# Save the image with the hashed filename
image.save("./" + filename)