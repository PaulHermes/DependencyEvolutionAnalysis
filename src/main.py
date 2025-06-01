import os
import platform
import argparse
import global_parameters
from urllib.parse import urlparse
from git_util import partial_clone, analyze_history
from db_util import create_db

def main():
    if platform.system() == "Windows":
        print("Windows is not supported by this program")
        return -1

    # Handle command line arguments
    args = handle_command_line_arguments()

    global_parameters.repo_url = args.git if args.git else global_parameters.default_repo_url   # TODO change to throw error for final release
    commit_limit = args.limit if args.limit else global_parameters.default_commit_limit

    set_repo_name(global_parameters.repo_url)   # for database 
    
    # Set working directory
    os.chdir(global_parameters.script_dir)

    # Run main part
    try:
        partial_clone(global_parameters.repo_url, global_parameters.clone_dir)
        analyze_history(global_parameters.mvn_path, global_parameters.clone_dir, commit_limit)
        create_db()
    except Exception as e:
        print(f"\n Error occurred: {str(e)}")

def handle_command_line_arguments():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-g', '--git', type=str, help="Link to github repository")
    parser.add_argument('-l', '--limit', type=int, help="Limit analysis to X newest commits")

    # Ideas for more args:
    # Keep/Delete previously saved repos

    return parser.parse_args()

def set_repo_name(url):
    parsed_url = urlparse(url)
    global_parameters.repo_name = os.path.basename(parsed_url.path).replace(".git", "")

if __name__ == "__main__":
    main()
