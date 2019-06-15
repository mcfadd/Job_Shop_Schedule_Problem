import os
import tempfile

# directories used by tests
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmp_dir = tempfile.mkdtemp()
