import json
import os

# Check if the JSON file exists
if os.path.exists('../config.json'):
    # Read the existing JSON file
    with open('../config.json', 'r') as f:
        existing_config = json.load(f)
else:
    existing_config = {}

# Prompt for the bot token and check if it should be updated
bot_token = input("Please enter your bot token: ")
if 'bot_token' in existing_config:
    update = input("The bot token already exists. Do you want to update it? (y/n): ")
    if update.lower() == 'y':
        existing_config['bot_token'] = bot_token
else:
    existing_config['bot_token'] = bot_token

# Prompt for the GitHub token and check if it should be updated
github_token = input("Please enter your GitHub token: ")
if 'GITHUB_TOKEN' in existing_config:
    update = input("The GitHub token already exists. Do you want to update it? (y/n): ")
    if update.lower() == 'y':
        existing_config['GITHUB_TOKEN'] = github_token
else:
    existing_config['GITHUB_TOKEN'] = github_token

# Prompt for the private key path
private_key_path = input("Please enter the private key path: ")
existing_config['PRIVATE_KEY_PATH'] = private_key_path

# Hardcode the owner ID
owner_id = 276782057412362241
existing_config['owner_id'] = owner_id

# Write the updated config to the JSON file
with open('../config.json', 'w') as f:
    json.dump(existing_config, f)

print("Config saved to ../config.json")