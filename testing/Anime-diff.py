from diffusers import StableDiffusionPipeline
import hashlib

model_id = "Linaqruf/anything-v3.0"
pipe = StableDiffusionPipeline.from_pretrained(model_id)

# Take user input for the prompt
prompt = input("Enter the prompt: ")

image = pipe(prompt).images[0]

# Generate the MD5 hash of the image data
hash_object = hashlib.md5(image.tobytes())
filename = hash_object.hexdigest() + ".png"

# Save the image with the hashed filename
image.save("./" + filename)