import sys
import os
from pathlib import Path

def fix_path():
    try:
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
        project_root_str = str(project_root)
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)
    except NameError:
        cwd = Path(os.getcwd()).resolve()
        if str(cwd) not in sys.path:
            sys.path.insert(0, str(cwd))

