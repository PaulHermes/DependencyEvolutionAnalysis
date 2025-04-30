import subprocess
import os
from global_parameters import *

def output_pom_tree(mvn_path: str, output_dir: str, commit_hash: str, project_dir: str):
    output_file = os.path.join(output_dir, f"{commit_hash}.txt")
    mvn_command = [
        mvn_path,
        "-f", project_dir,
        "dependency:tree",
        "-DoutputFile=" + output_file,
        "-DappendOutput"]

    try:
        subprocess.run(mvn_command, check=True, shell=True)
        print("Maven dependency tree command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")
    except FileNotFoundError:
        print("Maven executable not found. Please check the path.")

if __name__ == "__main__":
    output_pom_tree(mvn_path, output_file)