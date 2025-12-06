// This Cypress test code assumes you have a `cy.login` custom command defined in
// `cypress/support/commands.js` or similar, to handle the login process.
//
// Example `cypress/support/commands.js` content:
//
// Cypress.Commands.add('login', (email, password) => {
//   // Use cy.session to cache login state for performance.
//   // The cache key is an array of login parameters.
//   cy.session([email, password], () => {
//     cy.visit('/login/'); // Adjust if your login URL is different
//     cy.get('input[name="email"]').type(email); // Assuming login form field name for email
//     cy.get('input[name="password"]').type(password); // Assuming login form field name for password
//     cy.get('form').submit();
//     // After submission, verify that we are no longer on the login page.
//     // This might be the user's dashboard or a redirect to it.
//     cy.url().should('not.include', '/login/');
//     // It's good practice to verify some element that confirms successful login.
//     // E.g., cy.get('nav#user-menu').should('be.visible');
//   }, {
//     cacheAcrossSpecs: true // Optional: Keep session cached across multiple spec files
//   });
// });
//
// Ensure `cypress/support/e2e.js` includes `import './commands';` if you place it there.


// Base URL for the Django application
const BASE_URL = 'http://127.0.0.1:8000';

// Specific URLs used in the middleware and for testing
const LOGIN_PAGE = '/login/';

// Home dashboards for different user types
const ADMIN_DASHBOARD = '/admin_home/';
const STAFF_DASHBOARD = '/staff_home/';
const STUDENT_DASHBOARD = '/student_home/';

// Hypothetical pages representing views from specific Django modules.
// These URLs should correspond to how your `urls.py` maps to the specified view modules
// in the middleware (e.g., `main_app.hod_views`).
const HOD_VIEW_PAGE = '/hod/manage_courses/';      // Represents a page from `main_app.hod_views`
const STAFF_VIEW_PAGE = '/staff/take_attendance/'; // Represents a page from `main_app.staff_views`
const STUDENT_VIEW_PAGE = '/student/view_profile/';// Represents a page from `main_app.student_views`

// A hypothetical page for Admin-specific functionality, not explicitly restricted
// by the middleware's current rules for other user types (unless it falls into
// `main_app.hod_views`, `main_app.staff_views`, or `main_app.student_views`).
const ADMIN_SPECIFIC_PAGE = '/admin/manage_settings/';


describe('LoginCheckMiddleware E2E Tests', () => {

  // --- Guest User Tests (user.is_authenticated is False) ---
  describe('Guest User Access', () => {
    beforeEach(() => {
      // Ensure no active session for guest user tests
      cy.clearCookies();
      cy.clearLocalStorage();
      cy.visit(LOGIN_PAGE); // Start clean and not logged in
    });

    it('should allow access to the login page', () => {
      cy.url().should('eq', `${BASE_URL}${LOGIN_PAGE}`);
    });

    it('should redirect unauthenticated users from protected pages to the login page', () => {
      // List of protected pages that should redirect to login
      const protectedPages = [
        ADMIN_DASHBOARD,
        STAFF_DASHBOARD,
        STUDENT_DASHBOARD,
        HOD_VIEW_PAGE,
        STAFF_VIEW_PAGE,
        STUDENT_VIEW_PAGE,
        ADMIN_SPECIFIC_PAGE
      ];

      protectedPages.forEach(page => {
        cy.visit(page);
        cy.url().should('eq', `${BASE_URL}${LOGIN_PAGE}`);
      });
    });
  });

  // --- Admin User Tests (user.user_type == '1') ---
  describe('Admin User Access', () => {
    const adminEmail = 'qasim@admin.com';
    const adminPassword = 'admin';

    beforeEach(() => {
      // Log in as Admin before each test in this block
      cy.login(adminEmail, adminPassword);
    });

    it('should allow Admin to access their own dashboard', () => {
      cy.visit(ADMIN_DASHBOARD);
      cy.url().should('eq', `${BASE_URL}${ADMIN_DASHBOARD}`);
    });

    it('should allow Admin to access HOD-related views (as per middleware logic)', () => {
      cy.visit(HOD_VIEW_PAGE);
      cy.url().should('eq', `${BASE_URL}${HOD_VIEW_PAGE}`);
    });

    it('should allow Admin to access Staff-related views (as per middleware logic)', () => {
      cy.visit(STAFF_VIEW_PAGE);
      cy.url().should('eq', `${BASE_URL}${STAFF_VIEW_PAGE}`);
    });

    it('should allow Admin to access other Admin-specific pages', () => {
      cy.visit(ADMIN_SPECIFIC_PAGE);
      cy.url().should('eq', `${BASE_URL}${ADMIN_SPECIFIC_PAGE}`);
    });

    it('should redirect Admin from Student-related views (`main_app.student_views`) to Admin dashboard', () => {
      cy.visit(STUDENT_VIEW_PAGE); // This page simulates `main_app.student_views`
      cy.url().should('eq', `${BASE_URL}${ADMIN_DASHBOARD}`);
    });

    // Middleware does not explicitly block admin from staff/student dashboards (unless they fall into 'student_views' modules)
    it('should allow Admin to access Staff dashboard (not explicitly blocked by middleware for Admin)', () => {
      cy.visit(STAFF_DASHBOARD);
      cy.url().should('eq', `${BASE_URL}${STAFF_DASHBOARD}`);
    });

    it('should allow Admin to access Student dashboard (not explicitly blocked by middleware for Admin)', () => {
      cy.visit(STUDENT_DASHBOARD);
      cy.url().should('eq', `${BASE_URL}${STUDENT_DASHBOARD}`);
    });
  });

  // --- Staff User Tests (user.user_type == '2') ---
  describe('Staff User Access', () => {
    const staffEmail = 'bill@ms.com';
    const staffPassword = '123';

    beforeEach(() => {
      // Log in as Staff before each test in this block
      cy.login(staffEmail, staffPassword);
    });

    it('should allow Staff to access their own dashboard', () => {
      cy.visit(STAFF_DASHBOARD);
      cy.url().should('eq', `${BASE_URL}${STAFF_DASHBOARD}`);
    });

    it('should allow Staff to access Staff-related views (as per middleware logic)', () => {
      cy.visit(STAFF_VIEW_PAGE); // This page simulates `main_app.staff_views`
      cy.url().should('eq', `${BASE_URL}${STAFF_VIEW_PAGE}`);
    });

    it('should redirect Staff from Student-related views (`main_app.student_views`) to Staff dashboard', () => {
      cy.visit(STUDENT_VIEW_PAGE); // This page simulates `main_app.student_views`
      cy.url().should('eq', `${BASE_URL}${STAFF_DASHBOARD}`);
    });

    it('should redirect Staff from HOD-related views (`main_app.hod_views`) to Staff dashboard', () => {
      cy.visit(HOD_VIEW_PAGE); // This page simulates `main_app.hod_views`
      cy.url().should('eq', `${BASE_URL}${STAFF_DASHBOARD}`);
    });

    // Middleware does not explicitly block staff from admin/student dashboards (unless they fall into 'hod_views'/'student_views' modules)
    it('should allow Staff to access Admin dashboard (not explicitly blocked by middleware for Staff)', () => {
      cy.visit(ADMIN_DASHBOARD);
      cy.url().should('eq', `${BASE_URL}${ADMIN_DASHBOARD}`);
    });

    it('should allow Staff to access Student dashboard (not explicitly blocked by middleware for Staff)', () => {
      cy.visit(STUDENT_DASHBOARD);
      cy.url().should('eq', `${BASE_URL}${STUDENT_DASHBOARD}`);
    });
  });

  // --- Student User Tests (user.user_type == '3') ---
  describe('Student User Access', () => {
    const studentEmail = 'qasim@nu.edu.pk';
    const studentPassword = '123';

    beforeEach(() => {
      // Log in as Student before each test in this block
      cy.login(studentEmail, studentPassword);
    });

    it('should allow Student to access their own dashboard', () => {
      cy.visit(STUDENT_DASHBOARD);
      cy.url().should('eq', `${BASE_URL}${STUDENT_DASHBOARD}`);
    });

    it('should allow Student to access Student-related views (as per middleware logic)', () => {
      cy.visit(STUDENT_VIEW_PAGE); // This page simulates `main_app.student_views`
      cy.url().should('eq', `${BASE_URL}${STUDENT_VIEW_PAGE}`);
    });

    it('should redirect Student from HOD-related views (`main_app.hod_views`) to Student dashboard', () => {
      cy.visit(HOD_VIEW_PAGE); // This page simulates `main_app.hod_views`
      cy.url().should('eq', `${BASE_URL}${STUDENT_DASHBOARD}`);
    });

    it('should redirect Student from Staff-related views (`main_app.staff_views`) to Student dashboard', () => {
      cy.visit(STAFF_VIEW_PAGE); // This page simulates `main_app.staff_views`
      cy.url().should('eq', `${BASE_URL}${STUDENT_DASHBOARD}`);
    });

    // Middleware does not explicitly block student from admin/staff dashboards (unless they fall into 'hod_views'/'staff_views' modules)
    it('should allow Student to access Admin dashboard (not explicitly blocked by middleware for Student)', () => {
      cy.visit(ADMIN_DASHBOARD);
      cy.url().should('eq', `${BASE_URL}${ADMIN_DASHBOARD}`);
    });

    it('should allow Student to access Staff dashboard (not explicitly blocked by middleware for Student)', () => {
      cy.visit(STAFF_DASHBOARD);
      cy.url().should('eq', `${BASE_URL}${STAFF_DASHBOARD}`);
    });
  });
});