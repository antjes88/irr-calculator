import os
from dotenv import load_dotenv
import sys

# load env vars
load_dotenv(dotenv_path="tests/.env", override=True)

# load path to get python files
sys.path.append(os.path.join(os.getcwd(), "src"))
