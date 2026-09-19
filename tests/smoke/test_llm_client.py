# Generally we will not face import issue since we have used hatchling.build in our pyproject.toml and specifically
# mentioned src/toolcalling_proj as the package path.
# However, if we face any import issue, uncomment the below lines to add package path to sys.path!

# import sys
# from pathlib import Path

# Resolve project root: tests/smoke/test_file.py -> parents[2]
# PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 1. If toolcalling_proj is directly inside the project root:
# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT))

# 2. UNCOMMENT below instead if you use a src/ layout (e.g., src/toolcalling_proj):
# SRC_DIR = PROJECT_ROOT / "src"
# if str(SRC_DIR) not in sys.path:
#     sys.path.insert(0, str(SRC_DIR))

from toolcalling_proj.llm_client import get_llm

llm = get_llm()

query = "What is equation of ideal gas?"

response = llm.invoke(query)

print(response.content)