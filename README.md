# Astuko

![Repo Size](https://img.shields.io/github/repo-size/Exohayvan/atsuko)

### [Click Here to Invite Bot](https://discord.com/oauth2/authorize?client_id=407929486206566400&permissions=2199023255551&scope=bot)
### [Click Here to Join My Discord](https://discord.gg/BYF6NTs)

Astuko is a Discord bot designed with a focus on extensibility and reliability. It's built using Python and relies on a dynamic cog system for modularity. This allows you to easily add new features by simply creating new Python files in the `commands` directory.

The bot's features include a custom help interface, and a bunch of commands.
Find those commands [Here](https://github.com/Exohayvan/atsuko/blob/main/commands/README.md)

The reliability aspect comes from the `Watcher.py` script, which continuously monitors the bot process. If the process exits with a specific exit code (42), it restarts the bot. This ensures that the bot is always up and running, even in the face of unexpected issues.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

To run Astuko, you need Python 3 and the discord.py library installed on your system. You can install the discord.py library using pip:

```markdown
pip install discord.py
```

### Installation

Clone the repository and navigate into the project directory:

```markdown
git clone https://github.com/Exohayvan/astuko.git
cd astuko
```

The entry point for Astuko is the `Watcher.py` script. To start the bot and enable the watchdog functionality, execute `Watcher.py` using Python:

```bash
python3 watcher.py
```

This will start the Astuko bot and keep it running, restarting it if necessary.

## Contributing

Please read [CONTRIBUTING.md](link-to-contributing.md) for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
