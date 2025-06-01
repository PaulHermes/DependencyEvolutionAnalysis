import os


## constant parameters
# directory to store cloned repository
clone_dir = "cloned_repository"

# path to working directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# path to mvn
mvn_path = "mvn"

## variable / temporary parameters
# URL of github repository to clone
# repo_url = "https://github.com/andyglick/maven-multi-level-modules-project.git"
default_repo_url = "https://github.com/apache/commons-lang"
repo_url = None # set in main

# path to output file
output_file = os.path.abspath( os.path.join( script_dir, "maven_dependencies.txt" ) )

output_dir = "dependency_history"

# path to the h2.jar and the .db file
h2_jar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "h2-2.3.232.jar")
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dependency_analysis")

# get repo name from url
repo_name = None # set in main set_repo_name()

# path to .gexf file used for gephi
gephi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dependency_graph.gexf")

# test parameters
default_commit_limit = None # set in main