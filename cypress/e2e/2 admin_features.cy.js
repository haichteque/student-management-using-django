import 'cypress-file-upload';

describe('Admin Features Test Suite', () => {

    const adminEmail = 'ijtaba@ijtaba.com';
    const adminPassword = 'ijtaba';

    let setupCourseName;
    let setupStaffEmail;

    beforeEach(() => {
        cy.login(adminEmail, adminPassword);
    });

    // ================================
    // Helper: Capture Edit URL
    // ================================
    const captureEditUrl = (email, envKey) => {
        cy.navigateTo('Manage Staff');

        cy.get('table tbody tr', { timeout: 12000 })
            .should('have.length.greaterThan', 0);

        cy.contains('table tbody tr', email, { timeout: 8000 })
            .should('exist')
            .within(() => {
                cy.get('a.btn-primary')
                    .should('have.attr', 'href')
                    .then(url => {
                        cy.log(`Captured ${envKey} edit URL:`, url);
                        Cypress.env(envKey, url);
                    });
            });
    };

    // ================================
    // COURSE MANAGEMENT
    // ================================
    describe('Course Management', () => {

        it('TC-06: Add a new course', () => {
            setupCourseName = 'Cypress Course ' + Date.now();
            cy.navigateTo('Add Course');
            cy.get('#id_name').type(setupCourseName);
            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Added').should('be.visible');
        });

        it('TC-07: Add course with empty name (BVA)', () => {
            cy.navigateTo('Add Course');
            cy.get('#id_name').clear();
            cy.get('button[type="submit"]').click();

            cy.get('#id_name')
                .invoke('prop', 'validationMessage')
                .should('not.be.empty');

            cy.url().should('include', '/course/add');
        });

    });

    // ================================
    // STAFF MANAGEMENT
    // ================================
    describe('Staff Management', () => {

        it('TC-16: Add new staff member', () => {
            const timestamp = Date.now();
            setupStaffEmail = `staff${timestamp}@test.com`;

            cy.navigateTo('Add Staff');
            cy.get('#id_first_name').type('Test');
            cy.get('#id_last_name').type(`Staff${timestamp}`);
            cy.get('#id_email').type(setupStaffEmail);
            cy.get('#id_password').type('123456789');
            cy.get('#id_address').type('123 Test St');

            cy.get('#id_profile_pic').selectFile('cypress/fixtures/images/profile.jpg', { force: true });
            cy.get('#id_course').select(1);
            cy.get('button[type="submit"]').click();

            cy.contains('Successfully Added').should('be.visible');

            // Capture the edit URL for TC-19
            captureEditUrl(setupStaffEmail, 'staffEditUrl');
        });

        it('TC-17: Add staff with invalid email', () => {
            cy.navigateTo('Add Staff');

            cy.get('#id_first_name').type('Test');
            cy.get('#id_last_name').type('Invalid');
            cy.get('#id_email').type('invalid-email-format');
            cy.get('#id_password').type('123456');
            cy.get('#id_address').type('Address');

            cy.get('button[type="submit"]').click();

            cy.get('#id_email')
                .invoke('prop', 'validationMessage')
                .should('not.be.empty');
        });

        it('TC-18: Duplicate email validation (AJAX)', () => {
            cy.navigateTo('Add Staff');

            cy.get('#id_email').type(setupStaffEmail);
            cy.get('#id_first_name').type('Duplicate');
            cy.get('#id_last_name').type('User');
            cy.get('#id_password').type('123456');
            cy.get('#id_address').type('Address');
            cy.get('#id_profile_pic').selectFile('cypress/fixtures/images/profile.jpg', { force: true });
            cy.get('#id_course').select(1);

            cy.get('#id_email').trigger('change');

            cy.contains('Email Address Already Exist', { timeout: 8000 }).should('be.visible');
        });

    });

    // ================================
    // SUBJECT MANAGEMENT
    // ================================
    describe('Subject Management', () => {

        it('TC-09: Add new subject', () => {
            const subjectName = 'Cypress Subject ' + Date.now();
            cy.navigateTo('Add Subject');

            cy.get('#id_name').type(subjectName);
            cy.get('#id_course').select(1);
            cy.get('#id_staff').select(1);

            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Added').should('be.visible');
        });

        it('TC-10: Add subject with empty name (BVA)', () => {
            cy.navigateTo('Add Subject');

            cy.get('#id_name').clear();
            cy.get('#id_course').select(1);
            cy.get('#id_staff').select(1);

            cy.get('button[type="submit"]').click();

            cy.get('#id_name')
                .invoke('prop', 'validationMessage')
                .should('not.be.empty');
        });

    });

    // ================================
    // SESSION MANAGEMENT
    // ================================
    describe('Session Management', () => {

        it('TC-13: Add session year', () => {
            cy.navigateTo('Add Session');

            cy.get('#id_start_year').type('2025-01-01');
            cy.get('#id_end_year').type('2025-12-31');

            cy.get('button[type="submit"]').click();
            cy.contains('Session Created').should('be.visible');
        });

        it('TC-15: Empty dates validation', () => {
            cy.navigateTo('Add Session');

            cy.get('#id_start_year').clear();
            cy.get('button[type="submit"]').click();

            cy.get('#id_start_year')
                .invoke('prop', 'validationMessage')
                .should('not.be.empty');
        });

    });

    // ================================
    // STUDENT MANAGEMENT
    // ================================
    describe('Student Management', () => {

        it('TC-21: Add new student', () => {
            const timestamp = Date.now();
            const studentEmail = `student${timestamp}@test.com`;

            cy.navigateTo('Add Student');

            cy.get('#id_first_name').type('Test');
            cy.get('#id_last_name').type('Student');
            cy.get('#id_email').type(studentEmail);
            cy.get('#id_password').type('123456');
            cy.get('#id_address').type('123 Test St');
            cy.get('#id_gender').select('Male');
            cy.get('#id_course').select(1);
            cy.get('#id_session').select(1);

            cy.get('#id_profile_pic').selectFile('cypress/fixtures/images/profile.jpg', { force: true });

            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Added').should('be.visible');
        });

        it('TC-23: Duplicate student email validation (AJAX)', () => {
            const timestamp = Date.now();
            const dupEmail = `dup_student${timestamp}@test.com`;

            // First student
            cy.navigateTo('Add Student');
            cy.get('#id_first_name').type('First');
            cy.get('#id_last_name').type('Student');
            cy.get('#id_email').type(dupEmail);
            cy.get('#id_password').type('123456');
            cy.get('#id_address').type('Address');
            cy.get('#id_gender').select('Female');
            cy.get('#id_course').select(1);
            cy.get('#id_session').select(1);
            cy.get('#id_profile_pic').selectFile('cypress/fixtures/images/profile.jpg', { force: true });
            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Added').should('be.visible');

            // Duplicate student
            cy.navigateTo('Add Student');
            cy.get('#id_email').type(dupEmail);
            cy.get('#id_first_name').type('Second');
            cy.get('#id_last_name').type('Student');
            cy.get('#id_password').type('123456');
            cy.get('#id_address').type('Address');
            cy.get('#id_gender').select('Female');
            cy.get('#id_course').select(1);
            cy.get('#id_session').select(1);

            cy.get('#id_email').trigger('change');

            cy.contains('Email Address Already Exist', { timeout: 8000 }).should('be.visible');
        });

    });

    // ================================
    // EDIT & DELETE WORKFLOWS
    // ================================
    describe('Edit/Delete Workflows', () => {

        // ---- COURSE ----
        it('TC-08: Edit course', () => {
            cy.navigateTo('Manage Course');

            cy.get('table tbody tr').last().find('.btn-primary').click();
            cy.url().should('include', '/course/edit/');

            const newName = 'Updated Course ' + Date.now();
            cy.get('#id_name').clear().type(newName);

            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Updated').should('be.visible');
        });

        it('TC-08-A: Delete course', () => {
            cy.navigateTo('Manage Course');
            cy.on('window:confirm', () => true);

            cy.get('table tbody tr').last().find('.btn-danger').click();
            cy.contains('Course deleted successfully').should('be.visible');
        });

        // ---- SUBJECT ----
        it('TC-11: Edit subject', () => {
            cy.navigateTo('Manage Subject');

            cy.get('table tbody tr').last().find('.btn-primary').click();
            cy.url().should('include', '/subject/edit/');

            const newName = 'Updated Subject ' + Date.now();
            cy.get('#id_name').clear().type(newName);

            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Updated').should('be.visible');
        });

        it('TC-12: Delete subject', () => {
            cy.navigateTo('Manage Subject');
            cy.on('window:confirm', () => true);

            cy.get('table tbody tr').last().find('.btn-danger').click();
            cy.contains('Subject deleted successfully').should('be.visible');
        });

        // ---- STAFF ----
        it('TC-19: Edit staff', () => {
            const editUrl = Cypress.env('staffEditUrl');

            expect(editUrl, 'Edit URL must be captured from TC-16').to.be.a('string');

            cy.visit(editUrl);

            cy.get('#id_first_name', { timeout: 10000 })
                .should('be.visible')
                .clear()
                .type('UpdatedName');

            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Updated').should('be.visible');
        });

        it('TC-20: Delete staff', () => {
            cy.navigateTo('Manage Staff');
            cy.on('window:confirm', () => true);

            cy.get('table tbody tr').last().find('.btn-danger').click();
            cy.contains('Staff deleted successfully').should('be.visible');
        });

        // ---- STUDENT ----
        it('TC-24: Edit student', () => {
            cy.navigateTo('Manage Student');

            cy.get('table tbody tr').last().find('.btn-primary').click();
            cy.url().should('include', '/student/edit/');

            cy.get('#id_first_name')
                .clear()
                .type('UpdatedStudent');

            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Updated').should('be.visible');
        });

        it('TC-24-A: Delete student', () => {
            cy.navigateTo('Manage Student');
            cy.on('window:confirm', () => true);

            cy.get('table tbody tr').last().find('.btn-danger').click();
            cy.contains('Student deleted successfully').should('be.visible');
        });

    });

});
