import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/"

STUDENT_EMAIL = "qasim@nu.edu.pk"
STUDENT_PASSWORD = "123"

class StudentViewTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.driver.get(BASE_URL)
        self.login_as_student()

    def login_as_student(self):
        driver = self.driver
        
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        email_field.send_keys(STUDENT_EMAIL)
        password_field.send_keys(STUDENT_PASSWORD)
        login_button.click()

        WebDriverWait(driver, 10).until(
            EC.url_contains("/student/home/")
        )

    def get_messages(self):
        try:
            message_elements = self.driver.find_elements(By.CSS_SELECTOR, '.alert, .messages li')
            return [msg.text for msg in message_elements if msg.is_displayed()]
        except:
            return []

    def test_student_home(self):
        driver = self.driver
        driver.get(BASE_URL + "student/home/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        self.assertIn("Student Homepage", driver.page_source)
        self.assertTrue(driver.find_element(By.ID, "total_subject_count").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "total_attendance_count").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "present_percent").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "absent_percent").is_displayed())

    def test_student_view_attendance_get(self):
        driver = self.driver
        driver.get(BASE_URL + "student/view_attendance/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        self.assertIn("View Attendance", driver.page_source)
        self.assertTrue(driver.find_element(By.NAME, "subject").is_displayed())
        self.assertTrue(driver.find_element(By.NAME, "start_date").is_displayed())
        self.assertTrue(driver.find_element(By.NAME, "end_date").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "fetch_attendance_btn").is_displayed())

    def test_student_view_attendance_post(self):
        driver = self.driver
        driver.get(BASE_URL + "student/view_attendance/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "subject")))

        subject_select_element = Select(driver.find_element(By.NAME, "subject"))
        subject_select_element.select_by_index(1) 

        start_date_field = driver.find_element(By.NAME, "start_date")
        end_date_field = driver.find_element(By.NAME, "end_date")

        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        start_date_field.send_keys(thirty_days_ago.strftime("%Y-%m-%d"))
        end_date_field.send_keys(today.strftime("%Y-%m-%d"))

        fetch_button = driver.find_element(By.ID, "fetch_attendance_btn")
        fetch_button.click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "pre")))
        page_content = driver.find_element(By.TAG_NAME, "pre").text
        self.assertIn("{", page_content)
        self.assertIn("date", page_content)
        self.assertIn("status", page_content)

    def test_student_apply_leave_get(self):
        driver = self.driver
        driver.get(BASE_URL + "student/apply_leave/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        self.assertIn("Apply for leave", driver.page_source)
        self.assertTrue(driver.find_element(By.ID, "id_start_date").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "id_end_date").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "id_reason").is_displayed())
        self.assertTrue(driver.find_element(By.XPATH, "//button[@type='submit']").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "leave_history_table").is_displayed())

    def test_student_apply_leave_post(self):
        driver = self.driver
        driver.get(BASE_URL + "student/apply_leave/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id_reason")))

        start_date_field = driver.find_element(By.ID, "id_start_date")
        end_date_field = driver.find_element(By.ID, "id_end_date")
        reason_field = driver.find_element(By.ID, "id_reason")
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        tomorrow = datetime.now() + timedelta(days=1)
        day_after_tomorrow = datetime.now() + timedelta(days=2)
        start_date_field.send_keys(tomorrow.strftime("%Y-%m-%d"))
        end_date_field.send_keys(day_after_tomorrow.strftime("%Y-%m-%d"))
        reason_field.send_keys("Family emergency leave test.")
        
        submit_button.click()

        WebDriverWait(driver, 10).until(EC.url_contains("/student/apply_leave/"))
        messages = self.get_messages()
        self.assertIn("Application for leave has been submitted for review", messages)

    def test_student_feedback_get(self):
        driver = self.driver
        driver.get(BASE_URL + "student/feedback/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        self.assertIn("Student Feedback", driver.page_source)
        self.assertTrue(driver.find_element(By.ID, "id_feedback").is_displayed())
        self.assertTrue(driver.find_element(By.XPATH, "//button[@type='submit']").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "feedback_history_table").is_displayed())

    def test_student_feedback_post(self):
        driver = self.driver
        driver.get(BASE_URL + "student/feedback/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id_feedback")))

        feedback_field = driver.find_element(By.ID, "id_feedback")
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        feedback_field.send_keys("This is a test feedback message from Selenium.")
        submit_button.click()

        WebDriverWait(driver, 10).until(EC.url_contains("/student/feedback/"))
        messages = self.get_messages()
        self.assertIn("Feedback submitted for review", messages)

    def test_student_view_profile_get(self):
        driver = self.driver
        driver.get(BASE_URL + "student/profile/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        self.assertIn("View/Edit Profile", driver.page_source)
        self.assertTrue(driver.find_element(By.ID, "id_first_name").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "id_last_name").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "id_address").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "id_gender").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "id_password").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "id_profile_pic").is_displayed())
        self.assertTrue(driver.find_element(By.XPATH, "//button[@type='submit']").is_displayed())

        first_name_value = driver.find_element(By.ID, "id_first_name").get_attribute("value")
        self.assertIsNotNone(first_name_value)

    def test_student_view_profile_post(self):
        driver = self.driver
        driver.get(BASE_URL + "student/profile/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id_address")))

        address_field = driver.find_element(By.ID, "id_address")
        gender_select = Select(driver.find_element(By.ID, "id_gender"))
        profile_pic_input = driver.find_element(By.ID, "id_profile_pic")
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        new_address = f"123 Test Street, Seleniumville {datetime.now().strftime('%H%M%S')}"
        address_field.clear()
        address_field.send_keys(new_address)

        current_gender = gender_select.first_selected_option.get_attribute("value")
        if current_gender == "Male":
            gender_select.select_by_value("Female")
        else:
            gender_select.select_by_value("Male")

        dummy_file_path = os.path.join(os.path.dirname(__file__), "dummy_profile.png")
        if not os.path.exists(dummy_file_path):
            with open(dummy_file_path, "w") as f:
                f.write("This is a dummy file for testing purposes.")
        profile_pic_input.send_keys(dummy_file_path)

        submit_button.click()

        WebDriverWait(driver, 10).until(EC.url_contains("/student/profile/"))
        messages = self.get_messages()
        self.assertIn("Profile Updated!", messages)

    def test_student_fcmtoken(self):
        driver = self.driver
        driver.get(BASE_URL + "student/home/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        script = """
        return fetch('/student/fcmtoken/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'token=test_fcm_token_12345'
        }).then(response => response.text());
        """
        response_text = driver.execute_script(script)
        self.assertEqual(response_text.strip(), "True")

    def test_student_view_notification(self):
        driver = self.driver
        driver.get(BASE_URL + "student/notification/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        self.assertIn("View Notifications", driver.page_source)
        self.assertTrue(driver.find_element(By.ID, "notification_list").is_displayed())

    def test_student_view_result(self):
        driver = self.driver
        driver.get(BASE_URL + "student/result/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        self.assertIn("View Results", driver.page_source)
        self.assertTrue(driver.find_element(By.ID, "result_table").is_displayed())

if __name__ == '__main__':
    dummy_file_path = os.path.join(os.path.dirname(__file__), "dummy_profile.png")
    if not os.path.exists(dummy_file_path):
        with open(dummy_file_path, "w") as f:
            f.write("This is a dummy file for testing purposes.")
    