import os
from src.utils.env_var_loader import env_var_loader
import sys

# load env vars
env_var_loader("tests/.env")

# load path to get python files
sys.path.append(os.path.join(os.getcwd(), "src"))

# load sa if applicable
if os.environ.get("SA_JSON"):
    file_name = "sa.json"
    with open(file_name, "w") as f:
        f.write(os.environ.get("SA_JSON", "{}"))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = file_name
