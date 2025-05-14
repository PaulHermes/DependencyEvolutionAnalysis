import os
from global_parameters import *
from git_util import partial_clone, analyze_history
from db_util import create_db

def main():
    os.chdir(script_dir)
    try:
        partial_clone(repo_url, clone_dir)
        analyze_history(mvn_path, clone_dir)
        create_db()
    except Exception as e:
        print(f"\n Error occurred: {str(e)}")


if __name__ == "__main__":
    main()