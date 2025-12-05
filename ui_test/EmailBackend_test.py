import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DjangoEmailBackendLoginTest(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000"
    LOGIN_URL_GENERIC = f"{BASE_URL}/accounts/login/"
    LOGIN_URL_ADMIN = f"{BASE_URL}/admin/login/"

    ADMIN_USER = {"email": "qasim@admin.com", "password": "admin"}
    STAFF_USER = {"email": "bill@ms.com", "password": "123"}
    STUDENT_USER = {"email": "qasim@nu.edu.pk", "password": "123"}

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5) # Set a reasonable implicit wait

    def tearDown(self):
        self.driver.quit()

    def _login(self, email, password, login_url):
        self.driver.get(login_url)
        
        # Try finding the email/username field by common Django IDs/names
        email_field_locator = None
        for by_type, selector in [(By.ID, "id_username"), (By.NAME, "username"), (By.ID, "id_email")]:
            try:
                email_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((by_type, selector))
                )
                email_field_locator = (by_type, selector)
                break
            except:
                continue
        
        if not email_field_locator:
            raise Exception("Could not find email/username input field by id_username, username, or id_email.")

        email_field = self.driver.find_element(*email_field_locator)
        
        password_field = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "id_password"))
        )
        
        # Find the submit button, robustly
        submit_button = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='submit'], button[type='submit']"))
        )

        email_field.send_keys(email)
        password_field.send_keys(password)
        submit_button.click()

    def test_admin_successful_login(self):
        self._login(self.ADMIN_USER["email"], self.ADMIN_USER["password"], self.LOGIN_URL_ADMIN)
        
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/admin/")
        )
        self.assertIn("/admin/", self.driver.current_url, "Admin login failed: Not redirected to /admin/")
        
        admin_header = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "user-tools"))
        )
        self.assertIsNotNone(admin_header, "Admin successful login: 'user-tools' element not found, indicating login failure.")

    def test_staff_successful_login(self):
        self._login(self.STAFF_USER["email"], self.STAFF_USER["password"], self.LOGIN_URL_GENERIC)
        
        WebDriverWait(self.driver, 10).until(
            EC.url_changes(self.LOGIN_URL_GENERIC)
        )
        self.assertNotIn("/accounts/login/", self.driver.current_url, "Staff login failed: Still on login page.")
        
        logout_link = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Logout"))
        )
        self.assertIsNotNone(logout_link, "Staff successful login: 'Logout' link not found, indicating login failure.")

    def test_student_successful_login(self):
        self._login(self.STUDENT_USER["email"], self.STUDENT_USER["password"], self.LOGIN_URL_GENERIC)
        
        WebDriverWait(self.driver, 10).until(
            EC.url_changes(self.LOGIN_URL_GENERIC)
        )
        self.assertNotIn("/accounts/login/", self.driver.current_url, "Student login failed: Still on login page.")
        
        logout_link = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Logout"))
        )
        self.assertIsNotNone(logout_link, "Student successful login: 'Logout' link not found, indicating login failure.")

    def test_admin_invalid_password(self):
        self._login(self.ADMIN_USER["email"], "wrong_admin_pass", self.LOGIN_URL_ADMIN)
        
        self.assertIn("/admin/login/", self.driver.current_url, "Admin invalid password: Not on admin login page after failed attempt.")
        
        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".errornote, .errorlist li"))
        )
        self.assertIn("Please enter a correct", error_message.text)
        self.assertIn("username and password", error_message.text)

    def test_staff_invalid_email(self):
        self._login("nonexistent@ms.com", self.STAFF_USER["password"], self.LOGIN_URL_GENERIC)
        
        self.assertIn("/accounts/login/", self.driver.current_url, "Staff invalid email: Not on generic login page after failed attempt.")
        
        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".errorlist li, .alert-danger"))
        )
        self.assertIn("Please enter a correct", error_message.text)
        self.assertIn("username and password", error_message.text)

    def test_student_invalid_password(self):
        self._login(self.STUDENT_USER["email"], "wrong_student_pass", self.LOGIN_URL_GENERIC)
        
        self.assertIn("/accounts/login/", self.driver.current_url, "Student invalid password: Not on generic login page after failed attempt.")
        
        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".errorlist li, .alert-danger"))
        )
        self.assertIn("Please enter a correct", error_message.text)
        self.assertIn("username and password", error_message.text)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)