import subprocess
import pathlib
import sys
import os




if __name__ == "__main__":
    if len(sys.argv) == 2:
        head_worktree = pathlib.Path("./.head")

        _command, file = sys.argv

        image_path = pathlib.Path(file)
        original_image_path = head_worktree / pathlib.Path(file)
        diff_path = (pathlib.Path("diffs") / pathlib.Path(file))

        p = subprocess.Popen(["git", "pull", "origin", "HEAD"], cwd=head_worktree)
        p.wait()
        print(diff_path.parent)
        if not diff_path.parent.exists():
            print(f"Creating {diff_path.parent}")
            os.makedirs(diff_path.parent)

        p = subprocess.Popen(["uprightdiff", image_path, original_image_path,
                              diff_path.absolute()])
        p.wait()
        print(p.returncode)
        print(f"Wrote diff to {diff_path}")





    else:
        print("Must provide exaclty one argument")
