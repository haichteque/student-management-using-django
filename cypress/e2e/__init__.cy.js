Cypress.Commands.add('login', (email, password) => {
  cy.visit('http://127.0.0.1:8000/accounts/login/');
  cy.get('input[name="username"]').type(email);
  cy.get('input[name="password"]').type(password, { log: false }); // { log: false } to prevent password from showing in logs
  cy.get('button[type="submit"], input[type="submit"]').click();
});

Cypress.Commands.add('logout', () => {
  // Assuming there's a logout link visible after login
  cy.contains('Logout').click({ force: true });
  // After logout, usually redirected to login or homepage
  cy.url().should('include', '/accounts/login/');
});

describe('User Authentication and Role-Based Access', () => {
  const baseUrl = 'http://127.0.0.1:8000';

  beforeEach(() => {
    cy.clearCookies(); // Ensure a clean session for each test
  });

  describe('Admin User Functionality', () => {
    const admin = { email: 'qasim@admin.com', password: 'admin' };

    it('should allow admin to log in and access the Django admin dashboard', () => {
      cy.login(admin.email, admin.password);
      cy.url().should('include', '/admin/');
      cy.contains('Site administration').should('be.visible');
      cy.logout();
    });

    it('should prevent admin from accessing a hypothetical staff-only dashboard', () => {
      cy.login(admin.email, admin.password);
      // Attempt to visit a hypothetical staff-only page
      cy.visit(`${baseUrl}/staff/dashboard/`, { failOnStatusCode: false });
      cy.url().should('not.include', '/staff/dashboard/');
      // Expect either a redirect to admin dashboard, login, or permission denied message
      cy.contains('Permission denied', { timeout: 5000 }).should('exist');
      cy.logout();
    });

    it('should prevent admin from accessing a hypothetical student-only dashboard', () => {
      cy.login(admin.email, admin.password);
      // Attempt to visit a hypothetical student-only page
      cy.visit(`${baseUrl}/student/dashboard/`, { failOnStatusCode: false });
      cy.url().should('not.include', '/student/dashboard/');
      // Expect either a redirect to admin dashboard, login, or permission denied message
      cy.contains('Permission denied', { timeout: 5000 }).should('exist');
      cy.logout();
    });
  });

  describe('Staff User Functionality', () => {
    const staff = { email: 'bill@ms.com', password: '123' };

    it('should allow staff to log in and access a hypothetical staff dashboard', () => {
      cy.login(staff.email, staff.password);
      // Assuming a staff dashboard at /staff/dashboard/
      cy.url().should('include', '/staff/dashboard/');
      cy.contains('Staff Dashboard').should('be.visible'); // Placeholder text
      cy.logout();
    });

    it('should prevent staff from accessing the Django admin dashboard', () => {
      cy.login(staff.email, staff.password);
      cy.visit(`${baseUrl}/admin/`, { failOnStatusCode: false });
      cy.url().should('not.include', '/admin/');
      // Expect either a redirect to staff dashboard, login, or permission denied message
      cy.contains('Permission denied', { timeout: 5000 }).should('exist');
      cy.logout();
    });

    it('should prevent staff from accessing a hypothetical student-only dashboard', () => {
      cy.login(staff.email, staff.password);
      // Attempt to visit a hypothetical student-only page
      cy.visit(`${baseUrl}/student/dashboard/`, { failOnStatusCode: false });
      cy.url().should('not.include', '/student/dashboard/');
      // Expect either a redirect to staff dashboard, login, or permission denied message
      cy.contains('Permission denied', { timeout: 5000 }).should('exist');
      cy.logout();
    });
  });

  describe('Student User Functionality', () => {
    const student = { email: 'qasim@nu.edu.pk', password: '123' };

    it('should allow student to log in and access a hypothetical student dashboard', () => {
      cy.login(student.email, student.password);
      // Assuming a student dashboard at /student/dashboard/
      cy.url().should('include', '/student/dashboard/');
      cy.contains('Student Portal').should('be.visible'); // Placeholder text
      cy.logout();
    });

    it('should prevent student from accessing the Django admin dashboard', () => {
      cy.login(student.email, student.password);
      cy.visit(`${baseUrl}/admin/`, { failOnStatusCode: false });
      cy.url().should('not.include', '/admin/');
      // Expect either a redirect to student dashboard, login, or permission denied message
      cy.contains('Permission denied', { timeout: 5000 }).should('exist');
      cy.logout();
    });

    it('should prevent student from accessing a hypothetical staff-only dashboard', () => {
      cy.login(student.email, student.password);
      // Attempt to visit a hypothetical staff-only page
      cy.visit(`${baseUrl}/staff/dashboard/`, { failOnStatusCode: false });
      cy.url().should('not.include', '/staff/dashboard/');
      // Expect either a redirect to student dashboard, login, or permission denied message
      cy.contains('Permission denied', { timeout: 5000 }).should('exist');
      cy.logout();
    });
  });

  describe('General Authentication and Authorization Edge Cases', () => {
    it('should display an error for invalid login credentials', () => {
      cy.visit(`${baseUrl}/accounts/login/`);
      cy.get('input[name="username"]').type('invalid@user.com');
      cy.get('input[name="password"]').type('wrongpassword');
      cy.get('button[type="submit"], input[type="submit"]').click();
      cy.url().should('include', '/accounts/login/'); // Should remain on login page
      cy.contains('Please enter a correct username and password').should('be.visible'); // Common Django error message
    });

    it('should redirect unauthenticated users from protected pages to the login page', () => {
      // Attempt to directly visit a protected page without logging in
      cy.visit(`${baseUrl}/staff/dashboard/`, { failOnStatusCode: false });
      cy.url().should('include', '/accounts/login/');
      // Optionally, check for a message indicating the need to log in
      // cy.contains('Please log in to see this page').should('be.visible');
    });
  });
});