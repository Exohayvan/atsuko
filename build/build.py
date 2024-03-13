import subprocess, importlib.util
import sys
from colorama import init, Fore, Style

def setup_environment():
    """Check for pip, install and check for colorama, and verify Docker availability."""
    # Check if pip is installed
    try:
        subprocess.run(["pip", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("pip is not installed or not in the PATH. Please install pip to continue.")
        return False

    # Check if colorama is installed, and install it if not
    colorama_spec = importlib.util.find_spec("colorama")
    if colorama_spec is None:
        print("colorama package not found. Attempting to install colorama...")
        try:
            subprocess.run(["pip", "install", "colorama"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("colorama installed successfully.")
        except subprocess.CalledProcessError:
            print("Failed to install colorama. Please check your pip setup.")
            return False

    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Docker is not installed or not in the PATH. Please install Docker to continue.")
        return False

def is_windows():
    return sys.platform.startswith('win')

# Colorful print function
def cprint(message, color):
    print(color + message + Style.RESET_ALL)

def build_docker_image():
    # Define the path to the Dockerfile relative to the script location
    dockerfile_path = './Dockerfile'
    # Define the build context to be the project root, two levels up from the script location
    build_context = '../..'
    image_name = 'exohayvan/atsuko:latest'
    
    # Build the Docker build command
    command = [
        'docker', 'build',
        '-f', dockerfile_path,
        '-t', image_name,
        build_context
    ]
    
    # Run the command and stream output to terminal
    result = subprocess.run(command, text=True)
    
    # Check if the build was successful
    if result.returncode == 0:
        cprint("Docker image built successfully.", Fore.GREEN)
    else:
        cprint("Error building Docker image:", Fore.RED)

if __name__ == '__main__':
    run = setup_environment()
    if run == True:
        build_docker_image()
    else:
        print("Environment Setup Failed. Check output and try to install missing packages. Unable to start docker build until fixed.")