// cypress/e2e/school_management.cy.js

const BASE_URL = 'http://127.0.0.1:8000';

const login = (email, password) => {
  cy.visit(`${BASE_URL}/login/`);
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="password"]').type(password);
  cy.get('button[type="submit"]').click();
};

const logout = () => {
  cy.visit(`${BASE_URL}/logout/`);
  cy.url().should('include', '/login');
};

describe('School Management System E2E Tests', () => {

  // --- Admin User Functionality ---
  describe('Admin User Functionality', () => {
    const adminEmail = 'qasim@admin.com';
    const adminPassword = 'admin';

    beforeEach(() => {
      login(adminEmail, adminPassword);
      cy.url().should('include', '/admin_dashboard');
    });

    afterEach(() => {
      logout();
    });

    it('should allow admin to login and logout successfully', () => {
      cy.contains('h1', 'Admin Dashboard').should('be.visible');
    });

    it('should allow admin to manage sessions (create, view)', () => {
      cy.visit(`${BASE_URL}/admin/sessions/`);
      cy.contains('h1', 'Manage Sessions').should('be.visible');

      cy.get('a').contains('Add New Session').click();
      cy.url().should('include', '/admin/sessions/add/');
      cy.get('input[name="start_year"]').type('2023-09-01');
      cy.get('input[name="end_year"]').type('2024-06-30');
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/admin/sessions/');
      cy.contains('From 2023-09-01 to 2024-06-30').should('be.visible');
    });

    it('should allow admin to manage courses (create, view)', () => {
      cy.visit(`${BASE_URL}/admin/courses/`);
      cy.contains('h1', 'Manage Courses').should('be.visible');

      cy.get('a').contains('Add New Course').click();
      cy.url().should('include', '/admin/courses/add/');
      cy.get('input[name="name"]').type('Computer Science');
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/admin/courses/');
      cy.contains('Computer Science').should('be.visible');
    });

    it('should allow admin to manage staff (create, view)', () => {
      cy.visit(`${BASE_URL}/admin/staff/`);
      cy.contains('h1', 'Manage Staff').should('be.visible');

      cy.get('a').contains('Add New Staff').click();
      cy.url().should('include', '/admin/staff/add/');
      cy.get('input[name="first_name"]').type('John');
      cy.get('input[name="last_name"]').type('Doe');
      cy.get('input[name="email"]').type('john.doe@example.com');
      cy.get('input[name="password"]').type('staffpass');
      cy.get('input[name="address"]').type('123 Staff Street');
      cy.get('select[name="gender"]').select('M');
      cy.get('input[type="file"][name="profile_pic"]').selectFile('cypress/fixtures/profile.jpg');
      cy.get('select[name="course"]').select('Computer Science');
      cy.get('button[type="submit"]').click();

      cy.url().should('include', '/admin/staff/');
      cy.contains('John Doe').should('be.visible');
      cy.contains('john.doe@example.com').should('be.visible');
    });

    it('should allow admin to manage students (create, view)', () => {
      cy.visit(`${BASE_URL}/admin/students/`);
      cy.contains('h1', 'Manage Students').should('be.visible');

      cy.get('a').contains('Add New Student').click();
      cy.url().should('include', '/admin/students/add/');
      cy.get('input[name="first_name"]').type('Jane');
      cy.get('input[name="last_name"]').type('Smith');
      cy.get('input[name="email"]').type('jane.smith@example.com');
      cy.get('input[name="password"]').type('studentpass');
      cy.get('input[name="address"]').type('456 Student Avenue');
      cy.get('select[name="gender"]').select('F');
      cy.get('input[type="file"][name="profile_pic"]').selectFile('cypress/fixtures/profile.jpg');
      cy.get('select[name="course"]').select('Computer Science');
      cy.get('select[name="session"]').select('From 2023-09-01 to 2024-06-30');
      cy.get('button[type="submit"]').click();

      cy.url().should('include', '/admin/students/');
      cy.contains('Jane Smith').should('be.visible');
      cy.contains('jane.smith@example.com').should('be.visible');
    });

    it('should allow admin to manage subjects (create, view)', () => {
      cy.visit(`${BASE_URL}/admin/subjects/`);
      cy.contains('h1', 'Manage Subjects').should('be.visible');

      cy.get('a').contains('Add New Subject').click();
      cy.url().should('include', '/admin/subjects/add/');
      cy.get('input[name="name"]').type('Introduction to Programming');
      cy.get('select[name="course"]').select('Computer Science');
      cy.get('select[name="staff"]').select('John Doe');
      cy.get('button[type="submit"]').click();

      cy.url().should('include', '/admin/subjects/');
      cy.contains('Introduction to Programming').should('be.visible');
    });

    it('should allow admin to approve staff leave requests', () => {
      cy.visit(`${BASE_URL}/admin/staff_leave_requests/`);
      cy.contains('h1', 'Staff Leave Requests').should('be.visible');

      cy.contains('tr', 'John Doe')
        .find('button').contains('Approve').click();

      cy.contains('Leave request approved successfully').should('be.visible');
    });

    it('should allow admin to reply to staff feedback', () => {
      cy.visit(`${BASE_URL}/admin/staff_feedback/`);
      cy.contains('h1', 'Staff Feedback').should('be.visible');

      cy.contains('tr', 'John Doe')
        .find('a').contains('Reply').click();

      cy.url().should('include', '/admin/staff_feedback/reply/');
      cy.get('textarea[name="reply_message"]').type('Thank you for your feedback, John.');
      cy.get('button[type="submit"]').click();

      cy.url().should('include', '/admin/staff_feedback/');
      cy.contains('Feedback replied successfully').should('be.visible');
    });

    it('should allow admin to send a notification to staff', () => {
      cy.visit(`${BASE_URL}/admin/send_notification_staff/`);
      cy.contains('h1', 'Send Staff Notification').should('be.visible');
      cy.get('select[name="staff"]').select('John Doe');
      cy.get('textarea[name="message"]').type('Important meeting tomorrow at 10 AM.');
      cy.get('button[type="submit"]').click();
      cy.contains('Notification sent successfully').should('be.visible');
    });

    it('should allow admin to send a notification to students', () => {
      cy.visit(`${BASE_URL}/admin/send_notification_student/`);
      cy.contains('h1', 'Send Student Notification').should('be.visible');
      cy.get('select[name="student"]').select('Jane Smith');
      cy.get('textarea[name="message"]').type('Reminder: Project submission deadline is Friday.');
      cy.get('button[type="submit"]').click();
      cy.contains('Notification sent successfully').should('be.visible');
    });
  });

  // --- Staff User Functionality ---
  describe('Staff User Functionality', () => {
    const staffEmail = 'bill@ms.com';
    const staffPassword = '123';

    beforeEach(() => {
      login(staffEmail, staffPassword);
      cy.url().should('include', '/staff_dashboard');
    });

    afterEach(() => {
      logout();
    });

    it('should allow staff to login and logout successfully', () => {
      cy.contains('h1', 'Staff Dashboard').should('be.visible');
    });

    it('should allow staff to view assigned subjects', () => {
      cy.visit(`${BASE_URL}/staff/subjects/`);
      cy.contains('h1', 'My Subjects').should('be.visible');
      cy.contains('Introduction to Programming').should('be.visible');
    });

    it('should allow staff to mark student attendance', () => {
      cy.visit(`${BASE_URL}/staff/mark_attendance/`);
      cy.contains('h1', 'Mark Attendance').should('be.visible');

      cy.get('select[name="subject"]').select('Introduction to Programming');
      cy.get('select[name="session"]').select('From 2023-09-01 to 2024-06-30');
      cy.get('input[name="date"]').type('2024-01-15');
      cy.get('button').contains('Load Students').click();

      cy.get('input[name="attendance_status_jane.smith@example.com"]').check();
      cy.get('button[type="submit"]').click();

      cy.contains('Attendance marked successfully').should('be.visible');
    });

    it('should allow staff to add/update student results', () => {
      cy.visit(`${BASE_URL}/staff/student_results/`);
      cy.contains('h1', 'Manage Student Results').should('be.visible');

      cy.get('a').contains('Add New Result').click();
      cy.url().should('include', '/staff/student_results/add/');
      cy.get('select[name="student"]').select('Jane Smith');
      cy.get('select[name="subject"]').select('Introduction to Programming');
      cy.get('input[name="test"]').type('85');
      cy.get('input[name="exam"]').type('92');
      cy.get('button[type="submit"]').click();

      cy.url().should('include', '/staff/student_results/');
      cy.contains('Jane Smith').should('be.visible');
      cy.contains('Introduction to Programming').should('be.visible');
      cy.contains('85').should('be.visible');
      cy.contains('92').should('be.visible');
    });

    it('should allow staff to apply for leave', () => {
      cy.visit(`${BASE_URL}/staff/apply_leave/`);
      cy.contains('h1', 'Apply for Leave').should('be.visible');

      cy.get('input[name="date"]').type('2024-02-01');
      cy.get('textarea[name="message"]').type('Feeling unwell, requesting a day off.');
      cy.get('button[type="submit"]').click();

      cy.contains('Leave request submitted successfully').should('be.visible');
      cy.url().should('include', '/staff/leave_status/');
    });

    it('should allow staff to send feedback', () => {
      cy.visit(`${BASE_URL}/staff/send_feedback/`);
      cy.contains('h1', 'Send Feedback').should('be.visible');

      cy.get('textarea[name="feedback_message"]').type('Suggestion for improving attendance system.');
      cy.get('button[type="submit"]').click();

      cy.contains('Feedback submitted successfully').should('be.visible');
      cy.url().should('include', '/staff/feedback_status/');
    });

    it('should allow staff to view notifications', () => {
      cy.visit(`${BASE_URL}/staff/notifications/`);
      cy.contains('h1', 'My Notifications').should('be.visible');
      cy.contains('Important meeting tomorrow at 10 AM.').should('be.visible');
    });
  });

  // --- Student User Functionality ---
  describe('Student User Functionality', () => {
    const studentEmail = 'qasim@nu.edu.pk';
    const studentPassword = '123';

    beforeEach(() => {
      login(studentEmail, studentPassword);
      cy.url().should('include', '/student_dashboard');
    });

    afterEach(() => {
      logout();
    });

    it('should allow student to login and logout successfully', () => {
      cy.contains('h1', 'Student Dashboard').should('be.visible');
    });

    it('should allow student to view their attendance report', () => {
      cy.visit(`${BASE_URL}/student/attendance_report/`);
      cy.contains('h1', 'My Attendance').should('be.visible');
      cy.contains('Introduction to Programming').should('be.visible');
      cy.contains('2024-01-15').should('be.visible');
      cy.contains('Present').should('be.visible');
    });

    it('should allow student to view their results', () => {
      cy.visit(`${BASE_URL}/student/my_results/`);
      cy.contains('h1', 'My Results').should('be.visible');
      cy.contains('Introduction to Programming').should('be.visible');
      cy.contains('Test: 85').should('be.visible');
      cy.contains('Exam: 92').should('be.visible');
    });

    it('should allow student to apply for leave', () => {
      cy.visit(`${BASE_URL}/student/apply_leave/`);
      cy.contains('h1', 'Apply for Leave').should('be.visible');

      cy.get('input[name="date"]').type('2024-03-05');
      cy.get('textarea[name="message"]').type('Feeling unwell, requesting a day off.');
      cy.get('button[type="submit"]').click();

      cy.contains('Leave request submitted successfully').should('be.visible');
      cy.url().should('include', '/student/leave_status/');
    });

    it('should allow student to send feedback', () => {
      cy.visit(`${BASE_URL}/student/send_feedback/`);
      cy.contains('h1', 'Send Feedback').should('be.visible');

      cy.get('textarea[name="feedback_message"]').type('Regarding course material difficulty.');
      cy.get('button[type="submit"]').click();

      cy.contains('Feedback submitted successfully').should('be.visible');
      cy.url().should('include', '/student/feedback_status/');
    });

    it('should allow student to view notifications', () => {
      cy.visit(`${BASE_URL}/student/notifications/`);
      cy.contains('h1', 'My Notifications').should('be.visible');
      cy.contains('Reminder: Project submission deadline is Friday.').should('be.visible');
    });
  });
});