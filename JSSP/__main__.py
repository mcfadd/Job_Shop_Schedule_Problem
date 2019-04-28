import sys
import os

# change path to include JSSP
path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, path)

from JSSP.main import command_line_interface

if __name__ == '__main__':
    sys.exit(command_line_interface())
