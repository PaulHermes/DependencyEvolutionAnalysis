import os
import platform
## constant parameters
# directory to store cloned repository
clone_dir = "cloned_repository"

# path to working directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# path to mvn cli
#mvn_path = "mvn.cmd"
# TODO Change to relative path
if platform.system() == "Windows":
    mvn_path = r"F:\[21] Master\[P50] Projektarbeit 1\apache-maven-3.9.9\bin\mvn.cmd"
else:
    mvn_path = "mvn"

## variable / temporary parameters
# URL of github repository to clone
repo_url = "https://github.com/andyglick/maven-multi-level-modules-project.git"

# path to output file
output_file = os.path.abspath( os.path.join( script_dir, "maven_dependencies.txt" ) )