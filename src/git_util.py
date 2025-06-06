from datetime import datetime
from dateutil import parser
import pytz # timezones
from mvn_util import *
from global_parameters import *

def run_command(command, cwd=None):
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def partial_clone(repo_url, clone_dir):
    """Sparsely clones metadata of a git repository.
    This fetches only the repository’s tree structure (no file blobs except for top-level files),
    allowing us to later pull down just the files we actually need.

    @param repo_url: URL of git repository
    @param clone_dir: folder to clone to
    """
    clone_cmd = [
        "git", "clone", "--filter=blob:none", "--sparse",
        repo_url, clone_dir
    ]
    run_command(clone_cmd)

def get_pom_directories(clone_dir, commit_hash='HEAD'):
    ls_output = run_command(["git", "ls-tree", "-r", commit_hash, "--name-only"], cwd=clone_dir) # list all files in the current Git repository
    pom_dirs = set()
    for line in ls_output.splitlines():
        if line.endswith("pom.xml"):
            directory = os.path.dirname(line)
            if directory:
                pom_dirs.add(directory)
            else:
                pom_dirs.add(".")
    return list(pom_dirs)

def sparse_checkout_set(clone_dir, paths):
    run_command(["git", "sparse-checkout", "init", "--cone"], cwd=clone_dir)
    cmd = ["git", "sparse-checkout", "set"] + paths
    run_command(cmd, cwd=clone_dir)

def get_pom_commits(clone_dir):
    pom_paths = get_pom_directories(clone_dir)
    pom_files = [os.path.join(path, "pom.xml") if path != "." else "pom.xml" for path in pom_paths]
    if not pom_files:
        return []

    # save commits in a dict{hash, timestamp} with the timestamp format YYYY-MM-DD hh:mm:ss timezone
    # output has the format "4f5e6a1234567890abcdef1234567890abcdef12|2024-06-01 14:23:45 +0200"
    cmd = ["git", "log", "--all", "--pretty=format:%H|%ci", "--"] + pom_files
    output = run_command(cmd, cwd=clone_dir)
    commits = []
    for line in output.strip().splitlines():
        commit_hash, timestamp = line.split("|", 1)
        commits.append({
            "hash": commit_hash.strip(),
            "timestamp": timestamp.strip()
        })

    return commits

def analyze_history(mvn_path, clone_dir, commit_limit, start, end):
    """Analyze the dependecy tree of all commits where a pom.xml was changed
    For every commit a text file is created in pom_dirs.
    The first line of the file is the timestamp of the commit.

    @param mvn_path: path to mvn
    @param clone_dir: directory where repository got cloned to
    @param commit_limit: limits analyzation to last x commits
    @param start: First date of commit to be considered
    @param end: Last date of commit to be considered
    """
        
    output_directory = os.path.join(script_dir, output_dir)
    os.makedirs(output_directory, exist_ok=True)

    commits = get_pom_commits(clone_dir)

    for commit in commits[:commit_limit]:
        # skip commit if outside date range
        if(not is_commit_in_date_range(start, end, commit["timestamp"])):
            continue
        try:
            run_command(["git", "checkout", "--force", commit["hash"]], cwd=clone_dir)
            pom_dirs = get_pom_directories(clone_dir, commit["hash"])

            if not pom_dirs:
                continue

            sparse_checkout_set(clone_dir, pom_dirs)

            root_pom = os.path.join(clone_dir, "pom.xml")
            if os.path.exists(root_pom):
                output_pom_tree(mvn_path, output_directory, commit["hash"], commit["timestamp"], clone_dir)
            else:
                for pom_dir in pom_dirs:
                    full_path = os.path.join(clone_dir, pom_dir)
                    output_pom_tree(mvn_path, output_directory, commit["hash"], commit["timestamp"], full_path)

        except subprocess.CalledProcessError as e:
            print(f"Skipping commit {commit["hash"]}: {e.stderr}")

def is_commit_in_date_range(start, end, commit):
    """Check if date of commit is between start and end inclusive

    @param start: Start date in form YYYY-MM-DD
    @param end: End date in form YYYY-MM-DD
    @param commit: Date of Commit in form YYYY-MM-DD hh:mm:ss timezone
    """
    # Skip if no start or end date specified
    if not start and not end:
        return True

    start_obj = None
    end_obj = None

    # Parse user entered dates
    if start:
        start_obj = datetime.strptime(start, "%Y-%m-%d").date()
    if end:
        end_obj = datetime.strptime(end, "%Y-%m-%d").date()

    # Parse timezone sensitive commit timestamp
    commit_obj = parser.parse(commit)
    commit_obj = commit_obj.astimezone(pytz.UTC).date()

    # If both start and end are provided, check if commit is in range
    if start_obj and end_obj:
        return start_obj <= commit_obj <= end_obj
    # If only start is provided, check if commit is after start
    elif start_obj:
        return commit_obj >= start_obj
    # If only end is provided, check if commit is before end
    elif end_obj:
        return commit_obj <= end_obj
    

# Folgendes nur zum Testen von den spezifischen Funktionen hier drin
# Will, dass spaeter hier einfach die git funktionen sind und im main script einfach mit den Funktionen hier gepullt wird 
# und dann mit "mvn dependency:tree" subprocess call die text datei und dann DB eintraege gemacht werden. Allerdings not sure wie die commit history danach genutzt wird
if __name__ == "__main__":
    # # Change the current working directory to the directory of the Python script
    os.chdir(script_dir)
    #
    # # Idee hinter partial clone und sparse checkout ist es, dass wir vorerst durch den blob filter nur Ordnerstruktur herunterladen und KEINE dateiinhalte bis diese benoetigt werden
    # # sparse_checkout_set ist dann eben fuer das holen der benoetigten pom.xml dateien
    # # Zum Verifizieren "git ls-tree -r HEAD". alles andere sorgt dann dafuer, dass die datei benoetigt wird und gefetcht wuerde
    # partial_clone(repo_url, clone_dir)
    # pom_paths = get_pom_directories(clone_dir)
    # sparse_checkout_set(clone_dir, pom_paths)

# Test date function
    # start_date = "2025"
    # end_date = ""
    # commit_timestamp = "2025-05-30 22:23:45 +0200"

    # if is_commit_in_date_range(start_date, end_date, commit_timestamp):
    #     print("The commit is within the date range.")
    # else:
    #     print("The commit is outside the date range.")