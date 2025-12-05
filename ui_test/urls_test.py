import unittest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class TestStudentManagementSystem(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000/"

    CREDENTIALS = {
        "admin": {"email": "qasim@admin.com", "password": "admin"},
        "staff": {"email": "bill@ms.com", "password": "123"},
        "student": {"email": "qasim@nu.edu.pk", "password": "123"},
    }

    # URL paths mapped to their expected roles and if they are dynamic.
    # AJAX/API endpoints like 'get_attendance', 'doLogin', 'get_students', etc.,
    # are generally not tested for direct page loads, as they primarily serve data.
    # 'user_login' is implicitly tested by the _login method.
    URL_PATHS = [
        {"path": "", "name": "login_page", "role": "public"},
        {"path": "firebase-messaging-sw.js", "name": "showFirebaseJS", "role": "public"},
        {"path": "logout_user/", "name": "user_logout", "role": "public"}, # Accessed after login to logout

        # Admin (HOD) Views
        {"path": "admin/home/", "name": "admin_home", "role": "admin"},
        {"path": "staff/add", "name": "add_staff", "role": "admin"},
        {"path": "course/add", "name": "add_course", "role": "admin"},
        {"path": "send_student_notification/", "name": "send_student_notification", "role": "admin"},
        {"path": "send_staff_notification/", "name": "send_staff_notification", "role": "admin"},
        {"path": "add_session/", "name": "add_session", "role": "admin"},
        {"path": "admin_notify_student", "name": "admin_notify_student", "role": "admin"},
        {"path": "admin_notify_staff", "name": "admin_notify_staff", "role": "admin"},
        {"path": "admin_view_profile", "name": "admin_view_profile", "role": "admin"},
        {"path": "session/manage/", "name": "manage_session", "role": "admin"},
        {"path": "session/edit/<int:session_id>", "name": "edit_session", "role": "admin", "dynamic": True, "param": 1},
        {"path": "student/view/feedback/", "name": "student_feedback_message", "role": "admin"},
        {"path": "staff/view/feedback/", "name": "staff_feedback_message", "role": "admin"},
        {"path": "student/view/leave/", "name": "view_student_leave", "role": "admin"},
        {"path": "staff/view/leave/", "name": "view_staff_leave", "role": "admin"},
        {"path": "attendance/view/", "name": "admin_view_attendance", "role": "admin"},
        {"path": "student/add/", "name": "add_student", "role": "admin"},
        {"path": "subject/add/", "name": "add_subject", "role": "admin"},
        {"path": "staff/manage/", "name": "manage_staff", "role": "admin"},
        {"path": "student/manage/", "name": "manage_student", "role": "admin"},
        {"path": "course/manage/", "name": "manage_course", "role": "admin"},
        {"path": "subject/manage/", "name": "manage_subject", "role": "admin"},
        {"path": "staff/edit/<int:staff_id>", "name": "edit_staff", "role": "admin", "dynamic": True, "param": 1},
        {"path": "staff/delete/<int:staff_id>", "name": "delete_staff", "role": "admin", "dynamic": True, "param": 1},
        {"path": "course/delete/<int:course_id>", "name": "delete_course", "role": "admin", "dynamic": True, "param": 1},
        {"path": "subject/delete/<int:subject_id>", "name": "delete_subject", "role": "admin", "dynamic": True, "param": 1},
        {"path": "session/delete/<int:session_id>", "name": "delete_session", "role": "admin", "dynamic": True, "param": 1},
        {"path": "student/delete/<int:student_id>", "name": "delete_student", "role": "admin", "dynamic": True, "param": 1},
        {"path": "student/edit/<int:student_id>", "name": "edit_student", "role": "admin", "dynamic": True, "param": 1},
        {"path": "course/edit/<int:course_id>", "name": "edit_course", "role": "admin", "dynamic": True, "param": 1},
        {"path": "subject/edit/<int:subject_id>", "name": "edit_subject", "role": "admin", "dynamic": True, "param": 1},

        # Staff Views
        {"path": "staff/home/", "name": "staff_home", "role": "staff"},
        {"path": "staff/apply/leave/", "name": "staff_apply_leave", "role": "staff"},
        {"path": "staff/feedback/", "name": "staff_feedback", "role": "staff"},
        {"path": "staff/view/profile/", "name": "staff_view_profile", "role": "staff"},
        {"path": "staff/attendance/take/", "name": "staff_take_attendance", "role": "staff"},
        {"path": "staff/attendance/update/", "name": "staff_update_attendance", "role": "staff"}, # This is an update page, not an AJAX endpoint based on path.
        {"path": "staff/view/notification/", "name": "staff_view_notification", "role": "staff"},
        {"path": "staff/result/add/", "name": "staff_add_result", "role": "staff"},
        {"path": "staff/result/edit/", "name": "edit_student_result", "role": "staff"}, # This is EditResultView.as_view()

        # Student Views
        {"path": "student/home/", "name": "student_home", "role": "student"},
        {"path": "student/view/attendance/", "name": "student_view_attendance", "role": "student"},
        {"path": "student/apply/leave/", "name": "student_apply_leave", "role": "student"},
        {"path": "student/feedback/", "name": "student_feedback", "role": "student"},
        {"path": "student/view/profile/", "name": "student_view_profile", "role": "student"},
        {"path": "student/view/notification/", "name": "student_view_notification", "role": "student"},
        {"path": "student/view/result/", "name": "student_view_result", "role": "student"},
    ]

    def setUp(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")

        # Initialize WebDriver. Selenium Manager automatically handles chromedriver.
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10) # Set a general implicit wait

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def _login(self, user_role):
        """Logs in a user based on their role and waits for dashboard redirection."""
        credentials = self.CREDENTIALS.get(user_role)
        if not credentials:
            raise ValueError(f"Unknown user role: {user_role}")

        self.driver.get(self.BASE_URL)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        email_input = self.driver.find_element(By.NAME, "email")
        password_input = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        email_input.send_keys(credentials["email"])
        password_input.send_keys(credentials["password"])
        login_button.click()

        try:
            # Wait for redirection to a specific home page based on role
            if user_role == "admin":
                WebDriverWait(self.driver, 10).until(EC.url_contains("/admin/home"))
            elif user_role == "staff":
                WebDriverWait(self.driver, 10).until(EC.url_contains("/staff/home"))
            elif user_role == "student":
                WebDriverWait(self.driver, 10).until(EC.url_contains("/student/home"))
            else:
                # Fallback for unexpected roles, just wait for any body content
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            return True
        except TimeoutException:
            self.fail(f"Failed to log in as {user_role}. Current URL: {self.driver.current_url}, Page source: {self.driver.page_source[:500]}")

    def _logout(self):
        """Logs out the current user and waits for redirection to the login page."""
        try:
            self.driver.get(self.BASE_URL + "logout_user/")
            WebDriverWait(self.driver, 10).until(
                EC.url_to_be(self.BASE_URL)
            )
        except TimeoutException:
            # Log a warning if logout doesn't redirect as expected, but don't fail the test
            print(f"Warning: Logout might not have redirected to login page. Current URL: {self.driver.current_url}")
        except Exception as e:
            print(f"Error during logout: {e}")

    def _test_page_load(self, url_info):
        """Generic test method to check if a page loads correctly with the appropriate user role."""
        path = url_info["path"]
        name = url_info["name"]
        role = url_info["role"]
        is_dynamic = url_info.get("dynamic", False)
        param = url_info.get("param")

        if is_dynamic and param is not None:
            # Replace the dynamic part (e.g., <int:session_id>) with the placeholder parameter
            # This assumes the parameter name is consistent within the <int:...> pattern
            dynamic_segment = path.split('<int:')[1].split('>')[0]
            full_path = path.replace(f"<int:{dynamic_segment}>", str(param))
        else:
            full_path = path

        test_url = self.BASE_URL + full_path
        print(f"Testing {name} ({test_url}) as {role}...")

        # Perform login if the path requires a specific role
        if role != "public":
            self._login(role)
            # Ensure the login was successful before navigating to the specific test_url
            if not self.driver.current_url.startswith(self.BASE_URL):
                 self.fail(f"Login failed for {role} before attempting to access {name}.")
        else:
            # For public paths, ensure we are not logged in or navigate directly
            if self.driver.current_url != self.BASE_URL: # If currently logged in, log out first.
                 self._logout()
            self.driver.get(self.BASE_URL) # Always start public tests from base URL to ensure clean state.


        try:
            self.driver.get(test_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Check for common error indicators or unexpected redirections
            if "Page Not Found" in self.driver.title or "Error" in self.driver.title or "Internal Server Error" in self.driver.page_source:
                self.fail(f"'{name}' page ({test_url}) returned an error or 'Page Not Found' as {role}. Title: '{self.driver.title}'. Source contains: {self.driver.page_source[:500]}")
            
            # If the current URL is still the login page for a non-public, non-login path, it's a failure
            if self.driver.current_url == self.BASE_URL and name != "login_page" and role != "public":
                self.fail(f"'{name}' page ({test_url}) redirected unexpectedly to login page for {role}.")

            # Assert that the page loaded some content (basic check for non-empty page)
            self.assertGreater(len(self.driver.page_source), 50, f"Page {name} ({test_url}) loaded with very little content (likely an error or blank page) as {role}.")
            print(f"  --> {name} as {role} loaded successfully.")

        except TimeoutException:
            self.fail(f"Timeout while loading '{name}' ({test_url}) as {role}. Current URL: {self.driver.current_url}. Page source (first 500 chars): {self.driver.page_source[:500]}")
        except NoSuchElementException:
            self.fail(f"Required element not found on '{name}' ({test_url}) as {role}. Current URL: {self.driver.current_url}. Page source (first 500 chars): {self.driver.page_source[:500]}")
        except WebDriverException as e:
            self.fail(f"WebDriver error accessing '{name}' ({test_url}) as {role}: {e}")
        finally:
            # Log out only if a user was logged in for the test
            if role != "public":
                self._logout()

# Dynamically generate test methods for each URL path
for url_info in TestStudentManagementSystem.URL_PATHS:
    path_name = url_info["name"]
    role = url_info["role"]
    # Create a descriptive and valid Python method name
    method_name = f"test_{role}_{path_name.replace('/', '_').replace('-', '_').replace(' ', '_').replace('.', '_')}_page_load"
    
    # Ensure method name is unique (though unlikely with path_name)
    counter = 1
    original_method_name = method_name
    while hasattr(TestStudentManagementSystem, method_name):
        method_name = f"{original_method_name}_{counter}"
        counter += 1

    # Attach the dynamically created test method to the class
    # Using a lambda closure to capture the current url_info for each test
    setattr(TestStudentManagementSystem, method_name, 
            (lambda current_url_info=url_info: 
             lambda self: self._test_page_load(current_url_info))(url_info))

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)