import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class TestDjangoApp(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000/"
    LOGIN_PAGE_URL = BASE_URL

    ADMIN_CREDENTIALS = {"email": "qasim@admin.com", "password": "admin"}
    STAFF_CREDENTIALS = {"email": "bill@ms.com", "password": "123"}
    STUDENT_CREDENTIALS = {"email": "qasim@nu.edu.pk", "password": "123"}

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(10)
        self.wait = WebDriverWait(self.driver, 5)

    def tearDown(self):
        self.driver.quit()

    def _login(self, email, password):
        self.driver.get(self.LOGIN_PAGE_URL)
        try:
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "email")))
            password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
            login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form input[type='submit']")))
        except TimeoutException:
            self.fail("Login page elements (email, password, submit button) not found. Ensure Django server is running and the login form HTML has 'name=\"email\"', 'name=\"password\"', and a submit button within a form.")

        email_field.send_keys(email)
        password_field.send_keys(password)
        login_button.click()

    def _logout(self):
        self.driver.get(self.BASE_URL + "logout/")
        self.wait.until(EC.url_to_be(self.LOGIN_PAGE_URL))

    def test_admin_login_success(self):
        self._login(self.ADMIN_CREDENTIALS["email"], self.ADMIN_CREDENTIALS["password"])
        expected_url = self.BASE_URL + "admin_home/"
        self.wait.until(EC.url_to_be(expected_url))
        self.assertEqual(self.driver.current_url, expected_url, "Admin login did not redirect to admin home.")
        # Optional: Verify content specific to admin dashboard if known (e.g., "Admin Dashboard" in body)
        self._logout()

    def test_staff_login_success(self):
        self._login(self.STAFF_CREDENTIALS["email"], self.STAFF_CREDENTIALS["password"])
        expected_url = self.BASE_URL + "staff_home/"
        self.wait.until(EC.url_to_be(expected_url))
        self.assertEqual(self.driver.current_url, expected_url, "Staff login did not redirect to staff home.")
        # Optional: Verify content specific to staff dashboard
        self._logout()

    def test_student_login_success(self):
        self._login(self.STUDENT_CREDENTIALS["email"], self.STUDENT_CREDENTIALS["password"])
        expected_url = self.BASE_URL + "student_home/"
        self.wait.until(EC.url_to_be(expected_url))
        self.assertEqual(self.driver.current_url, expected_url, "Student login did not redirect to student home.")
        # Optional: Verify content specific to student dashboard
        self._logout()

    def test_invalid_login_credentials(self):
        self._login("wrong@example.com", "wrongpassword")
        self.wait.until(EC.url_to_be(self.LOGIN_PAGE_URL))
        self.assertEqual(self.driver.current_url, self.LOGIN_PAGE_URL, "Invalid login redirected away from login page.")
        
        try:
            # Assuming Django's messages framework renders errors in a ul.messages li or similar
            error_message_element = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".messages li")))
            self.assertIn("Invalid details", error_message_element.text, "Error message 'Invalid details' not found.")
        except TimeoutException:
            self.fail("Error message element '.messages li' not found after invalid login. Check your Django template for message display.")
        except NoSuchElementException:
            self.fail("Error message element '.messages li' not found after invalid login. Check your Django template for message display.")

    def test_logout_functionality(self):
        self._login(self.ADMIN_CREDENTIALS["email"], self.ADMIN_CREDENTIALS["password"])
        self.wait.until(EC.url_to_be(self.BASE_URL + "admin_home/"))
        self._logout()
        self.assertEqual(self.driver.current_url, self.LOGIN_PAGE_URL, "Logout did not redirect to login page.")

if __name__ == "__main__":
    unittest.main(verbosity=2)