import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginCheckMiddlewareTests(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000/"
    # Assumed URL paths for the Django application, corresponding to the middleware logic
    LOGIN_PAGE_URL = BASE_URL + "login/"
    USER_LOGIN_SUBMIT_URL = BASE_URL + "doLogin/" # This is the URL that reverse('user_login') would point to
    ADMIN_HOME_URL = BASE_URL + "admin_home/" # Assumed to be served by a view in 'main_app.hod_views'
    STAFF_HOME_URL = BASE_URL + "staff_home/" # Assumed to be served by a view in 'main_app.staff_views'
    STUDENT_HOME_URL = BASE_URL + "student_home/" # Assumed to be served by a view in 'main_app.student_views'

    # Login credentials as provided
    CREDENTIALS = {
        "admin": {"email": "qasim@admin.com", "password": "admin"},
        "staff": {"email": "bill@ms.com", "password": "123"},
        "student": {"email": "qasim@nu.edu.pk", "password": "123"},
    }

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10) # Set an implicit wait for elements

    def tearDown(self):
        self.driver.quit()

    def _login(self, user_type):
        """
        Logs in a user of the specified type and verifies redirection to their respective home page.
        """
        credentials = self.CREDENTIALS[user_type]
        self.driver.get(self.LOGIN_PAGE_URL)

        # Wait for the login form to be present
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        # Fill in the login form
        self.driver.find_element(By.NAME, "email").send_keys(credentials["email"])
        self.driver.find_element(By.NAME, "password").send_keys(credentials["password"])
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # Determine the expected URL after successful login based on user type
        if user_type == "admin":
            expected_post_login_url = self.ADMIN_HOME_URL
        elif user_type == "staff":
            expected_post_login_url = self.STAFF_HOME_URL
        elif user_type == "student":
            expected_post_login_url = self.STUDENT_HOME_URL
        else:
            raise ValueError(f"Unsupported user type: {user_type}")

        # Wait for the redirection to the expected home page
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(expected_post_login_url)
        )
        self.assertEqual(self.driver.current_url, expected_post_login_url,
                         f"Login for {user_type} failed: did not redirect to {expected_post_login_url}")

    # --- Test Cases for Unauthenticated Users ---

    def test_unauthenticated_access_admin_home_redirects_to_login(self):
        self.driver.get(self.ADMIN_HOME_URL)
        WebDriverWait(self.driver, 10).until(EC.url_to_be(self.LOGIN_PAGE_URL))
        self.assertEqual(self.driver.current_url, self.LOGIN_PAGE_URL)

    def test_unauthenticated_access_staff_home_redirects_to_login(self):
        self.driver.get(self.STAFF_HOME_URL)
        WebDriverWait(self.driver, 10).until(EC.url_to_be(self.LOGIN_PAGE_URL))
        self.assertEqual(self.driver.current_url, self.LOGIN_PAGE_URL)

    def test_unauthenticated_access_student_home_redirects_to_login(self):
        self.driver.get(self.STUDENT_HOME_URL)
        WebDriverWait(self.driver, 10).until(EC.url_to_be(self.LOGIN_PAGE_URL))
        self.assertEqual(self.driver.current_url, self.LOGIN_PAGE_URL)

    def test_unauthenticated_access_login_page_stays_on_login(self):
        self.driver.get(self.LOGIN_PAGE_URL)
        # No redirection is expected, so we just check the current URL
        self.assertEqual(self.driver.current_url, self.LOGIN_PAGE_URL)

    def test_unauthenticated_access_user_login_submit_page_not_redirected_by_middleware(self):
        # The middleware explicitly says to "pass" if request.path == reverse('user_login')
        # This means the middleware itself should not force a redirect to login_page.
        # Other parts of Django (e.g., a POST-only view handler for GET requests) might redirect,
        # but the middleware's logic should not be the cause of redirection to LOGIN_PAGE_URL.
        self.driver.get(self.USER_LOGIN_SUBMIT_URL)
        # We assert that the URL is NOT the login_page, implying the middleware didn't intervene.
        # What it *does* redirect to (e.g., back to login form or 405) is outside the middleware's explicit action here.
        WebDriverWait(self.driver, 10).until_not(EC.url_to_be(self.LOGIN_PAGE_URL))
        self.assertNotEqual(self.driver.current_url, self.LOGIN_PAGE_URL,
                            "Middleware incorrectly redirected unauthenticated user_login URL to login page.")

    # --- Test Cases for Admin (user_type == '1') ---

    def test_admin_access_admin_home_success(self):
        self._login("admin")
        # Already on admin_home after login, no further redirection by middleware
        self.assertEqual(self.driver.current_url, self.ADMIN_HOME_URL)

    def test_admin_access_student_home_redirects_to_admin_home(self):
        self._login("admin")
        self.driver.get(self.STUDENT_HOME_URL)
        WebDriverWait(self.driver, 10).until(EC.url_to_be(self.ADMIN_HOME_URL))
        self.assertEqual(self.driver.current_url, self.ADMIN_HOME_URL)

    def test_admin_access_staff_home_success(self):
        self._login("admin")
        self.driver.get(self.STAFF_HOME_URL)
        # Middleware does not block admin from staff_views
        WebDriverWait(self.driver, 10).until(EC.url_to_be(self.STAFF_HOME_URL))
        self.assertEqual(self.driver.current_url, self.STAFF_HOME_URL)

    # --- Test Cases for Staff (user_type == '2') ---

    def test_staff_access_staff_home_success(self):
        self._login("staff")
        # Already on staff_home after login
        self.assertEqual(self.driver.current_url, self.STAFF_HOME_URL)

    def test_staff_access_student_home_redirects_to_staff_home(self):
        self._login("staff")
        self.driver.get(self.STUDENT_HOME_URL)
        WebDriverWait(self.driver, 10).until(EC.url_to_be(self.STAFF_HOME_URL))
        self.assertEqual(self.driver.current_url, self.STAFF_HOME_URL)

    def test_staff_access_admin_home_redirects_to_staff_home(self):
        self._login("staff")
        self.driver.get(self.ADMIN_HOME_URL)
        WebDriverWait(self.driver, 10).until(EC.url_to_be(self.STAFF_HOME_URL))
        self.assertEqual(self.driver.current_url, self.STAFF_HOME_URL)

    # --- Test Cases for Student (user_type == '3') ---

    def test_student_access_student_home_success(self):
        self._login("student")
        # Already on student_home after login
        self.assertEqual(self.driver.current_url, self.STUDENT_HOME_URL)

    def test_student_access_admin_home_redirects_to_student_home(self):
        self._login("student")
        self.driver.get(self.ADMIN_HOME_URL)
        WebDriverWait(self.driver, 10).until(EC.url_to_be(self.STUDENT_HOME_URL))
        self.assertEqual(self.driver.current_url, self.STUDENT_HOME_URL)

    def test_student_access_staff_home_redirects_to_student_home(self):
        self._login("student")
        self.driver.get(self.STAFF_HOME_URL)
        WebDriverWait(self.driver, 10).until(EC.url_to_be(self.STUDENT_HOME_URL))
        self.assertEqual(self.driver.current_url, self.STUDENT_HOME_URL)

if __name__ == '__main__':
    unittest.main()