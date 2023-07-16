from diffusers import StableDiffusionPipeline

model_id = "Linaqruf/anything-v3.0"
pipe = StableDiffusionPipeline.from_pretrained(model_id)

prompt = "pikachu"
image = pipe(prompt).images[0]

image.save("./pikachu.png")
