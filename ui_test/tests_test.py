import unittest
from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

BASE_URL = "http://127.0.0.1:8000/"
LOGIN_URL = f"{BASE_URL}login/"

ADMIN_USER = "qasim@admin.com"
ADMIN_PASS = "admin"
STAFF_USER = "bill@ms.com"
STAFF_PASS = "123"
STUDENT_USER = "qasim@nu.edu.pk"
STUDENT_PASS = "123"

class SeleniumTestCase(TestCase):
    driver = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.driver.get(BASE_URL)
        try:
            logout_link = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
            )
            logout_link.click()
        except (TimeoutException, NoSuchElementException):
            pass

    def _login(self, username, password):
        self.driver.get(LOGIN_URL)
        username_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = self.driver.find_element(By.NAME, "password")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")

        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()

    def _assert_logged_in(self):
        try:
            logout_link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
            )
            self.assertIsNotNone(logout_link)
        except TimeoutException:
            self.fail("Login was not successful: Logout link not found or page did not change.")
        except NoSuchElementException:
            self.fail("Login was not successful: Logout link not found after successful login.")

    def _assert_logged_out(self):
        try:
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            self.assertIsNotNone(username_field)
        except TimeoutException:
            self.fail("User appears to be logged in: Login form not found.")
        except NoSuchElementException:
            self.fail("User appears to be logged in: Login form elements not found.")


class TestAdminLogin(SeleniumTestCase):
    def test_admin_successful_login(self):
        self._login(ADMIN_USER, ADMIN_PASS)
        self._assert_logged_in()
        # Assuming successful login redirects to a dashboard or home page
        # which URL doesn't contain '/login/' anymore.
        self.assertNotIn("/login/", self.driver.current_url)

class TestStaffLogin(SeleniumTestCase):
    def test_staff_successful_login(self):
        self._login(STAFF_USER, STAFF_PASS)
        self._assert_logged_in()
        self.assertNotIn("/login/", self.driver.current_url)

class TestStudentLogin(SeleniumTestCase):
    def test_student_successful_login(self):
        self._login(STUDENT_USER, STUDENT_PASS)
        self._assert_logged_in()
        self.assertNotIn("/login/", self.driver.current_url)