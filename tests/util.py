import tempfile
from pathlib import Path

from JSSP import data, SolutionFactory

project_root = Path(__file__).parent.parent
tmp_dir = Path(tempfile.mkdtemp())

csv_data = data.SpreadsheetData(
            project_root / 'data/given_data/sequenceDependencyMatrix.csv',
            project_root / 'data/given_data/machineRunSpeed.csv',
            project_root / 'data/given_data/jobTasks.csv')

csv_data_solution_factory = SolutionFactory(csv_data)


def path_walk(top, topdown=False, followlinks=False):
    names = list(top.iterdir())

    dirs = (node for node in names if node.is_dir())
    nondirs = (node for node in names if not node.is_dir())

    if topdown:
        yield top, dirs, nondirs

    for name in dirs:
        if followlinks or not name.is_symlink():
            for x in path_walk(name, topdown, followlinks):
                yield x

    if not topdown:
        yield top, dirs, nondirs


def rm_tree(pth):
    pth = Path(pth)
    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()


def get_files_with_suffix(dir_path, suffix):
    """
    Gets a list of file paths under dir_path with suffix equal to suffix parameter.

    :type dir_path: Path | str
    :param dir_path: path to directory to look into

    :type suffix: str
    :param suffix: suffix to look for

    :rtype: list
    :returns: A list of file paths
    """
    dir_path = Path(dir_path)
    result = []
    for dirpath, dirs, files in path_walk(dir_path):
        for filename in files:
            fname = dirpath / filename
            if fname.suffix == suffix:
                result.append(fname)

    return result
