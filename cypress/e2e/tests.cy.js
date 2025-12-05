// cypress/e2e/authentication.cy.js

const baseUrl = 'http://127.0.0.1:8000';

describe('Authentication and Authorization Tests', () => {

  // Reusable function to perform a login
  const login = (email, password) => {
    cy.visit(`${baseUrl}/login/`); // Assuming a login page at /login/
    cy.get('input[name="email"]').type(email); // Selector for email input field
    cy.get('input[name="password"]').type(password); // Selector for password input field
    cy.get('button[type="submit"]').click(); // Selector for submit button
  };

  // Reusable function to perform a logout
  const logout = () => {
    // Assuming a logout URL, common in Django projects.
    // After visiting, user should typically be redirected to login or home.
    cy.visit(`${baseUrl}/logout/`);
    cy.url().should('include', '/login/'); // Assert that we are redirected to the login page after logout
  };

  beforeEach(() => {
    // Ensure each test starts from a clean, logged-out state.
    cy.clearCookies(); // Clear all browser cookies
    // Visit logout URL to ensure the Django session is cleared.
    // failOnStatusCode: false is used because /logout/ might return a non-2xx status
    // if already logged out, or redirect in a way Cypress interprets as an error.
    cy.visit(`${baseUrl}/logout/`, { failOnStatusCode: false });
  });

  // --- Admin User Tests ---
  describe('Admin User Authentication', () => {
    const admin = { email: 'qasim@admin.com', password: 'admin' };

    it('should allow admin to log in successfully, access admin panel, and log out', () => {
      login(admin.email, admin.password);
      cy.url().should('not.include', '/login/'); // Verify not on login page anymore
      cy.url().should('eq', `${baseUrl}/`); // Assuming successful login redirects to the root URL

      // Verify a general element that confirms login, e.g., a welcome message or dashboard link
      cy.get('body').should('contain', 'Welcome'); // Adjust if there's a more specific success indicator
      cy.get('body').should('contain', admin.email); // Check if admin's email is visible (e.g., in a navbar)

      // Access the Django admin interface
      cy.visit(`${baseUrl}/admin/`);
      cy.url().should('include', '/admin/');
      cy.get('h1').should('contain', 'Django administration'); // Verify admin panel header
      cy.get('body').should('contain', admin.email); // Check if admin's email is visible in admin panel

      logout();
      cy.url().should('include', '/login/'); // Confirm redirection to login after logout
    });

    it('should prevent admin from logging in with incorrect password', () => {
      login(admin.email, 'wrongpassword');
      cy.url().should('include', '/login/'); // Should remain on the login page
      // Check for common error message selectors from Django forms or Bootstrap alerts
      cy.get('.errorlist, .alert.alert-danger, .error-message').should('be.visible')
        .and('contain', 'Please enter a correct email and password.');
    });
  });

  // --- Staff User Tests ---
  describe('Staff User Authentication', () => {
    const staff = { email: 'bill@ms.com', password: '123' };

    it('should allow staff to log in successfully, access admin panel (with limited view), and log out', () => {
      login(staff.email, staff.password);
      cy.url().should('not.include', '/login/');
      cy.url().should('eq', `${baseUrl}/`);

      cy.get('body').should('contain', 'Welcome');
      cy.get('body').should('contain', staff.email);

      // Access the Django admin interface. Staff users typically have access but with limited permissions.
      cy.visit(`${baseUrl}/admin/`);
      cy.url().should('include', '/admin/');
      cy.get('h1').should('contain', 'Django administration');
      cy.get('body').should('contain', staff.email); // Check if staff's email is visible in admin panel

      logout();
      cy.url().should('include', '/login/');
    });
  });

  // --- Student User Tests ---
  describe('Student User Authentication', () => {
    const student = { email: 'qasim@nu.edu.pk', password: '123' };

    it('should allow student to log in successfully and log out', () => {
      login(student.email, student.password);
      cy.url().should('not.include', '/login/');
      cy.url().should('eq', `${baseUrl}/`);

      cy.get('body').should('contain', 'Welcome');
      cy.get('body').should('contain', student.email);

      logout();
      cy.url().should('include', '/login/');
    });

    it('should prevent student from accessing the admin panel', () => {
      login(student.email, student.password);
      cy.url().should('not.include', '/login/');

      // Attempt to access /admin/ as a student. Should be redirected or denied.
      cy.visit(`${baseUrl}/admin/`, { failOnStatusCode: false }); // Allow non-2xx status codes (e.g., 403, 302 redirect)
      cy.url().should('not.include', '/admin/'); // Student should not remain on /admin/ page
      cy.url().should('include', '/login/'); // Typically redirected to login page if unauthorized

      logout();
    });
  });

  // --- General Invalid Login Tests ---
  describe('Invalid Credential Handling', () => {
    it('should display an error for non-existent user credentials', () => {
      login('nonexistent@example.com', 'fakepassword');
      cy.url().should('include', '/login/');
      cy.get('.errorlist, .alert.alert-danger, .error-message').should('be.visible')
        .and('contain', 'Please enter a correct email and password.');
    });

    it('should display an error for empty credentials', () => {
      cy.visit(`${baseUrl}/login/`);
      cy.get('button[type="submit"]').click(); // Submit an empty form
      cy.url().should('include', '/login/');
      cy.get('.errorlist, .alert.alert-danger, .error-message').should('be.visible')
        .and('contain', 'This field is required'); // Or a similar message for missing input
    });
  });

});