import sys
import os
from datetime import datetime

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from app import app
from services.analytics_service import analytics_service

with app.app_context():
    stats = analytics_service.get_dashboard_stats()
    print('Dashboard stats:')
    for k, v in stats.items():
        print(f'  {k}: {v}')
