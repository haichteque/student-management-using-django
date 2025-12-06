import unittest
import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000/"
LOGIN_URL = f"{BASE_URL}login/"
LOGOUT_URL = f"{BASE_URL}logout/"

# Login credentials
ADMIN_CREDENTIALS = {"email": "qasim@admin.com", "password": "admin", "dashboard": "admin_dashboard"}
STAFF_CREDENTIALS = {"email": "bill@ms.com", "password": "123", "dashboard": "staff_dashboard"}
STUDENT_CREDENTIALS = {"email": "qasim@nu.edu.pk", "password": "123", "dashboard": "student_dashboard"}

# Dummy image for profile_pic upload
DUMMY_IMAGE_PATH = os.path.abspath("dummy_profile.png")
# Create a dummy image file if it doesn't exist
if not os.path.exists(DUMMY_IMAGE_PATH):
    try:
        from PIL import Image
        img = Image.new('RGB', (60, 30), color = 'red')
        img.save(DUMMY_IMAGE_PATH)
        print(f"Created dummy image at {DUMMY_IMAGE_PATH}")
    except ImportError:
        print("Pillow not installed. Cannot create dummy image. Please ensure a 'dummy_profile.png' exists for image uploads.")
        # Fallback: create a dummy text file. This might not work for actual image uploads.
        with open(DUMMY_IMAGE_PATH, 'w') as f:
            f.write("This is a dummy file content.")
            print(f"Created a dummy text file at {DUMMY_IMAGE_PATH}")

# Helper function to generate unique identifiers
def generate_unique_name(prefix):
    return f"{prefix}_{int(time.time())}"

# --- Base Test Class ---
class BaseSeleniumTestCase(unittest.TestCase):
    driver = None # Class-level driver

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless") # Run Chrome in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080") # Set a larger window size for headless
        options.add_argument("--disable-gpu") # Recommended for headless on some systems
        
        # Initialize the Chrome WebDriver. Ensure chromedriver is in your PATH or specify its path.
        # Example if chromedriver is not in PATH: service = Service('/path/to/chromedriver')
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(5) # Implicit wait for elements to be found

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()
        # Clean up dummy image
        if os.path.exists(DUMMY_IMAGE_PATH) and "dummy_profile.png" in DUMMY_IMAGE_PATH: # Only remove if created by script
            os.remove(DUMMY_IMAGE_PATH)
            print(f"Removed dummy image at {DUMMY_IMAGE_PATH}")

    def setUp(self):
        self.driver.get(BASE_URL)

    def login(self, email, password, expected_dashboard_url_part):
        self.driver.get(LOGIN_URL)
        try:
            # Wait for the login form to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            self.driver.find_element(By.NAME, "email").send_keys(email)
            self.driver.find_element(By.NAME, "password").send_keys(password)
            
            # Assuming the login button is a <button> or <input type="submit">
            login_button = self.driver.find_element(By.TAG_NAME, "button")
            login_button.click()
            
            # Wait for successful login by checking for URL change to dashboard
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(expected_dashboard_url_part)
            )
            print(f"Successfully logged in as {email}. Current URL: {self.driver.current_url}")
            return True
        except TimeoutException:
            self.fail(f"Login failed for {email}: Timeout waiting for page elements or dashboard redirect.")
        except NoSuchElementException:
            self.fail(f"Login failed for {email}: Could not find login form elements.")
        except ElementClickInterceptedException:
            self.fail(f"Login failed for {email}: Login button click intercepted (e.g., by an overlay).")
        except Exception as e:
            self.fail(f"An unexpected error occurred during login for {email}: {e}")

    def logout(self):
        self.driver.get(LOGOUT_URL)
        # Wait until the URL changes back to the login page
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(LOGIN_URL)
        )
        # Optionally, check for a login form element to confirm logout
        self.assertTrue(self.driver.find_element(By.NAME, "email").is_displayed(), "Logout failed: Login form not displayed after redirect.")
        print(f"Successfully logged out. Current URL: {self.driver.current_url}")

# --- Test Cases ---

class TestUserLogins(BaseSeleniumTestCase):
    def test_admin_login_logout(self):
        self.login(ADMIN_CREDENTIALS["email"], ADMIN_CREDENTIALS["password"], ADMIN_CREDENTIALS["dashboard"])
        self.assertIn(ADMIN_CREDENTIALS["dashboard"], self.driver.current_url)
        self.logout()
        self.assertIn("login", self.driver.current_url)

    def test_staff_login_logout(self):
        self.login(STAFF_CREDENTIALS["email"], STAFF_CREDENTIALS["password"], STAFF_CREDENTIALS["dashboard"])
        self.assertIn(STAFF_CREDENTIALS["dashboard"], self.driver.current_url)
        self.logout()
        self.assertIn("login", self.driver.current_url)

    def test_student_login_logout(self):
        self.login(STUDENT_CREDENTIALS["email"], STUDENT_CREDENTIALS["password"], STUDENT_CREDENTIALS["dashboard"])
        self.assertIn(STUDENT_CREDENTIALS["dashboard"], self.driver.current_url)
        self.logout()
        self.assertIn("login", self.driver.current_url)

class TestAdminFunctions(BaseSeleniumTestCase):
    # This class assumes Admin-specific URLs for adding/managing data.
    # If these URLs are different in your Django app, please update them.
    ADMIN_ADD_STUDENT_URL = f"{BASE_URL}add_student/" # Common admin URL for adding student
    ADMIN_ADD_STAFF_URL = f"{BASE_URL}add_staff/" # Common admin URL for adding staff
    ADMIN_ADD_COURSE_URL = f"{BASE_URL}add_course/"
    ADMIN_ADD_SUBJECT_URL = f"{BASE_URL}add_subject/"
    ADMIN_ADD_SESSION_URL = f"{BASE_URL}add_session/"

    def setUp(self):
        super().setUp()
        self.login(ADMIN_CREDENTIALS["email"], ADMIN_CREDENTIALS["password"], ADMIN_CREDENTIALS["dashboard"])

    def tearDown(self):
        self.logout()
        super().tearDown()

    def _submit_form_and_verify(self, url, success_url_part, required_element_name=None):
        self.driver.get(url)
        if required_element_name:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, required_element_name))
            )
        else:
            # Fallback for pages without specific required_element_name
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form")) # Ensure a form is present
            )

        # Fill common CustomUserForm fields if applicable
        if "add_student" in url or "add_staff" in url:
            unique_email = generate_unique_name("user") + "@example.com"
            self.driver.find_element(By.NAME, "first_name").send_keys("Test")
            self.driver.find_element(By.NAME, "last_name").send_keys("User")
            self.driver.find_element(By.NAME, "email").send_keys(unique_email)
            Select(self.driver.find_element(By.NAME, "gender")).select_by_value("M")
            self.driver.find_element(By.NAME, "password").send_keys("password123")
            self.driver.find_element(By.NAME, "address").send_keys("123 Test Street")
            
            # Upload profile picture
            try:
                profile_pic_input = self.driver.find_element(By.NAME, "profile_pic")
                profile_pic_input.send_keys(DUMMY_IMAGE_PATH)
            except NoSuchElementException:
                print(f"Warning: 'profile_pic' field not found on {url}, skipping image upload.")
            except Exception as e:
                print(f"Error uploading profile_pic on {url}: {e}")

        if "add_student" in url: # StudentForm specific fields
            try:
                # Assuming index 1 selects a valid option (not '---' or 'select')
                Select(self.driver.find_element(By.NAME, "course")).select_by_index(1)
            except (NoSuchElementException, IndexError):
                print(f"Warning: No 'course' options available on {url}, skipping selection.")
            try:
                Select(self.driver.find_element(By.NAME, "session")).select_by_index(1)
            except (NoSuchElementException, IndexError):
                print(f"Warning: No 'session' options available on {url}, skipping selection.")

        elif "add_staff" in url: # StaffForm specific fields
            try:
                Select(self.driver.find_element(By.NAME, "course")).select_by_index(1)
            except (NoSuchElementException, IndexError):
                print(f"Warning: No 'course' options available on {url}, skipping selection.")

        elif "add_course" in url: # CourseForm specific fields
            self.driver.find_element(By.NAME, "name").send_keys(generate_unique_name("Test Course"))

        elif "add_subject" in url: # SubjectForm specific fields
            self.driver.find_element(By.NAME, "name").send_keys(generate_unique_name("Test Subject"))
            try:
                Select(self.driver.find_element(By.NAME, "staff")).select_by_index(1)
            except (NoSuchElementException, IndexError):
                self.skipTest(f"Skipping add subject test for {url}: No staff available to assign.")
            try:
                Select(self.driver.find_element(By.NAME, "course")).select_by_index(1)
            except (NoSuchElementException, IndexError):
                self.skipTest(f"Skipping add subject test for {url}: No courses available to assign.")

        elif "add_session" in url: # SessionForm specific fields
            current_year = datetime.date.today().year
            self.driver.find_element(By.NAME, "start_year").send_keys(f"{current_year}-09-01")
            self.driver.find_element(By.NAME, "end_year").send_keys(f"{current_year + 1}-06-30")

        # Submit the form
        try:
            submit_button = self.driver.find_element(By.TAG_NAME, "button")
            submit_button.click()
        except NoSuchElementException:
            self.fail(f"No submit button found on {url}.")
        except ElementClickInterceptedException:
            # Try to click with JavaScript if intercepted by another element
            self.driver.execute_script("arguments[0].click();", submit_button)

        # Verify success
        try:
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(success_url_part) or 
                EC.presence_of_element_located((By.CLASS_NAME, "alert-success")) # Check for success message
            )
            self.assertNotIn("Error", self.driver.page_source)
            self.assertNotIn("alert-danger", self.driver.page_source)
            print(f"Successfully submitted form on {url}. Current URL: {self.driver.current_url}")
        except TimeoutException:
            self.fail(f"Form submission on {url} failed: Timeout waiting for success page or message. Current URL: {self.driver.current_url}\nPage Source:\n{self.driver.page_source}")
        except Exception as e:
            self.fail(f"An unexpected error occurred after form submission on {url}: {e}\nPage Source:\n{self.driver.page_source}")


    def test_add_student(self):
        # Assuming admin_add_student/ redirects to admin_manage_student/ or shows success
        self._submit_form_and_verify(self.ADMIN_ADD_STUDENT_URL, "manage_student", "email")

    def test_add_staff(self):
        # Assuming admin_add_staff/ redirects to admin_manage_staff/ or shows success
        self._submit_form_and_verify(self.ADMIN_ADD_STAFF_URL, "manage_staff", "email")

    def test_add_course(self):
        # Assuming admin_add_course/ redirects to admin_manage_course/ or shows success
        self._submit_form_and_verify(self.ADMIN_ADD_COURSE_URL, "manage_course", "name")

    def test_add_subject(self):
        # Assuming admin_add_subject/ redirects to admin_manage_subject/ or shows success
        self._submit_form_and_verify(self.ADMIN_ADD_SUBJECT_URL, "manage_subject", "name")

    def test_add_session(self):
        # Assuming admin_add_session/ redirects to admin_manage_session/ or shows success
        self._submit_form_and_verify(self.ADMIN_ADD_SESSION_URL, "manage_session", "start_year")


class TestStaffFunctions(BaseSeleniumTestCase):
    # This class assumes Staff-specific URLs for applying leave, feedback, and managing results.
    STAFF_APPLY_LEAVE_URL = f"{BASE_URL}staff_apply_leave/"
    STAFF_FEEDBACK_URL = f"{BASE_URL}staff_feedback/"
    STAFF_ADD_RESULT_URL = f"{BASE_URL}staff_add_result/" # Or admin_add_result based on permissions

    def setUp(self):
        super().setUp()
        self.login(STAFF_CREDENTIALS["email"], STAFF_CREDENTIALS["password"], STAFF_CREDENTIALS["dashboard"])

    def tearDown(self):
        self.logout()
        super().tearDown()

    def _submit_form_and_verify(self, url, success_url_part, required_element_name=None):
        self.driver.get(url)
        if required_element_name:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, required_element_name))
            )
        else:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )

        if "staff_apply_leave" in url: # LeaveReportStaffForm
            today = datetime.date.today().strftime("%Y-%m-%d")
            self.driver.find_element(By.NAME, "date").send_keys(today)
            self.driver.find_element(By.NAME, "message").send_keys("Requesting a leave due to personal reasons.")
        
        elif "staff_feedback" in url: # FeedbackStaffForm
            feedback_message = f"Staff feedback message {generate_unique_name('')}."
            self.driver.find_element(By.NAME, "feedback").send_keys(feedback_message)

        elif "staff_add_result" in url: # EditResultForm
            try:
                # Select first available options for ModelChoiceFields
                Select(self.driver.find_element(By.NAME, "session_year")).select_by_index(1)
                Select(self.driver.find_element(By.NAME, "subject")).select_by_index(1)
                Select(self.driver.find_element(By.NAME, "student")).select_by_index(1)
                self.driver.find_element(By.NAME, "test").send_keys("85")
                self.driver.find_element(By.NAME, "exam").send_keys("92")
            except (NoSuchElementException, IndexError) as e:
                self.skipTest(f"Skipping add student result test for {url}: Missing prerequisite data (sessions, subjects, students) or field issue: {e}")

        # Submit the form
        try:
            submit_button = self.driver.find_element(By.TAG_NAME, "button")
            submit_button.click()
        except NoSuchElementException:
            self.fail(f"No submit button found on {url}.")
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", submit_button)

        # Verify success
        try:
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(success_url_part) or
                EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
            )
            self.assertNotIn("Error", self.driver.page_source)
            self.assertNotIn("alert-danger", self.driver.page_source)
            print(f"Successfully submitted form on {url}. Current URL: {self.driver.current_url}")
        except TimeoutException:
            self.fail(f"Form submission on {url} failed: Timeout waiting for success page or message. Current URL: {self.driver.current_url}\nPage Source:\n{self.driver.page_source}")
        except Exception as e:
            self.fail(f"An unexpected error occurred after form submission on {url}: {e}\nPage Source:\n{self.driver.page_source}")


    def test_apply_for_leave(self):
        # Assuming staff_apply_leave/ redirects to staff_leave_status/ or shows success
        self._submit_form_and_verify(self.STAFF_APPLY_LEAVE_URL, "staff_leave_status", "date")

    def test_submit_feedback_staff(self):
        # Assuming staff_feedback/ redirects to staff_dashboard/ or shows success
        self._submit_form_and_verify(self.STAFF_FEEDBACK_URL, STAFF_CREDENTIALS["dashboard"], "feedback")

    def test_add_student_result(self):
        # Assuming staff_add_result/ redirects to staff_manage_result/ or shows success
        self._submit_form_and_verify(self.STAFF_ADD_RESULT_URL, "staff_manage_result", "session_year")


class TestStudentFunctions(BaseSeleniumTestCase):
    # This class assumes Student-specific URLs for applying leave and feedback.
    STUDENT_APPLY_LEAVE_URL = f"{BASE_URL}student_apply_leave/"
    STUDENT_FEEDBACK_URL = f"{BASE_URL}student_feedback/"

    def setUp(self):
        super().setUp()
        self.login(STUDENT_CREDENTIALS["email"], STUDENT_CREDENTIALS["password"], STUDENT_CREDENTIALS["dashboard"])

    def tearDown(self):
        self.logout()
        super().tearDown()

    def _submit_form_and_verify(self, url, success_url_part, required_element_name=None):
        self.driver.get(url)
        if required_element_name:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, required_element_name))
            )
        else:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )

        if "student_apply_leave" in url: # LeaveReportStudentForm
            today = datetime.date.today().strftime("%Y-%m-%d")
            self.driver.find_element(By.NAME, "date").send_keys(today)
            self.driver.find_element(By.NAME, "message").send_keys("Requesting leave for a medical appointment.")
        
        elif "student_feedback" in url: # FeedbackStudentForm
            feedback_message = f"Student feedback message {generate_unique_name('')}."
            self.driver.find_element(By.NAME, "feedback").send_keys(feedback_message)

        # Submit the form
        try:
            submit_button = self.driver.find_element(By.TAG_NAME, "button")
            submit_button.click()
        except NoSuchElementException:
            self.fail(f"No submit button found on {url}.")
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", submit_button)

        # Verify success
        try:
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(success_url_part) or
                EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
            )
            self.assertNotIn("Error", self.driver.page_source)
            self.assertNotIn("alert-danger", self.driver.page_source)
            print(f"Successfully submitted form on {url}. Current URL: {self.driver.current_url}")
        except TimeoutException:
            self.fail(f"Form submission on {url} failed: Timeout waiting for success page or message. Current URL: {self.driver.current_url}\nPage Source:\n{self.driver.page_source}")
        except Exception as e:
            self.fail(f"An unexpected error occurred after form submission on {url}: {e}\nPage Source:\n{self.driver.page_source}")

    def test_apply_for_leave(self):
        # Assuming student_apply_leave/ redirects to student_leave_status/ or shows success
        self._submit_form_and_verify(self.STUDENT_APPLY_LEAVE_URL, "student_leave_status", "date")

    def test_submit_feedback_student(self):
        # Assuming student_feedback/ redirects to student_dashboard/ or shows success
        self._submit_form_and_verify(self.STUDENT_FEEDBACK_URL, STUDENT_CREDENTIALS["dashboard"], "feedback")


# To run all tests
if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUserLogins))
    suite.addTest(unittest.makeSuite(TestAdminFunctions))
    suite.addTest(unittest.makeSuite(TestStaffFunctions))
    suite.addTest(unittest.makeSuite(TestStudentFunctions))

    # Run the test suite
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)