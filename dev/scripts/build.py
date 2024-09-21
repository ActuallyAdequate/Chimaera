import subprocess
import sys
import os

# Function to install a package if not already installed
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"{package} is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    else:
        print(f"{package} is already installed.")

# Function to run another Python script
def run_script(script_name, *args):
    try:
        command = [sys.executable, script_name] + list(args)
        result = subprocess.run(command, check=True)
        if result.returncode == 0:
            print(f"{script_name} ran successfully.")
        else:
            print(f"{script_name} encountered an issue.")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")

# Main function to handle the build process
def main():
    # Install necessary packages
    install_package("yaml")   # PyYAML for the YAML conversion script
    install_package("pandas") # pandas for CSV manipulation

    # Define paths for the scripts and input/output
    conversion_script = "dev/scripts/process_bodyparts.py" # Path to your conversion script
    yaml_file = "core/rules/body-part-list.yaml"   # Path to your YAML file
    output_folder = "build"      # Path to output folder

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Run the YAML-to-CSV conversion script
    run_script(conversion_script, yaml_file, output_folder)

    # Add more scripts to run here, for example:
    # run_script("another_script.py", "arg1", "arg2")

if __name__ == "__main__":
    main()
