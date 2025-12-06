// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

Cypress.Commands.add('login', (email, password) => {
    cy.visit('/');
    cy.get('input[name="email"]').type(email);
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click();
});

Cypress.Commands.add('navigateTo', (menuItem) => {
    // Click the menu item in the sidebar
    // Use regex to match text with whitespace and case insensitivity
    const regex = new RegExp(menuItem, 'i');
    cy.contains('.nav-link p', regex).click({ force: true });
});
