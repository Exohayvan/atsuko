import json
import os

# Prompt for the bot token and GitHub token
bot_token = input("Please enter your bot token: ")
github_token = input("Please enter your GitHub token: ")

# Hardcode the owner ID
owner_id = 276782057412362241

# Create a dictionary with the tokens
config = {
    "bot_token": bot_token,
    "GITHUB_TOKEN": github_token,
    "owner_id": owner_id
}

# Write the dictionary to a JSON file
with open('../config.json', 'w') as f:
    json.dump(config, f)

print("Config saved to ../config.json")
