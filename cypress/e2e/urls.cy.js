const BASE_URL = 'http://127.0.0.1:8000';

const ADMIN_CREDENTIALS = {
  email: 'qasim@admin.com',
  password: 'admin',
  homePath: '/admin/home/',
};

const STAFF_CREDENTIALS = {
  email: 'bill@ms.com',
  password: '123',
  homePath: '/staff/home/',
};

const STUDENT_CREDENTIALS = {
  email: 'qasim@nu.edu.pk',
  password: '123',
  homePath: '/student/home/',
};

/**
 * Custom Cypress command to log in a user.
 * Utilizes `cy.session` for efficient caching of login state across tests.
 * @param {string} email - The user's email for login.
 * @param {string} password - The user's password for login.
 * @param {string} expectedHomePath - The expected URL path after successful login.
 */
Cypress.Commands.add('login', (email, password, expectedHomePath) => {
  cy.session([email, password], () => {
    cy.visit(`${BASE_URL}/`);
    cy.get('input#id_email').type(email);
    cy.get('input#id_password').type(password);
    cy.get('button[type="submit"]').click();
    cy.url().should('eq', `${BASE_URL}${expectedHomePath}`);
  });
});

/**
 * Custom Cypress command to log out the current user.
 * Assumes the logout URL redirects back to the login page.
 */
Cypress.Commands.add('logout', () => {
  cy.visit(`${BASE_URL}/logout_user/`);
  cy.url().should('eq', `${BASE_URL}/`); // Should redirect back to the login page
  cy.get('input#id_email').should('be.visible'); // Check for login form presence
});

describe('Public and Authentication Tests', () => {
  it('should display the login page correctly', () => {
    cy.visit(`${BASE_URL}/`);
    cy.url().should('eq', `${BASE_URL}/`);
    cy.get('h1').should('contain', 'Login'); // Assuming an H1 element contains "Login"
    cy.get('input#id_email').should('be.visible');
    cy.get('input#id_password').should('be.visible');
    cy.get('button[type="submit"]').should('be.visible');
  });

  it('should successfully log in Admin user and redirect to admin home', () => {
    cy.login(ADMIN_CREDENTIALS.email, ADMIN_CREDENTIALS.password, ADMIN_CREDENTIALS.homePath);
    cy.url().should('eq', `${BASE_URL}${ADMIN_CREDENTIALS.homePath}`);
    cy.logout(); // Logout after specific login test
  });

  it('should successfully log in Staff user and redirect to staff home', () => {
    cy.login(STAFF_CREDENTIALS.email, STAFF_CREDENTIALS.password, STAFF_CREDENTIALS.homePath);
    cy.url().should('eq', `${BASE_URL}${STAFF_CREDENTIALS.homePath}`);
    cy.logout(); // Logout after specific login test
  });

  it('should successfully log in Student user and redirect to student home', () => {
    cy.login(STUDENT_CREDENTIALS.email, STUDENT_CREDENTIALS.password, STUDENT_CREDENTIALS.homePath);
    cy.url().should('eq', `${BASE_URL}${STUDENT_CREDENTIALS.homePath}`);
    cy.logout(); // Logout after specific login test
  });

  it('should handle incorrect login credentials', () => {
    // This test intentionally skips cy.session to test a failed login scenario
    cy.visit(`${BASE_URL}/`);
    cy.get('input#id_email').type('invalid@example.com');
    cy.get('input#id_password').type('wrongpassword');
    cy.get('button[type="submit"]').click();
    cy.url().should('eq', `${BASE_URL}/`); // Should remain on the login page
    cy.get('.alert-danger, .errorlist').should('be.visible').and('contain', 'Invalid Login Details'); // Generic error message selector
  });

  it('should access firebase-messaging-sw.js (static file)', () => {
    cy.request(`${BASE_URL}/firebase-messaging-sw.js`).its('status').should('eq', 200);
    cy.request(`${BASE_URL}/firebase-messaging-sw.js`).its('headers').its('content-type').should('include', 'javascript');
  });

  it('should access get_attendance (API endpoint)', () => {
    cy.request(`${BASE_URL}/get_attendance`).its('status').should('eq', 200);
    // Further assertions could check JSON structure if known, e.g., .its('body').should('be.an', 'object')
  });

  it('should access check_email_availability (API endpoint)', () => {
    // Requires a query parameter for a meaningful response
    cy.request(`${BASE_URL}/check_email_availability?email=test@example.com`).its('status').should('eq', 200);
  });
});

describe('Admin (HOD) Module Tests', () => {
  // Log in once before all Admin tests in this block
  before(() => {
    cy.login(ADMIN_CREDENTIALS.email, ADMIN_CREDENTIALS.password, ADMIN_CREDENTIALS.homePath);
  });

  // Log out once after all Admin tests in this block
  after(() => {
    cy.logout();
  });

  const adminPaths = [
    { path: '/admin/home/', name: 'Admin Home' },
    { path: '/staff/add', name: 'Add Staff' },
    { path: '/course/add', name: 'Add Course' },
    { path: '/send_student_notification/', name: 'Send Student Notification' },
    { path: '/send_staff_notification/', name: 'Send Staff Notification' },
    { path: '/add_session/', name: 'Add Session' },
    { path: '/admin_notify_student', name: 'Admin Notify Student (Action)' }, // May redirect if GET not allowed
    { path: '/admin_notify_staff', name: 'Admin Notify Staff (Action)' }, // May redirect if GET not allowed
    { path: '/admin_view_profile', name: 'Admin View Profile' },
    { path: '/session/manage/', name: 'Manage Session' },
    { path: '/session/edit/1', name: 'Edit Session (ID 1)' }, // Using a dummy ID
    { path: '/student/view/feedback/', name: 'Student Feedback Messages' },
    { path: '/staff/view/feedback/', name: 'Staff Feedback Messages' },
    { path: '/student/view/leave/', name: 'Student Leave Applications' },
    { path: '/staff/view/leave/', name: 'Staff Leave Applications' },
    { path: '/attendance/view/', name: 'View Attendance' },
    { path: '/attendance/fetch/', name: 'Get Admin Attendance (API)' },
    { path: '/student/add/', name: 'Add Student' },
    { path: '/subject/add/', name: 'Add Subject' },
    { path: '/staff/manage/', name: 'Manage Staff' },
    { path: '/student/manage/', name: 'Manage Student' },
    { path: '/course/manage/', name: 'Manage Course' },
    { path: '/subject/manage/', name: 'Manage Subject' },
    { path: '/staff/edit/1', name: 'Edit Staff (ID 1)' },
    { path: '/staff/delete/1', name: 'Delete Staff (ID 1)' }, // Visiting might trigger action or confirmation
    { path: '/course/delete/1', name: 'Delete Course (ID 1)' },
    { path: '/subject/delete/1', name: 'Delete Subject (ID 1)' },
    { path: '/session/delete/1', name: 'Delete Session (ID 1)' },
    { path: '/student/delete/1', name: 'Delete Student (ID 1)' },
    { path: '/student/edit/1', name: 'Edit Student (ID 1)' },
    { path: '/course/edit/1', name: 'Edit Course (ID 1)' },
    { path: '/subject/edit/1', name: 'Edit Subject (ID 1)' },
  ];

  adminPaths.forEach(({ path, name }) => {
    it(`should successfully load/handle "${name}" page/action`, () => {
      if (name.includes('(API)')) {
        cy.request(`${BASE_URL}${path}`).its('status').should('eq', 200);
      } else if (path.includes('/delete/')) {
        cy.visit(`${BASE_URL}${path}`);
        // Expect deletion actions to redirect away from the delete URL, or show a confirmation
        cy.url().should('not.include', path);
        // A more robust test would check for a success message or specific redirect target
      } else if (name.includes('(Action)')) { // For admin_notify_student/staff
        cy.visit(`${BASE_URL}${path}`);
        // These are likely POST handlers. Visiting as GET might redirect or show an error.
        // Assert that it either stays on the path, redirects to the home page, or an error page.
        cy.url().should('not.eq', `${BASE_URL}/`); // Should not just redirect to login
        cy.url().should('include', path)
          .or('eq', `${BASE_URL}${ADMIN_CREDENTIALS.homePath}`)
          .or('include', '/error'); // Or to home if it's a "back" redirect.
      } else {
        cy.visit(`${BASE_URL}${path}`);
        cy.url().should('include', path);
        cy.get('body').should('be.visible'); // Basic check for content rendering
      }
    });
  });
});

describe('Staff Module Tests', () => {
  before(() => {
    cy.login(STAFF_CREDENTIALS.email, STAFF_CREDENTIALS.password, STAFF_CREDENTIALS.homePath);
  });

  after(() => {
    cy.logout();
  });

  const staffPaths = [
    { path: '/staff/home/', name: 'Staff Home' },
    { path: '/staff/apply/leave/', name: 'Staff Apply Leave' },
    { path: '/staff/feedback/', name: 'Staff Feedback' },
    { path: '/staff/view/profile/', name: 'Staff View Profile' },
    { path: '/staff/attendance/take/', name: 'Staff Take Attendance' },
    // staff_update_attendance (POST), save_attendance (POST), update_attendance (POST) are skipped for direct GET visit
    { path: '/staff/get_students/', name: 'Get Students (API)' },
    { path: '/staff/attendance/fetch/', name: 'Get Student Attendance (API)' },
    { path: '/staff/fcmtoken/', name: 'Staff FCM Token (API)' },
    { path: '/staff/view/notification/', name: 'Staff View Notification' },
    { path: '/staff/result/add/', name: 'Staff Add Result' },
    { path: '/staff/result/edit/', name: 'Staff Edit Result' }, // Class-based view, might need ID or form
    { path: '/staff/result/fetch/', name: 'Fetch Student Result (API)' },
  ];

  staffPaths.forEach(({ path, name }) => {
    it(`should successfully load/handle "${name}" page/action`, () => {
      if (name.includes('(API)')) {
        cy.request(`${BASE_URL}${path}`).its('status').should('eq', 200);
      } else {
        cy.visit(`${BASE_URL}${path}`);
        cy.url().should('include', path);
        cy.get('body').should('be.visible');
      }
    });
  });
});

describe('Student Module Tests', () => {
  before(() => {
    cy.login(STUDENT_CREDENTIALS.email, STUDENT_CREDENTIALS.password, STUDENT_CREDENTIALS.homePath);
  });

  after(() => {
    cy.logout();
  });

  const studentPaths = [
    { path: '/student/home/', name: 'Student Home' },
    { path: '/student/view/attendance/', name: 'Student View Attendance' },
    { path: '/student/apply/leave/', name: 'Student Apply Leave' },
    { path: '/student/feedback/', name: 'Student Feedback' },
    { path: '/student/view/profile/', name: 'Student View Profile' },
    { path: '/student/fcmtoken/', name: 'Student FCM Token (API)' },
    { path: '/student/view/notification/', name: 'Student View Notification' },
    { path: '/student/view/result/', name: 'Student View Result' },
  ];

  studentPaths.forEach(({ path, name }) => {
    it(`should successfully load/handle "${name}" page/action`, () => {
      if (name.includes('(API)')) {
        cy.request(`${BASE_URL}${path}`).its('status').should('eq', 200);
      } else {
        cy.visit(`${BASE_URL}${path}`);
        cy.url().should('include', path);
        cy.get('body').should('be.visible');
      }
    });
  });
});