import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000/"
ADMIN_CREDENTIALS = {"email": "qasim@admin.com", "password": "admin"}
STAFF_CREDENTIALS = {"email": "bill@ms.com", "password": "123"}
STUDENT_CREDENTIALS = {"email": "qasim@nu.edu.pk", "password": "123"}

# !!! IMPORTANT !!!
# Replace "your_app_name" with the actual name of your Django app
# where the models (CustomUser, Staff, Student, etc.) are defined.
# For example, if your models are in 'myproject/enrollment/models.py',
# then APP_NAME should be 'enrollment'.
APP_NAME = "your_app_name" 

# List of models registered in admin.py to verify access for admin user
REGISTERED_MODELS = [
    "customuser",
    "staff",
    "student",
    "course",
    "subject",
    "session",
]

# --- Pytest Fixture for WebDriver Setup ---
@pytest.fixture(scope="module")
def driver():
    """Sets up a headless Chrome WebDriver for the entire test module."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Use ChromeDriverManager to automatically handle driver download and setup
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10) # Implicit wait for elements to appear
    yield driver
    driver.quit()

# --- Helper Functions for Login/Logout ---

def _login(driver, email, password):
    """Logs a user into the Django admin interface."""
    driver.get(f"{BASE_URL}admin/login/?next=/admin/")
    
    try:
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
    except:
        # If already logged in or on a different page unexpectedly, try to log out first
        driver.get(f"{BASE_URL}admin/logout/")
        time.sleep(1)
        driver.get(f"{BASE_URL}admin/login/?next=/admin/")
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")

    username_field.send_keys(email)
    password_field.send_keys(password)
    
    password_field.send_keys(Keys.RETURN)
    time.sleep(1.5) # Give a moment for redirection/page load

def _logout(driver):
    """Logs out the current user from the Django admin interface."""
    driver.get(f"{BASE_URL}admin/logout/")
    time.sleep(1.5) # Give a moment for logout to complete and page to load
    # Ensure we are on the logout confirmation page or redirected to login
    assert "Log out" in driver.page_source or "Login" in driver.page_source or f"{BASE_URL}admin/login/" in driver.current_url

# --- Test Cases ---

class TestAdminPanelAccess:

    def test_admin_user_access(self, driver):
        """
        Tests if an admin user can log in to the Django admin and access all registered models.
        """
        _login(driver, ADMIN_CREDENTIALS["email"], ADMIN_CREDENTIALS["password"])
        
        # Verify successful login
        assert "Site administration" in driver.page_source
        assert f"Welcome, {ADMIN_CREDENTIALS['email']}." in driver.page_source
        
        # Verify access to each registered model's change list page
        for model in REGISTERED_MODELS:
            model_url = f"{BASE_URL}admin/{APP_NAME}/{model}/"
            driver.get(model_url)
            time.sleep(1) # Small wait for page content to load
            
            # Check if the page title or content indicates successful access to the model list
            # Common page titles for change list: "Select [Model Name]", "[Model Name]s"
            # And also checking if the URL is correct
            assert model_url == driver.current_url 
            assert f"Select {model.replace('_', ' ').title()}" in driver.page_source or \
                   f"{model.replace('_', ' ').title()}s" in driver.page_source or \
                   f"Add {model.replace('_', ' ').title()}" in driver.page_source
            
        _logout(driver)
        assert f"{BASE_URL}admin/login/" in driver.current_url

    def test_staff_user_access(self, driver):
        """
        Tests if a staff user can log in to the Django admin.
        (Staff users may have limited access based on permissions, but should be able to log in).
        """
        _login(driver, STAFF_CREDENTIALS["email"], STAFF_CREDENTIALS["password"])
        
        # Verify successful login (should see admin index, even if empty or limited)
        assert "Site administration" in driver.page_source
        assert f"Welcome, {STAFF_CREDENTIALS['email']}." in driver.page_source
        
        # Staff users might not have access to all models by default.
        # This test only verifies successful login and presence of admin header.
        # Further tests would be needed to check specific staff permissions.
        
        _logout(driver)
        assert f"{BASE_URL}admin/login/" in driver.current_url

    def test_student_user_access(self, driver):
        """
        Tests if a student user (who should not have staff status) is denied access
        to the Django admin interface.
        """
        _login(driver, STUDENT_CREDENTIALS["email"], STUDENT_CREDENTIALS["password"])
        
        # Verify login failure
        # Should remain on the login page or see an error message
        assert "Please enter a correct username and password" in driver.page_source or \
               f"{BASE_URL}admin/login/" in driver.current_url
        
        # Ensure that "Site administration" (which appears after successful login) is NOT present
        assert "Site administration" not in driver.page_source
        assert f"Welcome, {STUDENT_CREDENTIALS['email']}." not in driver.page_source

        # No explicit logout needed as login failed, but we navigate away just in case
        driver.get(BASE_URL)
        time.sleep(0.5)

# --- How to Run These Tests ---
# 1. Save this code as a Python file (e.g., test_django_admin.py).
# 2. Make sure you have pytest, selenium, and webdriver-manager installed:
#    pip install pytest selenium webdriver-manager
# 3. IMPORTANT: Replace "your_app_name" at the top of this file
#    with the actual name of your Django app where the models
#    (CustomUser, Staff, Student, Course, Subject, Session) are defined.
#    Example: If your project structure is `myproject/users/models.py`,
#    then APP_NAME should be "users".
# 4. Ensure your Django development server is running at http://127.0.0.1:8000/
# 5. Run pytest from your terminal in the same directory as the test file:
#    pytest test_django_admin.py