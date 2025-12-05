import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time # For short waits, replace with WebDriverWait where possible

class SeleniumDjangoTests(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000/"

    # Login Credentials
    USERS = {
        "admin": {"email": "qasim@admin.com", "password": "admin"},
        "staff": {"email": "bill@ms.com", "password": "123"},
        "student": {"email": "qasim@nu.edu.pk", "password": "123"},
        "invalid": {"email": "wrong@user.com", "password": "wrong"}
    }

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080") # Set a default window size for headless

        cls.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        cls.driver.implicitly_wait(10) # Set a global implicit wait

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def _login(self, email, password):
        """
        Helper method to log in a user. Automatically detects if it's an admin login.
        """
        driver = self.driver
        if email == self.USERS["admin"]["email"]:
            # Admin login usually goes to /admin/
            driver.get(f"{self.BASE_URL}admin/login/?next=/admin/")
            # Assuming Django admin login form fields
            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")
            login_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Log in']")
        else:
            # General user login (staff/student) usually goes to /login/
            driver.get(f"{self.BASE_URL}login/") # Assuming a /login/ URL for non-admin users
            # Assuming general login form fields
            username_field = driver.find_element(By.NAME, "username") # Can be 'email' or 'username'
            password_field = driver.find_element(By.NAME, "password")
            login_button = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")

        username_field.send_keys(email)
        password_field.send_keys(password)
        login_button.click()

    def _logout(self):
        """
        Helper method to log out a user.
        Attempts to find a logout link, assuming common Django patterns.
        """
        driver = self.driver
        # Try to find common logout elements
        try:
            # For Django admin logout link
            logout_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/admin/logout/')] | //a[contains(text(), 'Log out')] | //a[contains(text(), 'Sign out')]"))
            )
            logout_link.click()
            # If redirected to a confirmation page, click confirm
            try:
                confirm_logout_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Yes, log me out']"))
                )
                confirm_logout_button.click()
            except:
                pass # No confirmation needed or already logged out
        except:
            # For general user logout, try /logout/ endpoint directly
            driver.get(f"{self.BASE_URL}logout/")
            # If there's a confirmation button for general logout
            try:
                confirm_logout_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit'] | //input[@type='submit']"))
                )
                confirm_logout_button.click()
            except:
                pass # No confirmation needed or already logged out

        WebDriverWait(driver, 10).until(
            EC.url_contains(f"{self.BASE_URL}login/") or EC.url_contains(f"{self.BASE_URL}admin/login/") or EC.url_contains(f"{self.BASE_URL}")
        )
        print(f"Logged out. Current URL: {driver.current_url}") # Debugging

    def _assert_logged_in(self, expected_url_part="", success_text_element=None):
        """
        Asserts that the user is logged in.
        Can check for a URL part or a specific element text.
        """
        driver = self.driver
        if expected_url_part:
            WebDriverWait(driver, 10).until(EC.url_contains(expected_url_part))
        if success_text_element:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(success_text_element))
        print(f"Asserted logged in. Current URL: {driver.current_url}") # Debugging

    def _assert_logged_out(self):
        """
        Asserts that the user is logged out (redirected to login page).
        """
        driver = self.driver
        WebDriverWait(driver, 10).until(
            lambda driver: f"{self.BASE_URL}login/" in driver.current_url or f"{self.BASE_URL}admin/login/" in driver.current_url
        )
        print(f"Asserted logged out. Current URL: {driver.current_url}") # Debugging

    def test_01_admin_login_logout(self):
        """
        Test Admin user login and logout.
        """
        print("\n--- Running Admin Login/Logout Test ---")
        user = self.USERS["admin"]
        self._login(user["email"], user["password"])
        self._assert_logged_in(expected_url_part="/admin/")
        self.assertIn("admin", self.driver.current_url)
        self._logout()
        self._assert_logged_out()

    def test_02_staff_login_logout(self):
        """
        Test Staff user login and logout.
        """
        print("\n--- Running Staff Login/Logout Test ---")
        user = self.USERS["staff"]
        self._login(user["email"], user["password"])
        # Assuming staff user lands on the homepage or a staff-specific dashboard
        self._assert_logged_in(expected_url_part=self.BASE_URL) # Assuming homepage post-login
        self.assertNotIn("/admin/", self.driver.current_url) # Should not be in admin
        self._logout()
        self._assert_logged_out()

    def test_03_student_login_logout(self):
        """
        Test Student user login and logout.
        """
        print("\n--- Running Student Login/Logout Test ---")
        user = self.USERS["student"]
        self._login(user["email"], user["password"])
        # Assuming student user lands on the homepage or a student-specific dashboard
        self._assert_logged_in(expected_url_part=self.BASE_URL) # Assuming homepage post-login
        self.assertNotIn("/admin/", self.driver.current_url) # Should not be in admin
        self._logout()
        self._assert_logged_out()

    def test_04_invalid_credentials_login(self):
        """
        Test login with invalid credentials.
        """
        print("\n--- Running Invalid Credentials Login Test ---")
        user = self.USERS["invalid"]
        self._login(user["email"], user["password"])
        # Expect to stay on the login page or see an error message
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Please enter a correct')] | //*[contains(text(), 'Invalid credentials')] | //*[contains(@class, 'errorlist')]"))
        )
        self.assertTrue(
            f"{self.BASE_URL}login/" in self.driver.current_url or f"{self.BASE_URL}admin/login/" in self.driver.current_url,
            "Expected to remain on login page with error"
        )
        print(f"Invalid login attempt successful. Current URL: {self.driver.current_url}") # Debugging

    def test_05_admin_access_control(self):
        """
        Test that only admin can access /admin/.
        """
        print("\n--- Running Admin Access Control Test ---")
        driver = self.driver
        admin_url = f"{self.BASE_URL}admin/"

        # 1. Try accessing /admin/ as an unauthenticated user
        driver.get(admin_url)
        # Should be redirected to admin login
        WebDriverWait(driver, 10).until(EC.url_contains("/admin/login/"))
        self.assertIn("/admin/login/", driver.current_url)
        print(f"Unauthenticated user redirected to: {driver.current_url}")

        # 2. Log in as Staff and try accessing /admin/
        user_staff = self.USERS["staff"]
        self._login(user_staff["email"], user_staff["password"])
        self.driver.get(admin_url)
        # Staff should not access /admin/, should be redirected or get permission denied
        WebDriverWait(driver, 10).until(
            lambda driver: "/admin/login/" in driver.current_url or "Forbidden" in driver.page_source or "Permission denied" in driver.page_source
        )
        self.assertFalse("/admin/" == driver.current_url and "Django administration" in driver.page_source,
                         "Staff user should not access Django admin dashboard directly.")
        print(f"Staff user access to admin: {driver.current_url}. Page source contains 'Forbidden' or 'Permission denied': {'Forbidden' in driver.page_source or 'Permission denied' in driver.page_source}")
        self._logout()
        self._assert_logged_out()

        # 3. Log in as Student and try accessing /admin/
        user_student = self.USERS["student"]
        self._login(user_student["email"], user_student["password"])
        self.driver.get(admin_url)
        # Student should not access /admin/, should be redirected or get permission denied
        WebDriverWait(driver, 10).until(
            lambda driver: "/admin/login/" in driver.current_url or "Forbidden" in driver.page_source or "Permission denied" in driver.page_source
        )
        self.assertFalse("/admin/" == driver.current_url and "Django administration" in driver.page_source,
                         "Student user should not access Django admin dashboard directly.")
        print(f"Student user access to admin: {driver.current_url}. Page source contains 'Forbidden' or 'Permission denied': {'Forbidden' in driver.page_source or 'Permission denied' in driver.page_source}")
        self._logout()
        self._assert_logged_out()

        # 4. Log in as Admin and verify access to /admin/
        user_admin = self.USERS["admin"]
        self._login(user_admin["email"], user_admin["password"])
        driver.get(admin_url) # Navigate directly to admin home to ensure access
        self._assert_logged_in(expected_url_part="/admin/")
        WebDriverWait(driver, 10).until(EC.title_contains("Django administration"))
        self.assertIn("Django administration", driver.page_source)
        print(f"Admin user successfully accessed: {driver.current_url}")
        self._logout()
        self._assert_logged_out()

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)