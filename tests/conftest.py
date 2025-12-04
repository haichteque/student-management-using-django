import os
import django
from django.conf import settings

def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
    os.environ.setdefault('MY_SECRET_KEY', 'test_secret_key')
    try:
        django.setup()
    except Exception:
        pass

import pytest
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

@pytest.fixture
def request_factory():
    return RequestFactory()

@pytest.fixture
def mock_request(request_factory):
    request = request_factory.get('/')
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    return request

