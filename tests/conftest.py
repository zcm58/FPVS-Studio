import sys
from pathlib import Path

# Ensure project root is available for imports when running tests from nested directories
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
