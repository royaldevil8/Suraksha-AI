from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "app" / "data"
REPORTS_FILE = DATA_DIR / "reports.json"

RESOURCE_INVENTORY = [
    {"resource_id": "AMB-01", "type": "ambulance", "count": 3},
    {"resource_id": "RES-01", "type": "rescue_team", "count": 4},
    {"resource_id": "BOAT-01", "type": "boat", "count": 2},
    {"resource_id": "MED-01", "type": "medical_kit", "count": 20},
    {"resource_id": "SHELTER-01", "type": "shelter_space", "count": 100},
]
