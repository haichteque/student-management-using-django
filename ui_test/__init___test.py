import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

BASE_URL = "http://127.0.0.1:8000/"
LOGIN_URL_PATH = "accounts/login/"

ADMIN_USER = {"email": "qasim@admin.com", "password": "admin"}
STAFF_USER = {"email": "bill@ms.com", "password": "123"}
STUDENT_USER = {"email": "qasim@nu.edu.pk", "password": "123"}

@pytest.fixture(scope="session")
def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)

    yield driver
    driver.quit()

@pytest.fixture
def driver_for_test(setup_driver):
    driver = setup_driver
    driver.delete_all_cookies()
    yield driver

def login_user(driver, email, password):
    driver.get(f"{BASE_URL}{LOGIN_URL_PATH}")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    email_field = driver.find_element(By.NAME, "email")
    password_field = driver.find_element(By.NAME, "password")
    submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")

    email_field.send_keys(email)
    password_field.send_keys(password)
    submit_button.click()

    WebDriverWait(driver, 10).until(
        EC.url_changes(f"{BASE_URL}{LOGIN_URL_PATH}")
    )

def logout_user(driver):
    try:
        logout_link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
        )
        logout_link.click()
        WebDriverWait(driver, 10).until(
            EC.url_to_be(f"{BASE_URL}{LOGIN_URL_PATH}")
        )
    except:
        driver.get(f"{BASE_URL}{LOGIN_URL_PATH}")

class TestUserAuthentication:
    @pytest.mark.parametrize("user_data, expected_title_part, expected_url_path_part", [
        (ADMIN_USER, "Dashboard", "dashboard/"),
        (STAFF_USER, "Staff Panel", "staff/"),
        (STUDENT_USER, "Student Portal", "student/"),
    ])
    def test_successful_login_and_redirect(self, driver_for_test, user_data, expected_title_part, expected_url_path_part):
        login_user(driver_for_test, user_data["email"], user_data["password"])

        WebDriverWait(driver_for_test, 10).until(
            EC.url_contains(f"{BASE_URL}{expected_url_path_part}")
        )
        assert expected_url_path_part in driver_for_test.current_url
        assert expected_title_part in driver_for_test.title

        assert WebDriverWait(driver_for_test, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
        )

        logout_user(driver_for_test)

    def test_invalid_login_credentials(self, driver_for_test):
        driver_for_test.get(f"{BASE_URL}{LOGIN_URL_PATH}")

        WebDriverWait(driver_for_test, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_field = driver_for_test.find_element(By.NAME, "email")
        password_field = driver_for_test.find_element(By.NAME, "password")
        submit_button = driver_for_test.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")

        email_field.send_keys("invalid@user.com")
        password_field.send_keys("wrongpass")
        submit_button.click()

        WebDriverWait(driver_for_test, 10).until(
            EC.url_contains(f"{BASE_URL}{LOGIN_URL_PATH}")
        )
        assert f"{BASE_URL}{LOGIN_URL_PATH}" in driver_for_test.current_url
        error_message = WebDriverWait(driver_for_test, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".errorlist li, .alert-danger, .message-error"))
        )
        assert error_message.is_displayed()
        assert "Please enter a correct email and password" in error_message.text or \
               "Incorrect credentials" in error_message.text


class TestAdminFunctionality:
    def test_admin_access_admin_panel(self, driver_for_test):
        login_user(driver_for_test, ADMIN_USER["email"], ADMIN_USER["password"])
        driver_for_test.get(f"{BASE_URL}admin/")

        WebDriverWait(driver_for_test, 10).until(
            EC.title_contains("Django administration")
        )
        assert "Django administration" in driver_for_test.title
        assert f"{BASE_URL}admin/" in driver_for_test.current_url
        assert "Site administration" in driver_for_test.page_source

        logout_user(driver_for_test)

    def test_admin_can_add_new_item_example(self, driver_for_test):
        login_user(driver_for_test, ADMIN_USER["email"], ADMIN_USER["password"])
        driver_for_test.get(f"{BASE_URL}admin/your_app/your_model/add/")

        # Placeholder: Add actual code to fill and submit a form
        # WebDriverWait(driver_for_test, 10).until(EC.presence_of_element_located((By.ID, "id_name")))
        # driver_for_test.find_element(By.ID, "id_name").send_keys("New Test Item")
        # driver_for_test.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Save']").click()
        # WebDriverWait(driver_for_test, 10).until(EC.url_contains("changelist"))
        # assert "successfully" in driver_for_test.page_source

        print("Admin 'add item' test placeholder executed. Replace with actual functionality tests.")
        logout_user(driver_for_test)

    def test_non_admin_cannot_access_admin_panel(self, driver_for_test):
        login_user(driver_for_test, STAFF_USER["email"], STAFF_USER["password"])
        driver_for_test.get(f"{BASE_URL}admin/")

        WebDriverWait(driver_for_test, 10).until(
            lambda driver: "Forbidden" in driver.title or \
                           "Login" in driver.title or \
                           f"{BASE_URL}admin/login/" in driver.current_url
        )
        assert "Forbidden" in driver_for_test.title or \
               "Login" in driver_for_test.title or \
               f"{BASE_URL}admin/login/" in driver_for_test.current_url or \
               f"{BASE_URL}{LOGIN_URL_PATH}" in driver_for_test.current_url

        logout_user(driver_for_test)


class TestStaffFunctionality:
    def test_staff_access_staff_dashboard(self, driver_for_test):
        login_user(driver_for_test, STAFF_USER["email"], STAFF_USER["password"])
        driver_for_test.get(f"{BASE_URL}staff/")

        WebDriverWait(driver_for_test, 10).until(
            EC.title_contains("Staff Panel")
        )
        assert "Staff Panel" in driver_for_test.title
        assert f"{BASE_URL}staff/" in driver_for_test.current_url

        logout_user(driver_for_test)

    def test_staff_cannot_access_admin_panel_duplicate(self, driver_for_test):
        login_user(driver_for_test, STAFF_USER["email"], STAFF_USER["password"])
        driver_for_test.get(f"{BASE_URL}admin/")

        WebDriverWait(driver_for_test, 10).until(
            lambda driver: "Forbidden" in driver.title or \
                           "Login" in driver.title or \
                           f"{BASE_URL}admin/login/" in driver.current_url
        )
        assert "Forbidden" in driver_for_test.title or \
               "Login" in driver_for_test.title or \
               f"{BASE_URL}admin/login/" in driver_for_test.current_url or \
               f"{BASE_URL}{LOGIN_URL_PATH}" in driver_for_test.current_url

        logout_user(driver_for_test)


class TestStudentFunctionality:
    def test_student_access_student_portal(self, driver_for_test):
        login_user(driver_for_test, STUDENT_USER["email"], STUDENT_USER["password"])
        driver_for_test.get(f"{BASE_URL}student/")

        WebDriverWait(driver_for_test, 10).until(
            EC.title_contains("Student Portal")
        )
        assert "Student Portal" in driver_for_test.title
        assert f"{BASE_URL}student/" in driver_for_test.current_url

        logout_user(driver_for_test)

    def test_student_cannot_access_staff_dashboard(self, driver_for_test):
        login_user(driver_for_test, STUDENT_USER["email"], STUDENT_USER["password"])
        driver_for_test.get(f"{BASE_URL}staff/")

        WebDriverWait(driver_for_test, 10).until(
            lambda driver: f"{BASE_URL}student/" in driver.current_url or \
                           f"{BASE_URL}{LOGIN_URL_PATH}" in driver.current_url or \
                           "Forbidden" in driver.title
        )
        assert f"{BASE_URL}student/" in driver_for_test.current_url or \
               f"{BASE_URL}{LOGIN_URL_PATH}" in driver_for_test.current_url or \
               "Forbidden" in driver_for_test.title
        assert f"{BASE_URL}staff/" not in driver_for_test.current_url

        logout_user(driver_for_test)