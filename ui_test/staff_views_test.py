import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager


class DjangoStaffPanelTests(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000/"

    # Login Credentials
    # Automatically detect which login to use based on the test name or context.
    # For these views (all staff_ prefix), we primarily use staff credentials.
    STAFF_EMAIL = "bill@ms.com"
    STAFF_PASSWORD = "123"

    ADMIN_EMAIL = "qasim@admin.com"
    ADMIN_PASSWORD = "admin"

    STUDENT_EMAIL = "qasim@nu.edu.pk"
    STUDENT_PASSWORD = "123"

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")  # Set a default window size for consistent screenshots/rendering

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.implicitly_wait(5)  # Implicit wait for elements to appear (max 5 seconds)

    def tearDown(self):
        self.driver.quit()

    def login(self, email, password):
        """
        Logs into the Django application with the given credentials.
        Assumes a login page at BASE_URL + "login/".
        """
        driver = self.driver
        driver.get(self.BASE_URL + "login/")
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        
        self.assertIn("Login", driver.title) # Basic check for login page title

        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()

        # After login, redirect behavior varies by user type.
        # For staff, we expect to land on or be redirected to the staff home page.
        if email == self.STAFF_EMAIL:
            WebDriverWait(driver, 10).until(
                EC.url_contains("/staff/home") or EC.title_contains("Staff Panel")
            )
            self.assertIn("Staff Panel", driver.title) # Verify staff panel
        elif email == self.ADMIN_EMAIL:
            WebDriverWait(driver, 10).until(
                EC.url_contains("/admin/home") or EC.title_contains("Admin Panel")
            )
            self.assertIn("Admin Panel", driver.title) # Verify admin panel
        elif email == self.STUDENT_EMAIL:
            WebDriverWait(driver, 10).until(
                EC.url_contains("/student/home") or EC.title_contains("Student Panel")
            )
            self.assertIn("Student Panel", driver.title) # Verify student panel
        print(f"Successfully logged in as {email}")

    def assert_success_message(self, message_text, timeout=10):
        """
        Asserts that a success message (Django messages framework) is displayed.
        Assumes success messages have a CSS class 'alert-success'.
        """
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        success_message = self.driver.find_element(By.CLASS_NAME, "alert-success").text
        self.assertIn(message_text, success_message)
        print(f"Success message found: '{success_message}'")

    def assert_error_message(self, message_text, timeout=10):
        """
        Asserts that an error message (Django messages framework) is displayed.
        Assumes error messages have a CSS class 'alert-danger'.
        """
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        error_message = self.driver.find_element(By.CLASS_NAME, "alert-danger").text
        self.assertIn(message_text, error_message)
        print(f"Error message found: '{error_message}'")

    # --- Test Cases for Staff Views ---
    # Assuming URLs follow a pattern like BASE_URL + "staff/view_name/"

    def test_staff_home(self):
        self.login(self.STAFF_EMAIL, self.STAFF_PASSWORD)
        driver = self.driver
        driver.get(self.BASE_URL + "staff/home/") # Direct navigation in case of different redirect path

        WebDriverWait(driver, 10).until(
            EC.title_contains("Staff Panel")
        )
        self.assertIn("Staff Panel", driver.title)
        # Verify presence of key statistics elements
        self.assertTrue(driver.find_element(By.XPATH, "//h3[contains(text(), 'Total Students')]").is_displayed())
        self.assertTrue(driver.find_element(By.XPATH, "//h3[contains(text(), 'Total Attendance')]").is_displayed())
        self.assertTrue(driver.find_element(By.XPATH, "//h3[contains(text(), 'Total Leave')]").is_displayed())
        self.assertTrue(driver.find_element(By.XPATH, "//h3[contains(text(), 'Total Subject')]").is_displayed())
        print("Staff Home page loaded and verified.")

    def test_staff_take_attendance(self):
        self.login(self.STAFF_EMAIL, self.STAFF_PASSWORD)
        driver = self.driver
        driver.get(self.BASE_URL + "staff/take_attendance/")

        WebDriverWait(driver, 10).until(
            EC.title_contains("Take Attendance")
        )
        self.assertIn("Take Attendance", driver.title)

        # Select Subject
        subject_dropdown = Select(driver.find_element(By.ID, "subject"))
        # Assume at least one subject option beyond a potential placeholder "---" exists
        if len(subject_dropdown.options) > 1:
            subject_dropdown.select_by_index(1) # Select the first actual subject
            print(f"Selected subject: {subject_dropdown.first_selected_option.text}")
        else:
            self.skipTest("No subjects available for attendance. Skipping this test.")
            return

        # Select Session (assuming `sessions` are populated based on the view logic)
        session_dropdown = Select(driver.find_element(By.ID, "session"))
        if len(session_dropdown.options) > 1:
            session_dropdown.select_by_index(1) # Select the first actual session
            print(f"Selected session: {session_dropdown.first_selected_option.text}")
        else:
            self.skipTest("No sessions available for attendance. Skipping this test.")
            return

        # Wait for students to load via AJAX (get_students)
        # The JavaScript for get_students might be triggered by onchange event of subject/session dropdowns
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//tbody[@id='student_data']/tr"))
        )
        student_rows = driver.find_elements(By.XPATH, "//tbody[@id='student_data']/tr")
        self.assertGreater(len(student_rows), 0, "No students loaded for attendance.")
        print(f"Loaded {len(student_rows)} students for attendance.")

        # Mark all students Present for simplicity
        for row in student_rows:
            student_admin_id = row.get_attribute("data-admin-id") # Assuming an attribute like data-admin-id or data-student-id
            # The radio button names are 'student_<student_id>'.
            # We need to find the actual student ID, not admin_id, from the HTML for the radio name.
            # Let's assume the actual student.id is available as `data-student-pk` or similar.
            # If not, the current XPATH might need adjustment based on rendered HTML.
            try:
                # Assuming student_id is directly on the row, or derivable.
                # For `save_attendance` the JSON uses `student_dict.get('id')` which is student PK.
                # We need to match this. Let's assume `data-student-id` on the `tr`
                student_pk = row.get_attribute("data-student-id") 
                radio_present = row.find_element(By.XPATH, f".//input[@type='radio'][@name='student_data_{student_pk}'][@value='True']")
                radio_present.click()
            except Exception as e:
                print(f"Could not find radio button for student. Error: {e}")
                continue


        # Set attendance date
        date_input = driver.find_element(By.ID, "attendance_date") # Assuming input id="attendance_date" for the date picker
        date_input.send_keys("01-01-2023") # Example date, adjust as needed

        # Submit attendance (triggers save_attendance)
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save Attendance')]")
        save_button.click()

        # The `save_attendance` view returns "OK" as HttpResponse, typically handled by JS.
        # This might result in a JS alert or a message on the page.
        WebDriverWait(driver, 10).until(
            EC.alert_is_present()
        )
        alert = driver.switch_to.alert
        self.assertEqual("OK", alert.text) # Assuming the alert text is exactly "OK"
        alert.accept()
        print("Attendance taken successfully.")

    def test_staff_update_attendance(self):
        # This test requires existing attendance data to update.
        # It's highly dependent on the state of the database.
        self.login(self.STAFF_EMAIL, self.STAFF_PASSWORD)
        driver = self.driver
        driver.get(self.BASE_URL + "staff/update_attendance/")

        WebDriverWait(driver, 10).until(
            EC.title_contains("Update Attendance")
        )
        self.assertIn("Update Attendance", driver.title)

        # Select Subject
        subject_dropdown = Select(driver.find_element(By.ID, "subject"))
        if len(subject_dropdown.options) > 1:
            subject_dropdown.select_by_index(1)
            print(f"Selected subject: {subject_dropdown.first_selected_option.text}")
        else:
            self.skipTest("No subjects available for update attendance. Skipping.")
            return

        # Select Session
        session_dropdown = Select(driver.find_element(By.ID, "session"))
        if len(session_dropdown.options) > 1:
            session_dropdown.select_by_index(1)
            print(f"Selected session: {session_dropdown.first_selected_option.text}")
        else:
            self.skipTest("No sessions available for update attendance. Skipping.")
            return

        # Wait for attendance dates to load and select one (get_student_attendance is triggered by this)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "attendance_date_id")) # Assuming attendance date dropdown has this ID
        )
        attendance_date_dropdown = Select(driver.find_element(By.ID, "attendance_date_id"))
        if len(attendance_date_dropdown.options) > 1:
            attendance_date_dropdown.select_by_index(1) # Select the first actual attendance record date
            print(f"Selected attendance date: {attendance_date_dropdown.first_selected_option.text}")
        else:
            self.skipTest("No attendance records found for selected subject/session. Skipping update attendance test.")
            return

        # Wait for student attendance data to load via AJAX (get_student_attendance)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//tbody[@id='student_data']/tr"))
        )
        student_rows = driver.find_elements(By.XPATH, "//tbody[@id='student_data']/tr")
        self.assertGreater(len(student_rows), 0, "No student attendance data loaded for update.")
        print(f"Loaded {len(student_rows)} students for update.")

        # Update attendance for a student (e.g., toggle status for the first student)
        first_student_row = student_rows[0]
        # For update_attendance, the student_data JSON uses 'id' which is student admin_id
        student_admin_id = first_student_row.get_attribute("data-admin-id")

        # Find the radio buttons for this student and toggle its status
        # Example: change status of first student. Need to know current status.
        # Assuming there are radio buttons with name 'student_data_<student_admin_id>'
        # and values 'True'/'False'.
        
        # Check current status (if radio buttons are pre-selected)
        current_status_present = False
        try:
            if first_student_row.find_element(By.XPATH, f".//input[@type='radio'][@name='student_data_{student_admin_id}'][@value='True']").is_selected():
                current_status_present = True
        except:
            pass # Not selected True

        if current_status_present:
            # Change to Absent
            first_student_row.find_element(By.XPATH, f".//input[@type='radio'][@name='student_data_{student_admin_id}'][@value='False']").click()
            print(f"Toggled student (admin_id: {student_admin_id}) to Absent.")
        else:
            # Change to Present
            first_student_row.find_element(By.XPATH, f".//input[@type='radio'][@name='student_data_{student_admin_id}'][@value='True']").click()
            print(f"Toggled student (admin_id: {student_admin_id}) to Present.")

        # Submit updated attendance (triggers update_attendance)
        update_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Update Attendance')]")
        update_button.click()

        WebDriverWait(driver, 10).until(
            EC.alert_is_present()
        )
        alert = driver.switch_to.alert
        self.assertEqual("OK", alert.text)
        alert.accept()
        print("Attendance updated successfully.")

    def test_staff_apply_leave(self):
        self.login(self.STAFF_EMAIL, self.STAFF_PASSWORD)
        driver = self.driver
        driver.get(self.BASE_URL + "staff/apply_leave/")

        WebDriverWait(driver, 10).until(
            EC.title_contains("Apply for Leave")
        )
        self.assertIn("Apply for Leave", driver.title)

        # Fill the form fields (assuming Django form renders with id_fieldname)
        driver.find_element(By.ID, "id_leave_date").send_keys("01-02-2023") # Example date
        driver.find_element(By.ID, "id_message").send_keys("Requesting a day off for personal reasons for testing.")

        # Submit the form
        driver.find_element(By.XPATH, "//button[contains(text(), 'Apply for Leave')]").click()

        # Check for success message (from messages framework)
        self.assert_success_message("Application for leave has been submitted for review")
        print("Leave application submitted successfully.")

    def test_staff_feedback(self):
        self.login(self.STAFF_EMAIL, self.STAFF_PASSWORD)
        driver = self.driver
        driver.get(self.BASE_URL + "staff/feedback/")

        WebDriverWait(driver, 10).until(
            EC.title_contains("Add Feedback")
        )
        self.assertIn("Add Feedback", driver.title)

        # Fill the form
        driver.find_element(By.ID, "id_message").send_keys("This is a test feedback message from staff for testing purposes.")

        # Submit the form
        driver.find_element(By.XPATH, "//button[contains(text(), 'Add Feedback')]").click()

        # Check for success message
        self.assert_success_message("Feedback submitted for review")
        print("Feedback submitted successfully.")

    def test_staff_view_profile(self):
        self.login(self.STAFF_EMAIL, self.STAFF_PASSWORD)
        driver = self.driver
        driver.get(self.BASE_URL + "staff/profile/") # Assuming URL '/staff/profile/'

        WebDriverWait(driver, 10).until(
            EC.title_contains("View/Update Profile")
        )
        self.assertIn("View/Update Profile", driver.title)

        # Update some profile fields (e.g., address)
        address_field = driver.find_element(By.ID, "id_address")
        address_field.clear()
        address_field.send_keys("123 Test Street, Automated City, 54321")

        # Select Gender if it's a dropdown/select element
        try:
            gender_dropdown = Select(driver.find_element(By.ID, "id_gender"))
            # Assuming 'Male' or 'Female' are value options
            gender_dropdown.select_by_value("Female")
            print("Gender updated to Female.")
        except:
            print("Gender field is not a select dropdown with id 'id_gender' or element not found, skipping gender update.")

        # Submit form (not changing password or profile pic for simplicity in automated testing)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Update Profile')]").click()

        # Check for success message
        self.assert_success_message("Profile Updated!")
        print("Staff profile updated successfully.")

    def test_staff_view_notification(self):
        self.login(self.STAFF_EMAIL, self.STAFF_PASSWORD)
        driver = self.driver
        driver.get(self.BASE_URL + "staff/view_notification/")

        WebDriverWait(driver, 10).until(
            EC.title_contains("View Notifications")
        )
        self.assertIn("View Notifications", driver.title)
        
        # Check for the presence of a notification list container or a "No Notifications Yet" message
        try:
            notification_list_present = driver.find_element(By.ID, "notification_list").is_displayed()
        except:
            notification_list_present = False
        
        try:
            no_notifications_message_present = driver.find_element(By.XPATH, "//p[contains(text(), 'No Notifications Yet')]").is_displayed()
        except:
            no_notifications_message_present = False

        self.assertTrue(notification_list_present or no_notifications_message_present,
                        "Notification list or 'No notifications' message not found.")
        print("Staff View Notifications page loaded and verified.")

    def test_staff_add_result(self):
        self.login(self.STAFF_EMAIL, self.STAFF_PASSWORD)
        driver = self.driver
        driver.get(self.BASE_URL + "staff/add_result/")

        WebDriverWait(driver, 10).until(
            EC.title_contains("Result Upload")
        )
        self.assertIn("Result Upload", driver.title)

        # Select Subject
        subject_dropdown = Select(driver.find_element(By.ID, "subject"))
        if len(subject_dropdown.options) > 1:
            subject_dropdown.select_by_index(1)
            print(f"Selected subject: {subject_dropdown.first_selected_option.text}")
        else:
            self.skipTest("No subjects available for result upload. Skipping.")
            return

        # Select Session (if this filters students, it needs to be selected before student_list)
        session_dropdown = Select(driver.find_element(By.ID, "session"))
        if len(session_dropdown.options) > 1:
            session_dropdown.select_by_index(1)
            print(f"Selected session: {session_dropdown.first_selected_option.text}")
        else:
            self.skipTest("No sessions available for result upload. Skipping.")
            return

        # Wait for students dropdown to populate (assuming AJAX or similar on subject/session change)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "student_list"))
        )
        student_dropdown = Select(driver.find_element(By.ID, "student_list"))
        if len(student_dropdown.options) > 1:
            student_dropdown.select_by_index(1) # Select the first actual student
            print(f"Selected student: {student_dropdown.first_selected_option.text}")
        else:
            self.skipTest("No students available for result upload. Skipping.")
            return

        # At this point, `fetch_student_result` might be triggered if a result already exists for the selected student/subject.
        # This would pre-fill test/exam fields. We can check if fields are already filled.

        # Fill in scores (assuming input IDs like id_test and id_exam, or similar based on view's 'test', 'exam' keys)
        test_score_input = driver.find_element(By.ID, "id_test_marks") # Common Django form ID guess
        exam_score_input = driver.find_element(By.ID, "id_exam_marks") # Common Django form ID guess

        test_score_input.clear()
        test_score_input.send_keys("85")
        exam_score_input.clear()
        exam_score_input.send_keys("92")

        # Submit form
        driver.find_element(By.XPATH, "//button[contains(text(), 'Add Result')]").click()

        # Check for success message (either "Scores Saved" or "Scores Updated")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        success_message_element = driver.find_element(By.CLASS_NAME, "alert-success")
        self.assertTrue("Scores Saved" in success_message_element.text or "Scores Updated" in success_message_element.text)
        print("Student result added/updated successfully.")


if __name__ == '__main__':
    # Important:
    # 1. Ensure your Django development server is running on http://127.0.0.1:8000/
    # 2. Populate your Django database with initial data:
    #    - CustomUser objects for Admin, Staff, Student roles with the specified credentials.
    #    - Staff, Course, Subject, Session, Student objects for the staff to manage.
    #    - For attendance/result tests, some pre-existing data might be necessary for 'update' tests or for dropdowns to be non-empty.
    # 3. Ensure your `urls.py` maps the views correctly (e.g., `path('staff/home/', staff_home, name='staff_home')`).
    #    The test code assumes paths like `/staff/home/`, `/staff/take_attendance/`, etc., and `/login/` for login.

    unittest.main(argv=['first-arg-is-ignored'], exit=False)