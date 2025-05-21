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

    cmd = ["git", "log", "--all", "--pretty=format:%H", "--"] + pom_files
    output = run_command(cmd, cwd=clone_dir)
    return list(dict.fromkeys(output.splitlines()))


def analyze_history(mvn_path, clone_dir):
    output_directory = os.path.join(script_dir, output_dir)
    os.makedirs(output_directory, exist_ok=True)

    commits = get_pom_commits(clone_dir)

    for commit in commits[:100]:
        try:
            run_command(["git", "checkout", "--force", commit], cwd=clone_dir)
            pom_dirs = get_pom_directories(clone_dir, commit)

            if not pom_dirs:
                continue

            sparse_checkout_set(clone_dir, pom_dirs)

            root_pom = os.path.join(clone_dir, "pom.xml")
            if os.path.exists(root_pom):
                output_pom_tree(mvn_path, output_directory, commit, clone_dir)
            else:
                for pom_dir in pom_dirs:
                    full_path = os.path.join(clone_dir, pom_dir)
                    output_pom_tree(mvn_path, output_directory, commit, full_path)

        except subprocess.CalledProcessError as e:
            print(f"Skipping commit {commit}: {e.stderr}")

# Folgendes nur zum Testen von den spezifischen Funktionen hier drin
# Will, dass spaeter hier einfach die git funktionen sind und im main script einfach mit den Funktionen hier gepullt wird 
# und dann mit "mvn dependency:tree" subprocess call die text datei und dann DB eintraege gemacht werden. Allerdings not sure wie die commit history danach genutzt wird
if __name__ == "__main__":
    # Change the current working directory to the directory of the Python script
    os.chdir(script_dir)
    
    # Idee hinter partial clone und sparse checkout ist es, dass wir vorerst durch den blob filter nur Ordnerstruktur herunterladen und KEINE dateiinhalte bis diese benoetigt werden
    # sparse_checkout_set ist dann eben fuer das holen der benoetigten pom.xml dateien
    # Zum Verifizieren "git ls-tree -r HEAD". alles andere sorgt dann dafuer, dass die datei benoetigt wird und gefetcht wuerde
    partial_clone(repo_url, clone_dir)
    pom_paths = get_pom_directories(clone_dir)
    sparse_checkout_set(clone_dir, pom_paths)

