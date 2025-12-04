import pytest
from django.urls import reverse
from unittest.mock import MagicMock, patch
from main_app.views import *
from main_app.models import *
from django.contrib.messages.storage.fallback import FallbackStorage

pytestmark = pytest.mark.django_db

def test_login_page_get(request_factory):
    url = reverse('login_page')
    request = request_factory.get(url)
    request.user = MagicMock()
    request.user.is_authenticated = False
    response = login_page(request)
    assert response.status_code == 200

def test_login_page_authenticated_admin(request_factory):
    url = reverse('login_page')
    request = request_factory.get(url)
    request.user = MagicMock()
    request.user.is_authenticated = True
    request.user.user_type = '1'
    response = login_page(request)
    assert response.status_code == 302
    assert response.url == reverse('admin_home')

def test_login_page_authenticated_staff(request_factory):
    url = reverse('login_page')
    request = request_factory.get(url)
    request.user = MagicMock()
    request.user.is_authenticated = True
    request.user.user_type = '2'
    response = login_page(request)
    assert response.status_code == 302
    assert response.url == reverse('staff_home')

def test_login_page_authenticated_student(request_factory):
    url = reverse('login_page')
    request = request_factory.get(url)
    request.user = MagicMock()
    request.user.is_authenticated = True
    request.user.user_type = '3'
    response = login_page(request)
    assert response.status_code == 302
    assert response.url == reverse('student_home')

def test_doLogin_get(request_factory):
    url = reverse('user_login')
    request = request_factory.get(url)
    response = doLogin(request)
    assert response.status_code == 200
    assert b'Denied' in response.content

@patch('main_app.views.requests.post')
@patch('main_app.views.EmailBackend.authenticate')
@patch('main_app.views.login')
def test_doLogin_post_success_admin(mock_login, mock_auth, mock_post, request_factory):
    url = reverse('user_login')
    data = {'email': 'admin@test.com', 'password': 'pass', 'g-recaptcha-response': 'token'}
    request = request_factory.post(url, data)
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    mock_response = MagicMock()
    mock_response.text = '{"success": true}'
    mock_post.return_value = mock_response
    
    mock_user = MagicMock()
    mock_user.user_type = '1'
    mock_auth.return_value = mock_user
    
    response = doLogin(request)
    assert response.status_code == 302
    assert response.url == reverse('admin_home')
    mock_login.assert_called_once()

@patch('main_app.views.requests.post')
@patch('main_app.views.EmailBackend.authenticate')
def test_doLogin_post_invalid_captcha(mock_auth, mock_post, request_factory):
    url = reverse('user_login')
    data = {'email': 'admin@test.com', 'password': 'pass', 'g-recaptcha-response': 'token'}
    request = request_factory.post(url, data)
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    mock_response = MagicMock()
    mock_response.text = '{"success": false}'
    mock_post.return_value = mock_response
    
    response = doLogin(request)
    assert response.status_code == 302
    assert response.url == '/'

@patch('main_app.views.requests.post')
@patch('main_app.views.EmailBackend.authenticate')
def test_doLogin_post_invalid_credentials(mock_auth, mock_post, request_factory):
    url = reverse('user_login')
    data = {'email': 'admin@test.com', 'password': 'pass', 'g-recaptcha-response': 'token'}
    request = request_factory.post(url, data)
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    
    mock_response = MagicMock()
    mock_response.text = '{"success": true}'
    mock_post.return_value = mock_response
    
    mock_auth.return_value = None
    
    response = doLogin(request)
    assert response.status_code == 302
    assert response.url == '/'

@patch('main_app.views.logout')
def test_logout_user(mock_logout, request_factory):
    url = reverse('user_logout')
    request = request_factory.get(url)
    request.user = MagicMock()
    response = logout_user(request)
    assert response.status_code == 302
    assert response.url == '/'
    mock_logout.assert_called_once()


@patch('main_app.views.get_object_or_404')
@patch('main_app.views.Attendance.objects.filter')
def test_get_attendance(mock_filter, mock_get, request_factory):
    url = reverse('get_attendance')
    request = request_factory.post(url, {'subject': 1, 'session': 1})
    
    mock_get.return_value = MagicMock()
    
    mock_attd = MagicMock()
    mock_attd.id = 1
    mock_attd.date = '2023-01-01'
    mock_attd.session.id = 1
    mock_filter.return_value = [mock_attd]
    
    response = get_attendance(request)
    assert response.status_code == 200
    assert b'2023-01-01' in response.content
