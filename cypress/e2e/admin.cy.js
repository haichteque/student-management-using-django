describe('Django Admin Panel E2E Tests', () => {
    const baseUrl = 'http://127.0.0.1:8000';

    // Helper function for logging in to the admin panel
    const login = (email, password) => {
        cy.visit(baseUrl + '/admin');
        cy.get('#id_username').type(email);
        cy.get('#id_password').type(password);
        cy.get('input[type="submit"]').click();
    };

    describe('Admin User Access', () => {
        const adminUser = {
            email: 'qasim@admin.com',
            password: 'admin'
        };

        beforeEach(() => {
            login(adminUser.email, adminUser.password);
        });

        it('should successfully log in and display all registered models', () => {
            cy.url().should('include', '/admin/');
            cy.contains('Site administration').should('be.visible');
            cy.contains('Welcome, qasim@admin.com').should('be.visible');

            // Check for visibility of all models registered in admin.py
            cy.contains('Authentication and Authorization').should('be.visible');
            cy.contains('Custom users').should('be.visible'); // Assuming default pluralization
            cy.contains('Groups').should('be.visible');       // Standard Django Group model

            // Assuming other models are in a default app or have no specific app group
            cy.contains('Staffs').should('be.visible');      // Assuming default pluralization
            cy.contains('Students').should('be.visible');    // Assuming default pluralization
            cy.contains('Courses').should('be.visible');     // Assuming default pluralization
            cy.contains('Subjects').should('be.visible');    // Assuming default pluralization
            cy.contains('Sessions').should('be.visible');    // Assuming default pluralization
        });

        it('should be able to log out from the admin panel', () => {
            cy.url().should('include', '/admin/');
            cy.contains('Log out').click();
            cy.url().should('include', '/admin/login/?next=/admin/');
            cy.contains('Logged out').should('be.visible');
        });
    });

    describe('Staff User Access', () => {
        const staffUser = {
            email: 'bill@ms.com',
            password: '123'
        };

        beforeEach(() => {
            login(staffUser.email, staffUser.password);
        });

        it('should successfully log in to the admin panel but with limited access', () => {
            cy.url().should('include', '/admin/');
            cy.contains('Site administration').should('be.visible');
            cy.contains('Welcome, bill@ms.com').should('be.visible');

            // A staff user can log in, but typically has limited permissions by default.
            // They should see the admin dashboard.
            // They might not see all models unless specific permissions are granted.
            // We'll assert that full admin models are not visible by default.
            cy.contains('Custom users').should('not.exist');
            cy.contains('Staffs').should('not.exist');
            cy.contains('Students').should('not.exist');
            cy.contains('Courses').should('not.exist');
            cy.contains('Subjects').should('not.exist');
            cy.contains('Sessions').should('not.exist');
            
            // Check for presence of 'Authentication and Authorization' if Staff has permissions on Groups/Users
            // By default, staff often has permissions on their own user object, but not other models without explicit setup.
            cy.contains('Authentication and Authorization').should('not.exist');
        });

        it('should be able to log out from the admin panel', () => {
            cy.url().should('include', '/admin/');
            cy.contains('Log out').click();
            cy.url().should('include', '/admin/login/?next=/admin/');
            cy.contains('Logged out').should('be.visible');
        });
    });

    describe('Student User Access', () => {
        const studentUser = {
            email: 'qasim@nu.edu.pk',
            password: '123'
        };

        beforeEach(() => {
            // Attempt to login as a student, who is not 'is_staff' by default
            cy.visit(baseUrl + '/admin');
            cy.get('#id_username').type(studentUser.email);
            cy.get('#id_password').type(studentUser.password);
            cy.get('input[type="submit"]').click();
        });

        it('should not be able to log in to the admin interface (student is not staff)', () => {
            cy.url().should('include', '/admin/login/?next=/admin/');
            // Check for the error message indicating failed login for non-staff user
            cy.contains('Please enter a correct username and password for a staff account. Note that both fields may be case-sensitive.').should('be.visible');
            cy.contains('Site administration').should('not.exist'); // Should not see the admin dashboard
        });
    });
});