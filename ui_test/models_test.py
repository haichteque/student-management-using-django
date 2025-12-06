import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class DjangoAuthTests(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000/"
    # Assuming the login page is at /login/. Adjust if your Django project uses a different URL (e.g., just BASE_URL).
    LOGIN_URL = f"{BASE_URL}login/"

    # Login Credentials
    ADMIN_CREDS = {"email": "qasim@admin.com", "password": "admin"}
    STAFF_CREDS = {"email": "bill@ms.com", "password": "123"}
    STUDENT_CREDS = {"email": "qasim@nu.edu.pk", "password": "123"}

    def setUp(self):
        options = Options()
        options.add_argument("--headless")  # Run Chrome in headless mode
        options.add_argument("--no-sandbox")  # Bypass OS security model, required for some environments
        options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        options.add_argument("--window-size=1920,1080")  # Set a consistent window size
        options.add_argument("--disable-gpu")  # Applicable to Windows OS for older Chrome versions

        # Initialize the Chrome WebDriver using webdriver_manager
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(10)  # Implicitly wait for elements to be available for 10 seconds

    def tearDown(self):
        self.driver.quit()  # Close the browser after each test

    def _login(self, email, password):
        """Helper method to perform login."""
        driver = self.driver
        driver.get(self.LOGIN_URL)

        # Wait for the email and password fields to be present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
        except Exception:
            self.fail(f"Login form elements (email/password) not found at {self.LOGIN_URL}.")

        email_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")

        # Assuming the submit button is inside a form and has type="submit"
        # Adjust locator if your submit button has a different attribute (e.g., id, class)
        submit_button = driver.find_element(By.XPATH, "//form//button[@type='submit']")

        email_input.send_keys(email)
        password_input.send_keys(password)
        submit_button.click()

    def _logout(self):
        """Helper method to perform logout."""
        driver = self.driver
        # Try to find a logout link, common options are 'Logout' text or an ID.
        try:
            logout_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
            )
            logout_link.click()
            # Wait until the URL changes to the login page or contains 'login'
            WebDriverWait(driver, 10).until(
                EC.url_contains("login")
            )
        except Exception:
            # If no "Logout" link found, try navigating directly to a common logout URL
            driver.get(f"{self.BASE_URL}logout/")
            WebDriverWait(driver, 10).until(
                EC.url_contains("login")
            )

        # Verify that we are back on the login page by checking for the login form elements
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        self.assertIn("login", driver.current_url.lower()) # Final check for URL

    def _assert_dashboard_access(self, expected_dashboard_url_part, user_type_name):
        """
        Helper method to assert successful dashboard access for a given user type.
        It first tries to match a specific URL part, then falls back to general
        indicators of a logged-in state if the URL is not predictable.
        """
        driver = self.driver
        try:
            # First, try to assert a specific dashboard URL pattern
            WebDriverWait(driver, 10).until(
                EC.url_contains(expected_dashboard_url_part)
            )
            self.assertIn(expected_dashboard_url_part, driver.current_url)
        except Exception:
            # Fallback: if no specific URL, check for general indicators of successful login
            # like the absence of the login form and presence of some logged-in user element (e.g., Logout link)
            self.assertNotIn("Login", driver.title)  # Page title should not be "Login"
            self.assertNotIn(self.LOGIN_URL, driver.current_url)  # Should not be on the login page URL
            # Assert presence of an element typically found on a dashboard (e.g., "Welcome", "Dashboard", or "Logout" link)
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[contains(text(), 'Welcome')] | //*[contains(text(), 'Dashboard')] | //a[text()='Logout']")
                    )
                )
            except Exception:
                self.fail(f"Failed to verify {user_type_name} dashboard access. No specific URL ({expected_dashboard_url_part}) or generic dashboard elements found.")
        # print(f"Successfully verified {user_type_name} dashboard access at {driver.current_url}") # Uncomment for debugging

    def test_admin_login_and_logout(self):
        """Tests login and logout for an Admin user."""
        self._login(self.ADMIN_CREDS["email"], self.ADMIN_CREDS["password"])
        # Assuming admin dashboard URL contains "/admin/dashboard/". Adjust if different.
        self._assert_dashboard_access("/admin/dashboard/", "Admin")
        self._logout()
        self.assertIn("login", self.driver.current_url.lower())

    def test_staff_login_and_logout(self):
        """Tests login and logout for a Staff user."""
        self._login(self.STAFF_CREDS["email"], self.STAFF_CREDS["password"])
        # Assuming staff dashboard URL contains "/staff/dashboard/". Adjust if different.
        self._assert_dashboard_access("/staff/dashboard/", "Staff")
        self._logout()
        self.assertIn("login", self.driver.current_url.lower())

    def test_student_login_and_logout(self):
        """Tests login and logout for a Student user."""
        self._login(self.STUDENT_CREDS["email"], self.STUDENT_CREDS["password"])
        # Assuming student dashboard URL contains "/student/dashboard/". Adjust if different.
        self._assert_dashboard_access("/student/dashboard/", "Student")
        self._logout()
        self.assertIn("login", self.driver.current_url.lower())


if __name__ == '__main__':
    # When running from an IDE or manually, use argv and exit=False to prevent SystemExit
    unittest.main(argv=['first-arg-is-ignored'], exit=False)