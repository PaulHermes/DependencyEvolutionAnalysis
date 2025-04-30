import subprocess
import os
from global_parameters import *

def output_pom_tree(mvn_path: str, output_file: str):
    pom_path = os.path.abspath(os.path.join(script_dir, clone_dir))
    mvn_command = [
        mvn_path,
       "-f", pom_path, 
        "dependency:tree",
        "-DoutputFile=" + output_file,
        "-DappendOutput"
        ]

    try:
        subprocess.run(mvn_command, check=True, shell=True)
        print("Maven dependency tree command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")
    except FileNotFoundError:
        print("Maven executable not found. Please check the path.")

if __name__ == "__main__":
    output_pom_tree(mvn_path, output_file)