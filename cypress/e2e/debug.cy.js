describe('Debug Login', () => {
    it('should visit login page', () => {
        cy.visit('/');
        cy.title().should('include', 'Student Management System');
    });

    it('should login and redirect', () => {
        cy.visit('/');
        cy.get('input[name="email"]').type('ijtaba@ijtaba.com');
        cy.get('input[name="password"]').type('ijtaba');
        cy.get('button[type="submit"]').click();

        // Wait for potential redirect
        cy.wait(2000);

        // Log the current URL
        cy.url().then(url => {
            cy.log('Current URL: ' + url);
        });

        // Check if we are NOT on login page
        cy.url().should('not.eq', 'http://127.0.0.1:8000/');
    });
});
