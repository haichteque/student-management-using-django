import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest
import time
import uuid
from PIL import Image

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000/"
LOGIN_URL = f"{BASE_URL}login/"  # Assuming a login endpoint at /login/

ADMIN_CREDENTIALS = {"email": "qasim@admin.com", "password": "admin"}
STAFF_CREDENTIALS = {"email": "bill@ms.com", "password": "123"}
STUDENT_CREDENTIALS = {"email": "qasim@nu.edu.pk", "password": "123"}

# Temporary file for uploads
TEMP_IMAGE_PATH = "test_profile_pic.png"

class SeleniumDjangoTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a dummy image file for uploads
        try:
            img = Image.new('RGB', (60, 30), color='red')
            img.save(TEMP_IMAGE_PATH)
        except ImportError:
            # Fallback if Pillow is not installed
            print("Pillow not installed. Creating a plain text file as a dummy for profile pic upload. For robust image tests, install Pillow.")
            with open(TEMP_IMAGE_PATH, 'w') as f:
                f.write("dummy image content")
        except Exception as e:
            print(f"Error creating dummy image: {e}. Creating a plain text file instead.")
            with open(TEMP_IMAGE_PATH, 'w') as f:
                f.write("dummy image content")


    @classmethod
    def tearDownClass(cls):
        # Clean up the dummy image file
        if os.path.exists(TEMP_IMAGE_PATH):
            os.remove(TEMP_IMAGE_PATH)

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")  # Ensure a large enough window size for headless
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)  # seconds
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

    def login(self, user_type):
        """Logs in the user based on the user_type."""
        self.driver.get(LOGIN_URL)
        time.sleep(1)  # Small delay to ensure page fully loads, adjust if needed

        credentials = {}
        if user_type == "admin":
            credentials = ADMIN_CREDENTIALS
        elif user_type == "staff":
            credentials = STAFF_CREDENTIALS
        elif user_type == "student":
            credentials = STUDENT_CREDENTIALS
        else:
            raise ValueError("Invalid user_type. Must be 'admin', 'staff', or 'student'.")

        self.driver.find_element(By.NAME, "email").send_keys(credentials["email"])
        self.driver.find_element(By.NAME, "password").send_keys(credentials["password"])
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # Assuming successful admin login redirects to /admin_home
        if user_type == "admin":
            self.wait.until(EC.url_to_be(f"{BASE_URL}admin_home"))
        # For staff and student, the target URL would need to be adjusted based on the application's routing.
        # Since the provided views are all admin-specific, we primarily focus on admin login for these tests.

    def assert_page_title(self, expected_title):
        """Helper to assert the page title visible in the template's content."""
        try:
            # Look for a common header element containing the page title
            title_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//h3[contains(text(), '{expected_title}')] | //h1[contains(text(), '{expected_title}')]")))
            self.assertIn(expected_title, title_element.text)
        except Exception:
            # Fallback to check the browser's HTML <title> tag
            self.assertIn(expected_title, self.driver.title)

    def _get_first_entity_id(self, manage_url, edit_link_xpath):
        """Helper to navigate to a manage page and extract the ID from the first edit link."""
        self.driver.get(manage_url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        edit_link = self.wait.until(EC.visibility_of_element_located((By.XPATH, edit_link_xpath)))
        href = edit_link.get_attribute("href")
        # Assuming URL structure like /edit_entity/ID/ or /delete_entity/ID/
        return href.split('/')[-2]

    # --- Admin Tests ---

    def test_admin_login_success(self):
        self.login("admin")
        self.assertIn(f"{BASE_URL}admin_home", self.driver.current_url)
        self.assert_page_title("Administrative Dashboard")

    def test_admin_home_dashboard(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}admin_home")
        self.assert_page_title("Administrative Dashboard")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h5[contains(text(), 'Total Staff')]")))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h5[contains(text(), 'Total Students')]")))

    def test_add_course(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_course")
        self.assert_page_title("Add Course")

        course_name = f"Test Course {uuid.uuid4().hex[:8]}"
        self.driver.find_element(By.NAME, "name").send_keys(course_name)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(EC.url_to_be(f"{BASE_URL}add_course"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Successfully Added')]")))

    def test_manage_course(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}manage_course")
        self.assert_page_title("Manage Courses")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    def test_add_staff(self):
        self.login("admin")
        # Ensure at least one course exists for staff assignment
        self.driver.get(f"{BASE_URL}add_course")
        course_name = f"Staff Course {uuid.uuid4().hex[:8]}"
        self.driver.find_element(By.NAME, "name").send_keys(course_name)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_staff")
        self.assert_page_title("Add Staff")

        unique_id = uuid.uuid4().hex[:8]
        first_name = f"StaffF_{unique_id}"
        last_name = f"StaffL_{unique_id}"
        email = f"staff_{unique_id}@example.com"
        password = "testpassword123"
        address = "123 Staff Street"

        self.driver.find_element(By.NAME, "first_name").send_keys(first_name)
        self.driver.find_element(By.NAME, "last_name").send_keys(last_name)
        self.driver.find_element(By.NAME, "email").send_keys(email)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.NAME, "address").send_keys(address)
        
        gender_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "gender")))
        gender_select.send_keys("Male") # Assuming select element, sending value.

        course_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "course")))
        course_select.find_elements(By.TAG_NAME, "option")[1].click()

        profile_pic_input = self.driver.find_element(By.NAME, "profile_pic")
        profile_pic_input.send_keys(os.path.abspath(TEMP_IMAGE_PATH))

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(EC.url_to_be(f"{BASE_URL}add_staff"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Successfully Added')]")))

    def test_manage_staff(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}manage_staff")
        self.assert_page_title("Manage Staff")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    def test_add_session(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_session")
        self.assert_page_title("Add Session")

        session_start = "2023-09-01"
        session_end = "2024-05-31"
        self.driver.find_element(By.NAME, "session_start").send_keys(session_start)
        self.driver.find_element(By.NAME, "session_end").send_keys(session_end)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(EC.url_to_be(f"{BASE_URL}add_session"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Session Created')]")))

    def test_manage_session(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}manage_session")
        self.assert_page_title("Manage Sessions")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    def test_add_student(self):
        self.login("admin")

        # Ensure a course and session exist
        self.driver.get(f"{BASE_URL}add_course")
        course_name = f"Student Course {uuid.uuid4().hex[:8]}"
        self.driver.find_element(By.NAME, "name").send_keys(course_name)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_session")
        session_start = "2025-09-01"
        session_end = "2026-05-31"
        self.driver.find_element(By.NAME, "session_start").send_keys(session_start)
        self.driver.find_element(By.NAME, "session_end").send_keys(session_end)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_student")
        self.assert_page_title("Add Student")

        unique_id = uuid.uuid4().hex[:8]
        first_name = f"StudentF_{unique_id}"
        last_name = f"StudentL_{unique_id}"
        email = f"student_{unique_id}@example.com"
        password = "studentpassword123"
        address = "456 Student Lane"

        self.driver.find_element(By.NAME, "first_name").send_keys(first_name)
        self.driver.find_element(By.NAME, "last_name").send_keys(last_name)
        self.driver.find_element(By.NAME, "email").send_keys(email)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.NAME, "address").send_keys(address)
        
        gender_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "gender")))
        gender_select.send_keys("Female")

        course_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "course")))
        course_select.find_elements(By.TAG_NAME, "option")[1].click()

        session_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "session")))
        session_select.find_elements(By.TAG_NAME, "option")[1].click()

        profile_pic_input = self.driver.find_element(By.NAME, "profile_pic")
        profile_pic_input.send_keys(os.path.abspath(TEMP_IMAGE_PATH))

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(EC.url_to_be(f"{BASE_URL}add_student"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Successfully Added')]")))

    def test_manage_student(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}manage_student")
        self.assert_page_title("Manage Students")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    def test_add_subject(self):
        self.login("admin")

        # Ensure course and staff exist first
        self.driver.get(f"{BASE_URL}add_course")
        course_name = f"Subject Course {uuid.uuid4().hex[:8]}"
        self.driver.find_element(By.NAME, "name").send_keys(course_name)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_staff")
        unique_id = uuid.uuid4().hex[:8]
        staff_email = f"subject_staff_{unique_id}@example.com"
        self.driver.find_element(By.NAME, "first_name").send_keys(f"SubStaffF_{unique_id}")
        self.driver.find_element(By.NAME, "last_name").send_keys(f"SubStaffL_{unique_id}")
        self.driver.find_element(By.NAME, "email").send_keys(staff_email)
        self.driver.find_element(By.NAME, "password").send_keys("password")
        self.driver.find_element(By.NAME, "address").send_keys("Staff Address")
        
        gender_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "gender")))
        gender_select.send_keys("Male")
        
        course_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "course")))
        course_select.find_elements(By.TAG_NAME, "option")[1].click()
        profile_pic_input = self.driver.find_element(By.NAME, "profile_pic")
        profile_pic_input.send_keys(os.path.abspath(TEMP_IMAGE_PATH))
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_subject")
        self.assert_page_title("Add Subject")

        subject_name = f"Test Subject {uuid.uuid4().hex[:8]}"
        self.driver.find_element(By.NAME, "name").send_keys(subject_name)

        course_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "course")))
        course_select.find_elements(By.TAG_NAME, "option")[1].click()

        staff_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "staff")))
        staff_select.find_elements(By.TAG_NAME, "option")[1].click()

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(EC.url_to_be(f"{BASE_URL}add_subject"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Successfully Added')]")))

    def test_manage_subject(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}manage_subject")
        self.assert_page_title("Manage Subjects")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    def test_edit_course(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_course")
        course_name_to_edit = f"Course_to_edit_{uuid.uuid4().hex[:8]}"
        self.driver.find_element(By.NAME, "name").send_keys(course_name_to_edit)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        course_id = self._get_first_entity_id(f"{BASE_URL}manage_course", "//a[contains(@href, '/edit_course/')]")
        self.assertIsNotNone(course_id, "Could not find a course to edit.")

        self.driver.get(f"{BASE_URL}edit_course/{course_id}")
        self.assert_page_title("Edit Course")

        updated_course_name = f"Updated {course_name_to_edit}"
        course_name_input = self.driver.find_element(By.NAME, "name")
        course_name_input.clear()
        course_name_input.send_keys(updated_course_name)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(EC.url_contains(f"{BASE_URL}edit_course/{course_id}"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Successfully Updated')]")))
        self.driver.get(f"{BASE_URL}manage_course")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//td[contains(text(), '{updated_course_name}')]")))

    def test_edit_staff(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_course")
        self.driver.find_element(By.NAME, "name").send_keys(f"Course For Edit Staff {uuid.uuid4().hex[:8]}")
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_staff")
        unique_id = uuid.uuid4().hex[:8]
        staff_email_to_edit = f"staff_to_edit_{unique_id}@example.com"
        self.driver.find_element(By.NAME, "first_name").send_keys(f"EditStaffF_{unique_id}")
        self.driver.find_element(By.NAME, "last_name").send_keys(f"EditStaffL_{unique_id}")
        self.driver.find_element(By.NAME, "email").send_keys(staff_email_to_edit)
        self.driver.find_element(By.NAME, "password").send_keys("password")
        self.driver.find_element(By.NAME, "address").send_keys("Staff Address")
        
        gender_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "gender")))
        gender_select.send_keys("Male")
        
        course_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "course")))
        course_select.find_elements(By.TAG_NAME, "option")[1].click()
        profile_pic_input = self.driver.find_element(By.NAME, "profile_pic")
        profile_pic_input.send_keys(os.path.abspath(TEMP_IMAGE_PATH))
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        staff_id = self._get_first_entity_id(f"{BASE_URL}manage_staff", "//a[contains(@href, '/edit_staff/')]")
        self.assertIsNotNone(staff_id, "Could not find staff to edit.")

        self.driver.get(f"{BASE_URL}edit_staff/{staff_id}")
        self.assert_page_title("Edit Staff")

        updated_first_name = f"Updated StaffF_{unique_id}"
        first_name_input = self.driver.find_element(By.NAME, "first_name")
        first_name_input.clear()
        first_name_input.send_keys(updated_first_name)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(EC.url_contains(f"{BASE_URL}edit_staff/{staff_id}"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Successfully Updated')]")))
        self.driver.get(f"{BASE_URL}manage_staff")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//td[contains(text(), '{updated_first_name}')]")))

    def test_edit_session(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_session")
        self.driver.find_element(By.NAME, "session_start").send_keys("2020-01-01")
        self.driver.find_element(By.NAME, "session_end").send_keys("2020-12-31")
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        session_id = self._get_first_entity_id(f"{BASE_URL}manage_session", "//a[contains(@href, '/edit_session/')]")
        self.assertIsNotNone(session_id, "Could not find a session to edit.")

        self.driver.get(f"{BASE_URL}edit_session/{session_id}")
        self.assert_page_title("Edit Session")

        updated_session_end = "2021-01-31"
        session_end_input = self.driver.find_element(By.NAME, "session_end")
        session_end_input.clear()
        session_end_input.send_keys(updated_session_end)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(EC.url_contains(f"{BASE_URL}edit_session/{session_id}"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Session Updated')]")))
        self.driver.get(f"{BASE_URL}manage_session")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//td[contains(text(), '{updated_session_end}')]")))

    def test_edit_student(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_course")
        self.driver.find_element(By.NAME, "name").send_keys(f"Course For Edit Student {uuid.uuid4().hex[:8]}")
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_session")
        self.driver.find_element(By.NAME, "session_start").send_keys("2025-09-01")
        self.driver.find_element(By.NAME, "session_end").send_keys("2026-05-31")
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_student")
        unique_id = uuid.uuid4().hex[:8]
        student_email_to_edit = f"student_to_edit_{unique_id}@example.com"
        self.driver.find_element(By.NAME, "first_name").send_keys(f"EditStudentF_{unique_id}")
        self.driver.find_element(By.NAME, "last_name").send_keys(f"EditStudentL_{unique_id}")
        self.driver.find_element(By.NAME, "email").send_keys(student_email_to_edit)
        self.driver.find_element(By.NAME, "password").send_keys("password")
        self.driver.find_element(By.NAME, "address").send_keys("Student Address")
        
        gender_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "gender")))
        gender_select.send_keys("Female")
        
        course_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "course")))
        course_select.find_elements(By.TAG_NAME, "option")[1].click()
        
        session_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "session")))
        session_select.find_elements(By.TAG_NAME, "option")[1].click()
        
        profile_pic_input = self.driver.find_element(By.NAME, "profile_pic")
        profile_pic_input.send_keys(os.path.abspath(TEMP_IMAGE_PATH))
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        student_id = self._get_first_entity_id(f"{BASE_URL}manage_student", "//a[contains(@href, '/edit_student/')]")
        self.assertIsNotNone(student_id, "Could not find a student to edit.")

        self.driver.get(f"{BASE_URL}edit_student/{student_id}")
        self.assert_page_title("Edit Student")

        updated_first_name = f"Updated StudentF_{unique_id}"
        first_name_input = self.driver.find_element(By.NAME, "first_name")
        first_name_input.clear()
        first_name_input.send_keys(updated_first_name)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(EC.url_contains(f"{BASE_URL}edit_student/{student_id}"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Successfully Updated')]")))
        self.driver.get(f"{BASE_URL}manage_student")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//td[contains(text(), '{updated_first_name}')]")))

    def test_edit_subject(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_course")
        self.driver.find_element(By.NAME, "name").send_keys(f"Course For Edit Subject {uuid.uuid4().hex[:8]}")
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_staff")
        unique_id = uuid.uuid4().hex[:8]
        self.driver.find_element(By.NAME, "first_name").send_keys(f"EditSubStaffF_{unique_id}")
        self.driver.find_element(By.NAME, "last_name").send_keys(f"EditSubStaffL_{unique_id}")
        self.driver.find_element(By.NAME, "email").send_keys(f"editsubject_staff_{unique_id}@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("password")
        self.driver.find_element(By.NAME, "address").send_keys("Staff Address")
        
        gender_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "gender")))
        gender_select.send_keys("Male")
        
        course_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "course")))
        course_select.find_elements(By.TAG_NAME, "option")[1].click()
        profile_pic_input = self.driver.find_element(By.NAME, "profile_pic")
        profile_pic_input.send_keys(os.path.abspath(TEMP_IMAGE_PATH))
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_subject")
        subject_name_to_edit = f"Subject_to_edit_{uuid.uuid4().hex[:8]}"
        self.driver.find_element(By.NAME, "name").send_keys(subject_name_to_edit)
        
        course_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "course")))
        course_select.find_elements(By.TAG_NAME, "option")[1].click()
        
        staff_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "staff")))
        staff_select.find_elements(By.TAG_NAME, "option")[1].click()
        
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        subject_id = self._get_first_entity_id(f"{BASE_URL}manage_subject", "//a[contains(@href, '/edit_subject/')]")
        self.assertIsNotNone(subject_id, "Could not find a subject to edit.")

        self.driver.get(f"{BASE_URL}edit_subject/{subject_id}")
        self.assert_page_title("Edit Subject")

        updated_subject_name = f"Updated {subject_name_to_edit}"
        subject_name_input = self.driver.find_element(By.NAME, "name")
        subject_name_input.clear()
        subject_name_input.send_keys(updated_subject_name)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(EC.url_contains(f"{BASE_URL}edit_subject/{subject_id}"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Successfully Updated')]")))
        self.driver.get(f"{BASE_URL}manage_subject")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//td[contains(text(), '{updated_subject_name}')]")))

    def test_admin_view_profile(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}admin_view_profile")
        self.assert_page_title("View/Edit Profile")

        first_name_input = self.driver.find_element(By.NAME, "first_name")
        first_name_input.clear()
        updated_first_name = f"AdminUpdatedF_{uuid.uuid4().hex[:4]}"
        first_name_input.send_keys(updated_first_name)

        profile_pic_input = self.driver.find_element(By.NAME, "profile_pic")
        profile_pic_input.send_keys(os.path.abspath(TEMP_IMAGE_PATH))

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(EC.url_to_be(f"{BASE_URL}admin_view_profile"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Profile Updated!')]")))
        self.assertEqual(self.driver.find_element(By.NAME, "first_name").get_attribute("value"), updated_first_name)

    def test_check_email_availability(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_staff")
        self.assert_page_title("Add Staff")

        email_input = self.driver.find_element(By.NAME, "email")
        email_input.send_keys("nonexistent@test.com")
        email_input.send_keys(Keys.TAB)
        time.sleep(1) # Allow for potential AJAX call to complete and update UI

        # To properly test, there should be a visible element that indicates availability.
        # Without specific knowledge of the template's dynamic error/success messages,
        # we can only ensure no immediate page-level errors occur.
        # For a truly robust test of this AJAX endpoint, direct 'requests' calls are often better.

        email_input.clear()
        email_input.send_keys(ADMIN_CREDENTIALS["email"])
        email_input.send_keys(Keys.TAB)
        time.sleep(1) # Allow for potential AJAX call to complete and update UI
        # Here we would assert an "Email already taken" message appears, if such a UI element exists.

    def test_student_feedback_message_get(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}student_feedback_message")
        self.assert_page_title("Student Feedback Messages")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    def test_staff_feedback_message_get(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}staff_feedback_message")
        self.assert_page_title("Staff Feedback Messages")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    def test_view_staff_leave_get(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}view_staff_leave")
        self.assert_page_title("Leave Applications From Staff")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    def test_view_student_leave_get(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}view_student_leave")
        self.assert_page_title("Leave Applications From Students")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    def test_admin_view_attendance(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}admin_view_attendance")
        self.assert_page_title("View Attendance")
        self.wait.until(EC.presence_of_element_located((By.NAME, "subject")))
        self.wait.until(EC.presence_of_element_located((By.NAME, "session")))

    def test_admin_notify_staff(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}admin_notify_staff")
        self.assert_page_title("Send Notifications To Staff")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Send Notification')]")))

    def test_admin_notify_student(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}admin_notify_student")
        self.assert_page_title("Send Notifications To Students")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Send Notification')]")))

    # --- Deletion Tests ---

    def test_delete_subject(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_course")
        self.driver.find_element(By.NAME, "name").send_keys(f"DelCourse {uuid.uuid4().hex[:8]}")
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_staff")
        unique_id = uuid.uuid4().hex[:8]
        self.driver.find_element(By.NAME, "first_name").send_keys(f"DelStaffF_{unique_id}")
        self.driver.find_element(By.NAME, "last_name").send_keys(f"DelStaffL_{unique_id}")
        self.driver.find_element(By.NAME, "email").send_keys(f"delsubject_staff_{unique_id}@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("password")
        self.driver.find_element(By.NAME, "address").send_keys("Staff Address")
        
        gender_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "gender")))
        gender_select.send_keys("Male")
        
        course_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "course")))
        course_select.find_elements(By.TAG_NAME, "option")[1].click()
        profile_pic_input = self.driver.find_element(By.NAME, "profile_pic")
        profile_pic_input.send_keys(os.path.abspath(TEMP_IMAGE_PATH))
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_subject")
        subject_name_to_delete = f"Subject_to_delete_{uuid.uuid4().hex[:8]}"
        self.driver.find_element(By.NAME, "name").send_keys(subject_name_to_delete)
        
        course_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "course")))
        course_select.find_elements(By.TAG_NAME, "option")[1].click()
        
        staff_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "staff")))
        staff_select.find_elements(By.TAG_NAME, "option")[1].click()
        
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}manage_subject")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//td[contains(text(), '{subject_name_to_delete}')]")))
        delete_link = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{subject_name_to_delete}')]/following-sibling::td/a[contains(@href, '/delete_subject/')]")
        delete_link.click()

        self.wait.until(EC.url_to_be(f"{BASE_URL}manage_subject"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Subject deleted successfully!')]")))
        self.assertFalse(any(subject_name_to_delete in e.text for e in self.driver.find_elements(By.TAG_NAME, "td")))

    def test_delete_staff(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_course")
        self.driver.find_element(By.NAME, "name").send_keys(f"Course For DelStaff {uuid.uuid4().hex[:8]}")
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_staff")
        unique_id = uuid.uuid4().hex[:8]
        staff_name_to_delete = f"Staff_to_delete_{unique_id}"
        staff_email_to_delete = f"delstaff_{unique_id}@example.com"
        self.driver.find_element(By.NAME, "first_name").send_keys(staff_name_to_delete)
        self.driver.find_element(By.NAME, "last_name").send_keys(f"DelStaffL_{unique_id}")
        self.driver.find_element(By.NAME, "email").send_keys(staff_email_to_delete)
        self.driver.find_element(By.NAME, "password").send_keys("password")
        self.driver.find_element(By.NAME, "address").send_keys("Staff Address")
        
        gender_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "gender")))
        gender_select.send_keys("Male")
        
        course_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "course")))
        course_select.find_elements(By.TAG_NAME, "option")[1].click()
        profile_pic_input = self.driver.find_element(By.NAME, "profile_pic")
        profile_pic_input.send_keys(os.path.abspath(TEMP_IMAGE_PATH))
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}manage_staff")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//td[contains(text(), '{staff_name_to_delete}')]")))
        delete_link = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{staff_name_to_delete}')]/following-sibling::td/a[contains(@href, '/delete_staff/')]")
        delete_link.click()

        self.wait.until(EC.url_to_be(f"{BASE_URL}manage_staff"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Staff deleted successfully!')]")))
        self.assertFalse(any(staff_name_to_delete in e.text for e in self.driver.find_elements(By.TAG_NAME, "td")))

    def test_delete_student(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_course")
        self.driver.find_element(By.NAME, "name").send_keys(f"Course For DelStudent {uuid.uuid4().hex[:8]}")
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_session")
        self.driver.find_element(By.NAME, "session_start").send_keys("2020-01-01")
        self.driver.find_element(By.NAME, "session_end").send_keys("2020-12-31")
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}add_student")
        unique_id = uuid.uuid4().hex[:8]
        student_name_to_delete = f"Student_to_delete_{unique_id}"
        student_email_to_delete = f"delstudent_{unique_id}@example.com"
        self.driver.find_element(By.NAME, "first_name").send_keys(student_name_to_delete)
        self.driver.find_element(By.NAME, "last_name").send_keys(f"DelStudentL_{unique_id}")
        self.driver.find_element(By.NAME, "email").send_keys(student_email_to_delete)
        self.driver.find_element(By.NAME, "password").send_keys("password")
        self.driver.find_element(By.NAME, "address").send_keys("Student Address")
        
        gender_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "gender")))
        gender_select.send_keys("Male")
        
        course_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "course")))
        course_select.find_elements(By.TAG_NAME, "option")[1].click()
        
        session_select = self.wait.until(EC.element_to_be_clickable((By.NAME, "session")))
        session_select.find_elements(By.TAG_NAME, "option")[1].click()
        
        profile_pic_input = self.driver.find_element(By.NAME, "profile_pic")
        profile_pic_input.send_keys(os.path.abspath(TEMP_IMAGE_PATH))
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}manage_student")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//td[contains(text(), '{student_name_to_delete}')]")))
        delete_link = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{student_name_to_delete}')]/following-sibling::td/a[contains(@href, '/delete_student/')]")
        delete_link.click()

        self.wait.until(EC.url_to_be(f"{BASE_URL}manage_student"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Student deleted successfully!')]")))
        self.assertFalse(any(student_name_to_delete in e.text for e in self.driver.find_elements(By.TAG_NAME, "td")))

    def test_delete_course(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_course")
        course_name_to_delete = f"Course_to_delete_{uuid.uuid4().hex[:8]}"
        self.driver.find_element(By.NAME, "name").send_keys(course_name_to_delete)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}manage_course")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//td[contains(text(), '{course_name_to_delete}')]")))
        delete_link = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{course_name_to_delete}')]/following-sibling::td/a[contains(@href, '/delete_course/')]")
        delete_link.click()

        self.wait.until(EC.url_to_be(f"{BASE_URL}manage_course"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Course deleted successfully!')]")))
        self.assertFalse(any(course_name_to_delete in e.text for e in self.driver.find_elements(By.TAG_NAME, "td")))

    def test_delete_session(self):
        self.login("admin")
        self.driver.get(f"{BASE_URL}add_session")
        session_start_to_delete = "2021-01-01"
        session_end_to_delete = "2021-12-31"
        self.driver.find_element(By.NAME, "session_start").send_keys(session_start_to_delete)
        self.driver.find_element(By.NAME, "session_end").send_keys(session_end_to_delete)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success')]")))

        self.driver.get(f"{BASE_URL}manage_session")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//td[contains(text(), '{session_start_to_delete}')]")))
        delete_link = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{session_start_to_delete}')]/following-sibling::td/a[contains(@href, '/delete_session/')]")
        delete_link.click()

        self.wait.until(EC.url_to_be(f"{BASE_URL}manage_session"))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Session deleted successfully!')]")))
        self.assertFalse(any(session_start_to_delete in e.text for e in self.driver.find_elements(By.TAG_NAME, "td")))

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)