describe('Email Backend Login Tests', () => {
    const BASE_URL = 'http://127.0.0.1:8000';

    beforeEach(() => {
        cy.clearCookies();
        cy.visit(`${BASE_URL}/login/`); // Assume a custom login page for staff/students
    });

    const login = (email, password) => {
        cy.get('input[name="email"]').type(email);
        cy.get('input[name="password"]').type(password);
        cy.get('form').submit();
    };

    context('Admin Login Tests', () => {
        const adminUser = {
            email: 'qasim@admin.com',
            password: 'admin'
        };

        it('should allow admin to log in successfully via /admin/login/', () => {
            cy.visit(`${BASE_URL}/admin/login/`);
            cy.get('input[name="username"]').type(adminUser.email); // Django admin uses 'username' field
            cy.get('input[name="password"]').type(adminUser.password);
            cy.get('form').submit();
            cy.url().should('include', '/admin/');
            cy.contains('Site administration').should('be.visible');
        });

        it('should prevent admin login with incorrect password via /admin/login/', () => {
            cy.visit(`${BASE_URL}/admin/login/`);
            cy.get('input[name="username"]').type(adminUser.email);
            cy.get('input[name="password"]').type('wrongpassword');
            cy.get('form').submit();
            cy.url().should('include', '/admin/login/');
            cy.contains('Please enter a correct username and password.').should('be.visible');
        });
    });

    context('Staff Login Tests', () => {
        const staffUser = {
            email: 'bill@ms.com',
            password: '123'
        };

        it('should allow staff to log in successfully via /login/', () => {
            login(staffUser.email, staffUser.password);
            cy.url().should('not.include', '/login/');
            cy.get('input[name="email"]').should('not.exist');
            cy.get('a').contains('Logout').should('be.visible');
        });

        it('should prevent staff login with incorrect password via /login/', () => {
            login(staffUser.email, 'wrongpass');
            cy.url().should('eq', `${BASE_URL}/login/`);
            cy.contains('Please enter a correct email and password.').should('be.visible');
        });
    });

    context('Student Login Tests', () => {
        const studentUser = {
            email: 'qasim@nu.edu.pk',
            password: '123'
        };

        it('should allow student to log in successfully via /login/', () => {
            login(studentUser.email, studentUser.password);
            cy.url().should('not.include', '/login/');
            cy.get('input[name="email"]').should('not.exist');
            cy.get('a').contains('Logout').should('be.visible');
        });

        it('should prevent student login with incorrect password via /login/', () => {
            login(studentUser.email, 'wrongpass');
            cy.url().should('eq', `${BASE_URL}/login/`);
            cy.contains('Please enter a correct email and password.').should('be.visible');
        });
    });

    context('General Login Failure Tests (via /login/)', () => {
        it('should prevent login with non-existent email', () => {
            login('nonexistent@example.com', 'somepassword');
            cy.url().should('eq', `${BASE_URL}/login/`);
            cy.contains('Please enter a correct email and password.').should('be.visible');
        });

        it('should prevent login with empty credentials (email and password)', () => {
            cy.get('form').submit();
            cy.url().should('eq', `${BASE_URL}/login/`);
            cy.contains('This field is required.').should('exist');
        });

        it('should prevent login with only email and no password', () => {
            cy.get('input[name="email"]').type('test@example.com');
            cy.get('form').submit();
            cy.url().should('eq', `${BASE_URL}/login/`);
            cy.get('input[name="password"]:invalid').should('exist');
            cy.contains('This field is required.').should('exist');
        });

        it('should prevent login with only password and no email', () => {
            cy.get('input[name="password"]').type('password123');
            cy.get('form').submit();
            cy.url().should('eq', `${BASE_URL}/login/`);
            cy.get('input[name="email"]:invalid').should('exist');
            cy.contains('This field is required.').should('exist');
        });
    });
});