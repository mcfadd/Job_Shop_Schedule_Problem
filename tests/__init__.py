import os
import tempfile

# directories used by tests
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmp_dir = tempfile.mkdtemp()


def get_all_fjs_files():
    """
    Gets a list of all the absolute file paths of all the .fjs files in the data directory.

    :returns: A list of all the absolute file paths of all the .fjs files
    """
    path_to_fjs_files = project_root + os.sep + 'data' + os.sep + 'fjs_data'
    result = []
    for dirpath, dirs, files in os.walk(path_to_fjs_files):
        for filename in files:
            fname = os.path.join(dirpath, filename)
            if fname.endswith('.fjs'):
                result.append(fname)

    return result
