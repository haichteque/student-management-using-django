import pytest
from unittest.mock import patch
import main_app.staff_views as views

def test_patching_debug():
    print(f"Original: {views.LeaveReportStaffForm}")
    with patch('main_app.staff_views.LeaveReportStaffForm') as MockForm:
        print(f"Patched: {views.LeaveReportStaffForm}")
        assert views.LeaveReportStaffForm is MockForm
