import os
import sys
from pathlib import Path

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set test defaults so Settings() doesn't fail when .env is not in CWD
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("ALLOWED_HOSTS", "localhost")
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")
