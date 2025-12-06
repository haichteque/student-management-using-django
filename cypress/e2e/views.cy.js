// cypress/e2e/django_app.cy.js

// Define a custom login command using cy.session for state preservation
Cypress.Commands.add('login', (email, password) => {
  cy.session([email, password], () => {
    cy.visit('/');
    cy.get('input[name="email"]').type(email);
    cy.get('input[name="password"]').type(password);
    cy.get('form').submit(); // Assuming the login form submits to the doLogin view
  }, {
    validate() {
      // Validate that the user is logged in by checking for redirection from the login page
      cy.url().should('not.eq', 'http://127.0.0.1:8000/');
    }
  });
});

describe('Django App Authentication and Core Functionality', () => {
  const baseURL = 'http://127.0.0.1:8000/';

  // User credentials
  const admin = { email: 'qasim@admin.com', password: 'admin' };
  const staff = { email: 'bill@ms.com', password: '123' };
  const student = { email: 'qasim@nu.edu.pk', password: '123' };

  // Helper function to detect user type and target home URL
  const getUserTypeData = (email) => {
    if (email === admin.email) return { type: 'admin', homeUrl: 'admin_home' };
    if (email === staff.email) return { type: 'staff', homeUrl: 'staff_home' };
    if (email === student.email) return { type: 'student', homeUrl: 'student_home' };
    return { type: 'unknown', homeUrl: '' }; // Fallback for unknown users
  };

  beforeEach(() => {
    // Ensure starting from a logged-out state for consistent test execution
    // Assumes /logout/ is an accessible URL that clears the user session and redirects to /
    cy.visit('/logout/');
    cy.url().should('eq', baseURL);
  });

  describe('Login Page Access and Redirection', () => {
    it('should display the login form for unauthenticated users at the base URL', () => {
      cy.visit('/');
      cy.get('input[name="email"]').should('be.visible');
      cy.get('input[name="password"]').should('be.visible');
      cy.get('form button[type="submit"], form input[type="submit"]').should('be.visible');
    });

    [admin, staff, student].forEach(user => {
      const userData = getUserTypeData(user.email);
      it(`should redirect an authenticated ${userData.type} user from the login page to their respective home`, () => {
        cy.login(user.email, user.password); // Log in the user
        cy.visit('/'); // Attempt to visit the login page again
        cy.url().should('eq', `${baseURL}${userData.homeUrl}/`);
      });
    });
  });

  describe('User Login Functionality (doLogin)', () => {
    [admin, staff, student].forEach(user => {
      const userData = getUserTypeData(user.email);
      it(`should allow ${userData.type} user to login successfully and redirect to ${userData.homeUrl}`, () => {
        cy.visit('/');
        cy.get('input[name="email"]').type(user.email);
        cy.get('input[name="password"]').type(user.password);
        cy.get('form').submit();
        cy.url().should('eq', `${baseURL}${userData.homeUrl}/`);
        // Optional: Verify a common element that indicates successful login, e.g., a dashboard heading
        // cy.contains('Dashboard').should('be.visible');
      });
    });

    it('should display an error message for invalid login credentials', () => {
      cy.visit('/');
      cy.get('input[name="email"]').type('nonexistent@example.com');
      cy.get('input[name="password"]').type('wrongpass');
      cy.get('form').submit();
      cy.url().should('eq', baseURL); // Should redirect back to the login page
      cy.contains('Invalid details').should('be.visible'); // Check for the error message
    });
  });

  describe('User Logout Functionality (logout_user)', () => {
    [admin, staff, student].forEach(user => {
      const userData = getUserTypeData(user.email);
      it(`should allow ${userData.type} user to logout successfully`, () => {
        cy.login(user.email, user.password);
        cy.url().should('include', userData.homeUrl); // Verify user is logged in
        cy.visit('/logout/'); // Navigate to the logout URL
        cy.url().should('eq', baseURL); // Should redirect back to the login page
        cy.get('input[name="email"]').should('be.visible'); // Verify login form is visible
      });
    });
  });

  describe('API Endpoint: get_attendance', () => {
    // Note: The success of these tests depends on existing data in the Django database.
    // Specifically, `Subject` and `Session` records with the specified IDs.
    // If such data does not exist, the server might return 404 or 500 errors.
    const assumedValidSubjectId = 1; // Replace with an actual valid subject ID from your DB
    const assumedValidSessionId = 1; // Replace with an actual valid session ID from your DB
    const nonExistentId = 9999; // A value highly unlikely to exist as an ID

    it('should return attendance data for valid subject and session IDs', () => {
      cy.request({
        method: 'POST',
        url: `${baseURL}get_attendance/`, // Assumed URL for the get_attendance view
        form: true, // Send as application/x-www-form-urlencoded
        body: {
          subject: assumedValidSubjectId,
          session: assumedValidSessionId,
        },
      }).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.headers['content-type']).to.include('application/json');
        const attendanceData = JSON.parse(response.body); // Response body is a stringified JSON
        expect(attendanceData).to.be.an('array');
        if (attendanceData.length > 0) {
          expect(attendanceData[0]).to.have.all.keys('id', 'attendance_date', 'session');
          expect(attendanceData[0].session).to.eq(assumedValidSessionId);
        }
      });
    });

    it('should return a 404 or 500 for non-existent subject/session IDs', () => {
      cy.request({
        method: 'POST',
        url: `${baseURL}get_attendance/`,
        form: true,
        body: {
          subject: nonExistentId,
          session: nonExistentId,
        },
        failOnStatusCode: false // Prevent Cypress from failing the test on non-2xx status codes
      }).then((response) => {
        // `get_object_or_404` raises Http404. If caught and returns None, Django defaults to 500.
        expect(response.status).to.be.oneOf([404, 500]);
      });
    });

    it('should return a 404 or 500 if one of the IDs is invalid', () => {
        cy.request({
            method: 'POST',
            url: `${baseURL}get_attendance/`,
            form: true,
            body: {
                subject: assumedValidSubjectId,
                session: nonExistentId,
            },
            failOnStatusCode: false
        }).then((response) => {
            expect(response.status).to.be.oneOf([404, 500]);
        });
    });
  });

  describe('Static Endpoint: showFirebaseJS', () => {
    it('should return a JavaScript file with Firebase content', () => {
      // Assumed URL for the showFirebaseJS view
      cy.request(`${baseURL}firebase-messaging-sw.js`).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.headers['content-type']).to.include('application/javascript');
        expect(response.body).to.include('firebase.initializeApp');
        expect(response.body).to.include('messaging.setBackgroundMessageHandler');
      });
    });
  });
});