describe('Authentication Module Test Suite', () => {
    const validEmail = 'ijtaba@ijtaba.com';
    const validPassword = 'ijtaba';

    beforeEach(() => {
        cy.visit('/');
    });

    it('TC-01: Verify successful login with valid superuser credentials', () => {
        cy.get('input[name="email"]').type(validEmail);
        cy.get('input[name="password"]').type(validPassword);
        cy.get('button[type="submit"]').click();

        // Assert redirection to Admin Dashboard
        // Using relaxed assertion to ensure robustness against minor title variations
        cy.url().should('include', '/admin/');
        cy.contains(/Dashboard/i).should('be.visible');
    });

    it('TC-01-A: Verify Login Page UI Elements', () => {
        cy.contains('Sign in to start your session').should('be.visible');
        cy.get('input[name="email"]').should('be.visible');
        cy.get('input[name="password"]').should('be.visible');
        cy.get('button[type="submit"]').should('be.visible');
    });

    it('TC-02: Verify login failure with valid email but wrong password', () => {
        cy.get('input[name="email"]').type(validEmail);
        cy.get('input[name="password"]').type('wrongpassword123');
        cy.get('button[type="submit"]').click();

        // Assert error message visibility
        cy.contains('Invalid details').should('be.visible');
        // Assert URL remains on login page or does not redirect to admin
        cy.url().should('not.include', '/admin/');
    });

    it('TC-02-A: Verify Password Masking', () => {
        cy.get('input[name="password"]')
            .should('have.attr', 'type', 'password');
    });

    it('TC-03: Verify login failure with unregistered email', () => {
        cy.get('input[name="email"]').type('unregistered@example.com');
        cy.get('input[name="password"]').type('somepassword');
        cy.get('button[type="submit"]').click();

        cy.contains('Invalid details').should('be.visible');
        cy.url().should('not.include', '/admin/');
    });

    it('TC-04: Verify login failure with empty credentials (BVA)', () => {
        // Attempt to submit empty form
        cy.get('button[type="submit"]').click();

        // Browser HTML5 validation usually prevents submission. 
        // We check that we are still on the login page.
        cy.url().should('not.include', '/admin/');

        // Optional: Check for browser validation message if possible, 
        // but checking URL is safer for cross-browser compatibility in Cypress.
        cy.get('input[name="email"]').then(($input) => {
            expect($input[0].validationMessage).to.not.be.empty;
        });
    });

    it('TC-05: Verify successful logout functionality', () => {
        // Pre-condition: User must be logged in
        cy.login(validEmail, validPassword);

        // Action: Click Logout
        // Note: Logout usually has a confirmation dialog. Cypress auto-accepts alerts/confirms.
        cy.contains('Logout').click({ force: true });

        // Assert redirection to Login Page
        cy.url().should('include', '/');
        cy.get('input[name="email"]').should('be.visible');
        cy.contains('Sign in to start your session').should('be.visible');
    });

    it('TC-05-A: Verify Security - Back Button after Logout', () => {
        cy.login(validEmail, validPassword);
        cy.contains('Logout').click({ force: true });

        // Try to go back
        cy.go('back');

        // Should still be on login page or redirected there
        // Django auth usually redirects unauthenticated users to login
        cy.url().should('not.include', '/admin/');
        cy.get('input[name="email"]').should('be.visible');
    });
});
