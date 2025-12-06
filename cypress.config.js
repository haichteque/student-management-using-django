const { defineConfig } = require("cypress");

// -----------------------------
// Cypress Configuration
// -----------------------------
module.exports = defineConfig({
  e2e: {
    baseUrl: "http://127.0.0.1:8000",

    // Test spec pattern
    specPattern: "cypress/e2e/**/*.cy.{js,ts}",

    // Support file
    supportFile: "cypress/support/e2e.js",
  },
});
