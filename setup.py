import json
import os

# Prompt for the bot token, GitHub token, and private key path
bot_token = input("Please enter your bot token: ")
github_token = input("Please enter your GitHub token: ")
private_key_path = input("Please enter the private key path: ")

# Hardcode the owner ID
owner_id = 276782057412362241

# Create a dictionary with the tokens
config = {
    "bot_token": bot_token,
    "GITHUB_TOKEN": github_token,
    "owner_id": owner_id,
    "PRIVATE_KEY_PATH": private_key_path
}

# Check if the JSON file exists
if os.path.exists('../config.json'):
    # Read the existing JSON file
    with open('../config.json', 'r') as f:
        existing_config = json.load(f)
    
    # Check if each key exists in the existing config
    for key in config:
        if key in existing_config:
            # Ask if the value should be updated
            update = input(f"The {key} already exists. Do you want to update it? (y/n): ")
            if update.lower() == 'y':
                existing_config[key] = config[key]
        else:
            # Key doesn't exist, add it to the existing config
            existing_config[key] = config[key]

    # Write the updated config to the JSON file
    with open('../config.json', 'w') as f:
        json.dump(existing_config, f)
else:
    # Write the new config to a JSON file
    with open('../config.json', 'w') as f:
        json.dump(config, f)

print("Config saved to ../config.json")