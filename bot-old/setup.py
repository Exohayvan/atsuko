import json
import os

# Check if the JSON file exists
if os.path.exists('../../config.json'):
    # Read the existing JSON file
    with open('../../config.json', 'r') as f:
        existing_config = json.load(f)
else:
    existing_config = {}

# Prompt for the bot token if it doesn't exist or ask if it should be updated
if 'bot_token' not in existing_config:
    bot_token = input("Please enter your bot token: ")
    existing_config['bot_token'] = bot_token
else:
    update = input("The bot token already exists. Do you want to update it? (y/n): ")
    if update.lower() == 'y':
        bot_token = input("Please enter your bot token: ")
        existing_config['bot_token'] = bot_token

# Prompt for the GitHub token if it doesn't exist or ask if it should be updated
if 'GITHUB_TOKEN' not in existing_config:
    github_token = input("Please enter your GitHub token: ")
    existing_config['GITHUB_TOKEN'] = github_token
else:
    update = input("The GitHub token already exists. Do you want to update it? (y/n): ")
    if update.lower() == 'y':
        github_token = input("Please enter your GitHub token: ")
        existing_config['GITHUB_TOKEN'] = github_token

# Prompt for the private key path if it doesn't exist or ask if it should be updated
if 'PRIVATE_KEY_PATH' not in existing_config:
    private_key_path = input("Please enter the private key path: ")
    existing_config['PRIVATE_KEY_PATH'] = private_key_path
else:
    update = input("The private key path already exists. Do you want to update it? (y/n): ")
    if update.lower() == 'y':
        private_key_path = input("Please enter the private key path: ")
        existing_config['PRIVATE_KEY_PATH'] = private_key_path

# Prompt for the App ID if it doesn't exist or ask if it should be updated
if 'APP_ID' not in existing_config:
    app_id = input("Please enter your App ID: ")
    existing_config['APP_ID'] = app_id
else:
    update = input("The App ID already exists. Do you want to update it? (y/n): ")
    if update.lower() == 'y':
        app_id = input("Please enter your App ID: ")
        existing_config['APP_ID'] = app_id

# Prompt for the Installation ID if it doesn't exist or ask if it should be updated
if 'INSTALLATION_ID' not in existing_config:
    installation_id = input("Please enter your Installation ID: ")
    existing_config['INSTALLATION_ID'] = installation_id
else:
    update = input("The Installation ID already exists. Do you want to update it? (y/n): ")
    if update.lower() == 'y':
        installation_id = input("Please enter your Installation ID: ")
        existing_config['INSTALLATION_ID'] = installation_id
        
# Hardcode the owner ID
owner_id = 276782057412362241
existing_config['owner_id'] = owner_id

# Write the updated config to the JSON file
with open('../../config.json', 'w') as f:
    json.dump(existing_config, f)

print("Config saved to ../../config.json")