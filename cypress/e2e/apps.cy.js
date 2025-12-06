describe('User Authentication and Role-Based Access', () => {
  const BASE_URL = 'http://127.0.0.1:8000';
  const LOGIN_PATH = '/login/'; // Common Django login path convention
  const LOGOUT_PATH = '/logout/'; // Common Django logout path convention

  const users = {
    admin: {
      email: 'qasim@admin.com',
      password: 'admin',
      roleIndicator: 'Admin Dashboard', // Text expected on admin's post-login page
      dashboardPath: '/admin/', // Common Django admin URL
    },
    staff: {
      email: 'bill@ms.com',
      password: '123',
      roleIndicator: 'Staff Panel', // Text expected on staff's post-login page
      dashboardPath: '/staff-dashboard/', // Assumed staff dashboard URL
    },
    student: {
      email: 'qasim@nu.edu.pk',
      password: '123',
      roleIndicator: 'Student Portal', // Text expected on student's post-login page
      dashboardPath: '/student-portal/', // Assumed student portal URL
    },
  };

  const login = (email, password) => {
    cy.visit(`${BASE_URL}${LOGIN_PATH}`);
    cy.get('input[name="username"]').type(email); // Assuming Django's default 'username' field, which can be an email if configured
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click(); // Assuming a submit button
  };

  beforeEach(() => {
    cy.clearCookies();
    cy.clearLocalStorage();
    // Attempt to log out before each test to ensure a clean state
    cy.visit(`${BASE_URL}${LOGOUT_PATH}`, { failOnStatusCode: false }); // Don't fail if logout redirects or doesn't exist
  });

  describe('Admin User Tests', () => {
    const admin = users.admin;

    it('should allow admin to log in successfully and access the admin dashboard', () => {
      login(admin.email, admin.password);
      cy.url().should('include', admin.dashboardPath);
      cy.contains(admin.roleIndicator).should('be.visible');
    });

    it('should prevent admin from accessing the student portal directly after login', () => {
      login(admin.email, admin.password);
      cy.url().should('include', admin.dashboardPath);
      cy.visit(`${BASE_URL}${users.student.dashboardPath}`, { failOnStatusCode: false });
      cy.url().should('include', admin.dashboardPath); // Admin should be redirected back to their own dashboard or forbidden page
      cy.contains(admin.roleIndicator).should('be.visible');
    });

    it('should allow admin to log out successfully', () => {
      login(admin.email, admin.password);
      cy.url().should('include', admin.dashboardPath);
      cy.get('a').contains('Logout').click();
      cy.url().should('include', LOGIN_PATH);
      cy.contains('logged out').should('be.visible'); // Assuming a "You are logged out" message
    });
  });

  describe('Staff User Tests', () => {
    const staff = users.staff;

    it('should allow staff to log in successfully and access the staff panel', () => {
      login(staff.email, staff.password);
      cy.url().should('include', staff.dashboardPath);
      cy.contains(staff.roleIndicator).should('be.visible');
    });

    it('should prevent staff from accessing the admin dashboard', () => {
      login(staff.email, staff.password);
      cy.url().should('include', staff.dashboardPath);
      cy.visit(`${BASE_URL}${users.admin.dashboardPath}`, { failOnStatusCode: false });
      cy.url().should('not.include', users.admin.dashboardPath); // Should be redirected or denied access
      cy.url().should('include', staff.dashboardPath); // Redirected back to staff dashboard or generic forbidden page
    });

    it('should allow staff to log out successfully', () => {
      login(staff.email, staff.password);
      cy.url().should('include', staff.dashboardPath);
      cy.get('a').contains('Logout').click();
      cy.url().should('include', LOGIN_PATH);
    });
  });

  describe('Student User Tests', () => {
    const student = users.student;

    it('should allow student to log in successfully and access the student portal', () => {
      login(student.email, student.password);
      cy.url().should('include', student.dashboardPath);
      cy.contains(student.roleIndicator).should('be.visible');
    });

    it('should prevent student from accessing the staff panel', () => {
      login(student.email, student.password);
      cy.url().should('include', student.dashboardPath);
      cy.visit(`${BASE_URL}${users.staff.dashboardPath}`, { failOnStatusCode: false });
      cy.url().should('not.include', users.staff.dashboardPath);
      cy.url().should('include', student.dashboardPath);
    });

    it('should allow student to log out successfully', () => {
      login(student.email, student.password);
      cy.url().should('include', student.dashboardPath);
      cy.get('a').contains('Logout').click();
      cy.url().should('include', LOGIN_PATH);
    });
  });

  describe('General Authentication and Security Tests', () => {
    it('should show an error message for invalid login credentials', () => {
      login('wrong@user.com', 'wrongpassword');
      cy.url().should('include', LOGIN_PATH);
      cy.contains('Please enter a correct username and password.').should('be.visible'); // Common Django error message
    });

    it('should redirect unauthenticated users from the admin dashboard to the login page', () => {
      cy.visit(`${BASE_URL}${users.admin.dashboardPath}`, { failOnStatusCode: false });
      cy.url().should('include', LOGIN_PATH);
    });

    it('should redirect unauthenticated users from the staff dashboard to the login page', () => {
      cy.visit(`${BASE_URL}${users.staff.dashboardPath}`, { failOnStatusCode: false });
      cy.url().should('include', LOGIN_PATH);
    });

    it('should redirect unauthenticated users from the student portal to the login page', () => {
      cy.visit(`${BASE_URL}${users.student.dashboardPath}`, { failOnStatusCode: false });
      cy.url().should('include', LOGIN_PATH);
    });
  });
});