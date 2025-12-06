// This file assumes a basic Cypress setup.
// The `cy.login` command is defined here for completeness.
// In a real project, this command would typically be in `cypress/support/commands.js`
// and automatically loaded.

// Base URL for the Django application
const BASE_URL = 'http://127.0.0.1:8000';

// Custom Cypress command to handle user login.
// It uses cy.session for improved performance by caching login state.
Cypress.Commands.add('login', (email, password) => {
    cy.session([email, password], () => {
        cy.visit(`${BASE_URL}/accounts/login/`); // Adjust this URL if your login page is different
        cy.get('#id_username').type(email); // Assumes the username field has id="id_username"
        cy.get('#id_password').type(password); // Assumes the password field has id="id_password"
        cy.get('form button[type="submit"]').click(); // Assumes the login button is a submit button within the form

        // Assert that login was successful by checking the URL or a specific element
        cy.url().should('not.include', '/accounts/login/');
        // You might want to check for a "Welcome, [Username]" message or a dashboard element
        cy.get('body').should('not.contain', 'Please log in'); // Generic check
    }, {
        cacheAcrossSpecs: true // Caches the session to speed up subsequent tests
    });
});

describe('EditResultView E2E Tests', () => {
    const editResultPath = '/staff/edit-result/'; // The expected URL path for the EditResultView

    // --- Tests for Staff User (authorized access) ---
    describe('As a Staff User', () => {
        const staffEmail = 'bill@ms.com';
        const staffPassword = '123';

        // Log in as staff before each test in this block
        beforeEach(() => {
            cy.login(staffEmail, staffPassword);
            cy.visit(`${BASE_URL}${editResultPath}`);
        });

        it('should display the "Edit Student\'s Result" form correctly', () => {
            cy.contains('h1', "Edit Student's Result").should('be.visible');
            cy.get('form').should('be.visible');
            cy.get('#id_student').should('be.visible'); // Assumes form fields have default Django IDs
            cy.get('#id_subject').should('be.visible');
            cy.get('#id_test').should('be.visible');
            cy.get('#id_exam').should('be.visible');
            cy.get('button[type="submit"]').contains('Submit').should('be.visible');

            // Verify that subjects are loaded in the dropdown.
            // This test assumes `bill@ms.com` teaches at least one subject.
            cy.get('#id_subject option').its('length').should('be.gt', 0);
        });

        it('should successfully update an existing student result', () => {
            // IMPORTANT: For this test to pass, ensure your test database contains:
            // 1. A student named 'Qasim Student' (or whatever text your student dropdown shows).
            // 2. A subject named 'Math' (or whatever text your subject dropdown shows) that `bill@ms.com` teaches.
            // 3. An existing StudentResult entry for 'Qasim Student' in 'Math'.
            const studentName = 'Qasim Student'; // Replace with actual student name/ID
            const subjectName = 'Math'; // Replace with actual subject name/ID taught by staff
            const newTestScore = 75;
            const newExamScore = 88;

            cy.get('#id_student').select(studentName);
            cy.get('#id_subject').select(subjectName);
            cy.get('#id_test').clear().type(newTestScore);
            cy.get('#id_exam').clear().type(newExamScore);

            cy.get('form button[type="submit"]').click();

            // Verify success message and redirection to the same page
            cy.get('.alert-success').should('contain', 'Result Updated');
            cy.url().should('eq', `${BASE_URL}${editResultPath}`);
        });

        it('should display a warning for invalid form submission (e.g., empty scores)', () => {
            // IMPORTANT: Assumes 'Qasim Student' and 'Physics' (taught by staff) exist in the database.
            const studentName = 'Qasim Student';
            const subjectName = 'Physics';

            cy.get('#id_student').select(studentName);
            cy.get('#id_subject').select(subjectName);

            // Clear required fields to simulate invalid data
            cy.get('#id_test').clear();
            cy.get('#id_exam').clear();

            cy.get('form button[type="submit"]').click();

            // Verify warning message and that the page remains on the edit form
            cy.get('.alert-warning').should('contain', 'Result Could Not Be Updated');
            cy.url().should('eq', `${BASE_URL}${editResultPath}`);
        });

        it('should display a warning if StudentResult does not exist for selected student/subject', () => {
            // IMPORTANT: This test requires a specific data scenario:
            // 1. A valid student (e.g., 'Jane Student') who exists.
            // 2. A valid subject (e.g., 'Chemistry') that `bill@ms.com` teaches.
            // 3. Crucially, NO StudentResult entry exists for 'Jane Student' in 'Chemistry'.
            const nonExistentResultStudentName = 'Jane Student'; // Student with no result for the selected subject
            const subjectTaughtByStaff = 'Chemistry'; // Subject taught by bill@ms.com

            cy.get('#id_student').select(nonExistentResultStudentName);
            cy.get('#id_subject').select(subjectTaughtByStaff);
            cy.get('#id_test').clear().type(80);
            cy.get('#id_exam').clear().type(90);

            cy.get('form button[type="submit"]').click();

            // Verify warning message, indicating the `get_object_or_404` or `objects.get` failed
            cy.get('.alert-warning').should('contain', 'Result Could Not Be Updated');
            cy.url().should('eq', `${BASE_URL}${editResultPath}`);
        });
    });

    // --- Tests for Unauthorized Access (Student, Admin, or Anonymous) ---
    describe('Unauthorized Access to EditResultView', () => {
        const studentEmail = 'qasim@nu.edu.pk';
        const studentPassword = '123';
        const adminEmail = 'qasim@admin.com';
        const adminPassword = 'admin';

        it('should redirect unauthenticated users to the login page', () => {
            cy.visit(`${BASE_URL}${editResultPath}`);
            cy.url().should('include', '/accounts/login/');
            cy.contains('Please log in').should('be.visible'); // Generic login prompt text
        });

        it('should not allow Student users to access the page', () => {
            cy.login(studentEmail, studentPassword);
            cy.visit(`${BASE_URL}${editResultPath}`, { failOnStatusCode: false }); // Prevents Cypress from failing on 403/404
            cy.url().should('not.include', editResultPath); // Should not remain on the edit result page

            // Expect a permission denied message or redirect to another page (e.g., student dashboard)
            // The exact behavior depends on your Django project's permission setup.
            cy.contains('You don\'t have permission', { timeout: 5000 }).should('be.visible'); // Example for a 403 page
            // OR if it redirects to the student dashboard:
            // cy.url().should('eq', `${BASE_URL}/student/home/`);
        });

        it('should not allow Admin users to access the page', () => {
            cy.login(adminEmail, adminPassword);
            cy.visit(`${BASE_URL}${editResultPath}`, { failOnStatusCode: false });
            cy.url().should('not.include', editResultPath); // Should not remain on the edit result page

            // Admin users are not Staff users by default. Expect similar permission issues.
            cy.contains('You don\'t have permission', { timeout: 5000 }).should('be.visible'); // Example for a 403 page
            // OR if it redirects to the admin dashboard:
            // cy.url().should('eq', `${BASE_URL}/admin/`);
        });
    });
});