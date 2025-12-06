describe('Authentication Module Test Suite', () => {
    const validEmail = 'admin@admin.com';
    
    beforeEach(() => {
        cy.visit('/');
    });

    // -------------------------------
    // Successful Login
    // -------------------------------
    it('TC-01: Verify successful login with valid superuser credentials', () => {
        cy.get('input[name="email"]').should('be.visible').type(validEmail);
        cy.get('input[name="password"]').should('be.visible').type('admin');
        cy.get('button[type="submit"]').click();

        cy.url({ timeout: 10000 }).should('include', '/admin/');
        cy.contains(/Dashboard/i, { timeout: 10000 }).should('be.visible');
    });

    it('TC-01-A: Verify Login Page UI Elements', () => {
        cy.contains(/Sign in to start your session/i).should('be.visible');
        cy.get('input[name="email"]').should('be.visible');
        cy.get('input[name="password"]').should('be.visible');
        cy.get('button[type="submit"]').should('be.visible');
    });

    // -------------------------------
    // Invalid Credentials
    // -------------------------------
    it('TC-02: Verify login failure with valid email but wrong password', () => {
        cy.get('input[name="email"]').type(validEmail);
        cy.get('input[name="password"]').type('wrongpassword123');
        cy.get('button[type="submit"]').click();

        cy.contains(/Invalid details/i, { timeout: 5000 }).should('be.visible');
        cy.url().should('not.include', '/admin/');
    });

    it('TC-02-A: Verify Password Masking', () => {
        cy.get('input[name="password"]').should('have.attr', 'type', 'password');
    });

    it('TC-03: Verify login failure with unregistered email', () => {
        cy.get('input[name="email"]').type('unregistered@example.com');
        cy.get('input[name="password"]').type('somepassword');
        cy.get('button[type="submit"]').click();

        cy.contains(/Invalid details/i, { timeout: 5000 }).should('be.visible');
        cy.url().should('not.include', '/admin/');
    });

    it('TC-04: Verify login failure with empty credentials (BVA)', () => {
        cy.get('button[type="submit"]').click();
        cy.url().should('not.include', '/admin/');
        cy.get('input[name="email"]').then(($input) => {
            expect($input[0].validationMessage).to.not.be.empty;
        });
        cy.get('input[name="password"]').then(($input) => {
            expect($input[0].validationMessage).to.not.be.empty;
        });
    });

    // -------------------------------
    // Logout
    // -------------------------------
    it('TC-05: Verify successful logout functionality', () => {
        cy.login(validEmail, 'admin');
        cy.contains(/Logout/i, { timeout: 5000 }).click({ force: true });
        cy.url({ timeout: 10000 }).should('include', '/');
        cy.get('input[name="email"]').should('be.visible');
        cy.contains(/Sign in to start your session/i).should('be.visible');
    });

    it('TC-05-A: Verify Security - Back Button after Logout', () => {
        cy.login(validEmail, 'admin');
        cy.contains(/Logout/i).click({ force: true });
        cy.go('back');
        cy.url().should('not.include', '/admin/');
        cy.get('input[name="email"]').should('be.visible');
    });
});
