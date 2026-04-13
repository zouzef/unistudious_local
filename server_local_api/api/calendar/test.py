import sys
import os

# ✅ Add the parent directory (server_local_api/) to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database import Database  # ✅ now works
from api.calendar.routes.calendar_bp import test_special_group  # adjust if needed

result = test_special_group(1997)
print(f"Result: {result}")