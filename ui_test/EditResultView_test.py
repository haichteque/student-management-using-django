import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time # Used for small delays, consider more robust waits for production tests

class EditResultViewTests(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000/"
    LOGIN_URL = BASE_URL + "login/" # Assuming a common login URL for the project
    EDIT_RESULT_URL = BASE_URL + "edit_student_result/" # Assuming this is the URL for EditResultView

    # Login credentials
    ADMIN_USER = "qasim@admin.com"
    ADMIN_PASS = "admin"
    STAFF_USER = "bill@ms.com"
    STAFF_PASS = "123"
    STUDENT_USER = "qasim@nu.edu.pk"
    STUDENT_PASS = "123"

    def setUp(self):
        # Configure Chrome options for headless mode
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080") # Recommended for headless
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10) # Set an implicit wait for elements

    def tearDown(self):
        self.driver.quit()

    def _login(self, username, password):
        """Helper function to log in a user."""
        self.driver.get(self.LOGIN_URL)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        self.driver.find_element(By.NAME, "email").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for a reasonable indication of successful login (e.g., URL change or dashboard element)
        WebDriverWait(self.driver, 10).until(
            EC.url_changes(self.LOGIN_URL) or
            EC.presence_of_element_located((By.TAG_NAME, "body")) # Generic wait for page load
        )

    def _check_form_presence(self):
        """Helper to check if the edit result form elements are present."""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "id_student"))
            )
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "id_subject"))
            )
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "id_test"))
            )
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "id_exam"))
            )
            return True
        except:
            return False

    def test_unauthorized_access_as_admin(self):
        """Test that an admin user cannot access the staff-specific edit result page."""
        self._login(self.ADMIN_USER, self.ADMIN_PASS)
        self.driver.get(self.EDIT_RESULT_URL)
        
        # The view uses get_object_or_404(Staff, admin=request.user).
        # An admin user is not linked to a Staff object, so this will raise Http404.
        # This typically leads to a 500 error page if DEBUG=False or a traceback page if DEBUG=True,
        # or a redirect to a login page if handled by middleware.
        # We check if the expected form elements are NOT present and that the title isn't the expected one.
        self.assertFalse(self._check_form_presence(), "Admin user should not see the edit student result form.")
        self.assertNotIn("Edit Student's Result", self.driver.title, 
                         "Admin user should not have 'Edit Student\'s Result' title.")
        # Further check: verify we are not on the expected URL or are redirected
        self.assertFalse("edit_student_result" in self.driver.current_url) 


    def test_unauthorized_access_as_student(self):
        """Test that a student user cannot access the staff-specific edit result page."""
        self._login(self.STUDENT_USER, self.STUDENT_PASS)
        self.driver.get(self.EDIT_RESULT_URL)
        
        self.assertFalse(self._check_form_presence(), "Student user should not see the edit student result form.")
        self.assertNotIn("Edit Student's Result", self.driver.title, 
                         "Student user should not have 'Edit Student\'s Result' title.")
        self.assertFalse("edit_student_result" in self.driver.current_url)

    def test_successful_result_update_as_staff(self):
        """Test that a staff user can successfully update a student's result."""
        self._login(self.STAFF_USER, self.STAFF_PASS)
        self.driver.get(self.EDIT_RESULT_URL)

        # Wait for the form elements to be present
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_student"))
        )
        self.assertTrue(self._check_form_presence(), "Edit student result form not loaded for staff user.")

        # Select a student and subject
        # IMPORTANT: These values (options for student and subject) must exist in your database
        # and be linked to the logged-in staff user for subjects.
        # We attempt to select the first actual option (assuming index 0 is a placeholder).
        student_select_element = Select(self.driver.find_element(By.ID, "id_student"))
        subject_select_element = Select(self.driver.find_element(By.ID, "id_subject"))

        try:
            student_select_element.select_by_index(1) 
            time.sleep(0.5) # Small delay in case of AJAX/JS dependency for subject field
            subject_select_element.select_by_index(1)
        except Exception as e:
            self.skipTest(f"Could not select student/subject options in the form. "
                          f"Ensure your database is populated with a student, subject, and StudentResult for Staff '{self.STAFF_USER}'. Error: {e}")

        test_score_input = self.driver.find_element(By.ID, "id_test")
        exam_score_input = self.driver.find_element(By.ID, "id_exam")

        test_score_input.clear()
        exam_score_input.clear()
        test_score_input.send_keys("75")
        exam_score_input.send_keys("85")

        # Submit the form
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for success message (assuming Django messages use Bootstrap alert classes)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success")) 
        )

        success_message = self.driver.find_element(By.CLASS_NAME, "alert-success").text
        self.assertIn("Result Updated", success_message)
        # Verify redirect back to the same page
        self.assertIn(self.EDIT_RESULT_URL, self.driver.current_url)


    def test_invalid_form_submission_as_staff(self):
        """Test handling of invalid form submission (e.g., missing required fields) by staff."""
        self._login(self.STAFF_USER, self.STAFF_PASS)
        self.driver.get(self.EDIT_RESULT_URL)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_student"))
        )
        self.assertTrue(self._check_form_presence(), "Edit student result form not loaded for staff user.")

        student_select_element = Select(self.driver.find_element(By.ID, "id_student"))
        subject_select_element = Select(self.driver.find_element(By.ID, "id_subject"))
        
        try:
            student_select_element.select_by_index(1)
            time.sleep(0.5)
            subject_select_element.select_by_index(1)
        except Exception as e:
            self.skipTest(f"Could not select student/subject options in the form. "
                          f"Ensure your database is populated with a student, subject, and StudentResult for Staff '{self.STAFF_USER}'. Error: {e}")

        test_score_input = self.driver.find_element(By.ID, "id_test")
        exam_score_input = self.driver.find_element(By.ID, "id_exam")

        # Clear existing values but *do not* fill them, assuming they are required or cause form validation to fail
        test_score_input.clear() 
        exam_score_input.clear()

        # Submit the form with missing required data
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for warning message (assuming Django messages use Bootstrap alert classes)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-warning")) 
        )

        warning_message = self.driver.find_element(By.CLASS_NAME, "alert-warning").text
        self.assertIn("Result Could Not Be Updated", warning_message)
        # Verify that the page stays on the same URL as there was an error
        self.assertIn(self.EDIT_RESULT_URL, self.driver.current_url)

if __name__ == '__main__':
    unittest.main()