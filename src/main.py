import os
import argparse
from global_parameters import *
from git_util import partial_clone, analyze_history
from db_util import create_db

def main():
    if platform.system() == "Windows":
        print("Windows is not supported by this program")
        return -1

    args = handle_command_line_arguments()

    repo_url = args.git if args.git else default_repo_url   # TODO change to throw error for final release
    commit_limit = args.limit if args.limit else default_commit_limit
    
    os.chdir(script_dir)
    try:
        partial_clone(repo_url, clone_dir)
        analyze_history(mvn_path, clone_dir, commit_limit)
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

if __name__ == "__main__":
    main()
