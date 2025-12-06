import 'cypress-file-upload';
describe('Admin Features Test Suite', () => {
    const adminEmail = 'ijtaba@ijtaba.com';
    const adminPassword = 'ijtaba';

    // --- Global Test Data ---
    let setupCourseName;
    let setupStaffEmail;

    beforeEach(() => {
        cy.login(adminEmail, adminPassword);
    });

    // --- Manage Course ---
    describe('Course Management', () => {
        it('TC-06: Verify adding a new course with valid data (and setup for subjects)', () => {
            setupCourseName = 'Cypress Course ' + Date.now();
            cy.navigateTo('Add Course');
            // ID derived from CourseForm field 'name'
            cy.get('#id_name').type(setupCourseName);
            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Added').should('be.visible');
        });

        it('TC-07: Verify adding a course with empty name (BVA)', () => {
            cy.navigateTo('Add Course');
            // Ensure field is empty and required
            cy.get('#id_name').clear().should('have.prop', 'required');

            cy.get('button[type="submit"]').click();

            // Assert browser validation message
            cy.get('#id_name').then(($input) => {
                expect($input[0].validationMessage).to.not.be.empty;
            });
            cy.url().should('include', '/course/add');
        });
    });

    // --- Manage Staff ---
    describe('Staff Management', () => {
        it('TC-16: Verify adding a new staff member with valid data (and setup for subjects)', () => {
            const timestamp = Date.now();
            setupStaffEmail = `staff${timestamp}@test.com`;

            cy.navigateTo('Add Staff');
            // IDs derived from CustomUserForm fields
            cy.get('#id_first_name').type('Test');
            cy.get('#id_last_name').type(`Staff${timestamp}`);
            cy.get('#id_email').type(setupStaffEmail);
            cy.get('#id_password').type('123456789');
            cy.get('#id_address').type('123 Test St');

            //File Upload
            cy.fixture('images/profile.jpg', 'base64').then(fileContent => {
                cy.get('#id_profile_pic').attachFile({
                    fileContent: fileContent,
                    fileName: 'profile.jpg',
                    mimeType: 'image/jpeg'
                });
            });
            cy.get('#id_profile_pic').selectFile('cypress/fixtures/images/profile.jpg');
            cy.wait(1000);
            cy.get('#id_course').select(2);
            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Added').should('be.visible');
        });

        it('TC-17: Verify adding staff with invalid email format (BVA)', () => {
            cy.navigateTo('Add Staff');
            cy.get('#id_first_name').type('Test');
            cy.get('#id_last_name').type('Invalid');
            cy.get('#id_email').type('invalid-email-format');
            cy.get('#id_password').type('123456');
            cy.get('#id_address').type('Address');

            cy.get('button[type="submit"]').click();

            // Browser validation
            cy.get('#id_email').then(($input) => {
                expect($input[0].validationMessage).to.not.be.empty;
            });
        });

        it('TC-18: Verify duplicate email validation (AJAX)', () => {
            const email = setupStaffEmail;

            cy.navigateTo('Add Staff');
            cy.get('#id_email').type(email);

            // Fill other required fields
            cy.get('#id_first_name').type('Duplicate');
            cy.get('#id_last_name').type('User');
            cy.get('#id_password').type('123456');
            cy.get('#id_address').type('Address');
            cy.get('#id_profile_pic').selectFile('cypress/fixtures/images/profile.jpg');
            cy.get('#id_course').select(1);
            // Trigger AJAX
            cy.get('#id_email').trigger('keyup'); // or blur
            cy.wait(1000); // Wait for AJAX

            cy.contains('Email Address Already Exist').should('be.visible');
        });
    });

    // --- Manage Subject ---
    describe('Subject Management', () => {
        it('TC-09: Verify adding a new subject with valid data', () => {
            const subjectName = 'Cypress Subject ' + Date.now();
            cy.navigateTo('Add Subject');
            cy.get('#id_name').type(subjectName);

            // Select first available course and staff (created in previous tests)
            cy.get('#id_course').select(1);
            cy.get('#id_staff').select(1);

            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Added').should('be.visible');
        });

        it('TC-10: Verify adding a subject with empty name (BVA)', () => {
            cy.navigateTo('Add Subject');
            cy.get('#id_name').clear().should('have.prop', 'required');
            cy.get('#id_course').select(1);
            cy.get('#id_staff').select(1);

            cy.get('button[type="submit"]').click();

            cy.get('#id_name').then(($input) => {
                expect($input[0].validationMessage).to.not.be.empty;
            });
        });
    });

    // --- Manage Session ---
    describe('Session Management', () => {
        it('TC-13: Verify adding a new session year with valid dates', () => {
            cy.navigateTo('Add Session');
            // Date inputs usually require YYYY-MM-DD
            cy.get('#id_start_year').type('2025-01-01');
            cy.get('#id_end_year').type('2025-12-31');
            cy.get('button[type="submit"]').click();
            cy.contains('Session Created').should('be.visible');
        });

        it('TC-15: Verify adding session with empty dates (BVA)', () => {
            cy.navigateTo('Add Session');
            cy.get('#id_start_year').clear().should('have.prop', 'required');
            cy.get('button[type="submit"]').click();

            cy.get('#id_start_year').then(($input) => {
                expect($input[0].validationMessage).to.not.be.empty;
            });
        });
    });

    // --- Manage Student ---
    describe('Student Management', () => {
        it('TC-21: Verify adding a new student with valid data', () => {
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
            cy.get('#id_profile_pic').selectFile('cypress/fixtures/images/profile.jpg');
            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Added').should('be.visible');
        });

        it('TC-23: Verify duplicate student email validation (AJAX)', () => {
            const timestamp = Date.now();
            const email = `dup_student${timestamp}@test.com`;

            // Create first student
            cy.navigateTo('Add Student');
            cy.get('#id_first_name').type('First');
            cy.get('#id_last_name').type('Student');
            cy.get('#id_email').type(email);
            cy.get('#id_password').type('123456');
            cy.get('#id_address').type('Address');
            cy.get('#id_gender').select('Female');
            cy.get('#id_course').select(1);
            cy.get('#id_session').select(1);
            cy.get('#id_profile_pic').selectFile('cypress/fixtures/images/profile.jpg');
            cy.get('button[type="submit"]').click();
            cy.contains('Successfully Added').should('be.visible');

            cy.wait(2000);
            // Try to create second student with same email
            //cy.navigateTo('Add Student');
            cy.get('#id_email').type(email);

            // Fill other fields
            cy.get('#id_first_name').type('Second');
            cy.get('#id_last_name').type('Student');
            cy.get('#id_password').type('123456');
            cy.get('#id_address').type('Address');
            cy.get('#id_gender').select('Female');
            cy.get('#id_course').select(1);
            cy.get('#id_session').select(1);
            cy.get('#id_email').trigger('keyup');
            cy.get('#id_profile_pic').selectFile('cypress/fixtures/images/profile.jpg');
            cy.wait(1000);

            cy.contains('Email Address Already Exist').should('be.visible');
        });
    });

    // --- Extended Coverage: Manage & Edit/Delete Workflows ---

    describe('Course Management - Extended', () => {
        it('TC-08: Verify Manage Course page and Edit functionality', () => {
            cy.navigateTo('Manage Course');
            cy.contains('Manage Course').should('be.visible');
            cy.get('table').should('exist');

            // Click Edit on the last course (likely the one we just added)
            cy.get('table tbody tr').last().find('.btn-primary').click();

            // Verify Edit Page
            cy.url().should('include', '/course/edit/');
            cy.contains('Edit Course').should('be.visible');

            // Update Name
            const newName = 'Updated Course ' + Date.now();
            cy.get('#id_name').clear().type(newName);
            cy.get('button[type="submit"]').click();

            cy.contains('Successfully Updated').should('be.visible');
        });

        it('TC-08-A: Verify Delete Course functionality', () => {
            cy.navigateTo('Manage Course');

            // Click Delete on the last course
            // Stub window.confirm to return true
            cy.on('window:confirm', () => true);

            cy.get('table tbody tr').last().find('.btn-danger').click();

            cy.contains('Course deleted successfully').should('be.visible');
        });
    });

    describe('Subject Management - Extended', () => {
        it('TC-11: Verify Manage Subject page and Edit functionality', () => {
            cy.navigateTo('Manage Subject');
            cy.contains('Manage Subject').should('be.visible');

            cy.get('table tbody tr').last().find('.btn-primary').click();

            cy.url().should('include', '/subject/edit/');
            cy.contains('Edit Subject').should('be.visible');

            const newName = 'Updated Subject ' + Date.now();
            cy.get('#id_name').clear().type(newName);
            cy.get('button[type="submit"]').click();

            cy.contains('Successfully Updated').should('be.visible');
        });

        it('TC-12: Verify Delete Subject functionality', () => {
            cy.navigateTo('Manage Subject');
            cy.on('window:confirm', () => true);
            cy.get('table tbody tr').last().find('.btn-danger').click();
            cy.contains('Subject deleted successfully').should('be.visible');
        });
    });

    describe('Staff Management - Extended', () => {
        it('TC-19: Verify Manage Staff page and Edit functionality', () => {
            cy.navigateTo('Manage Staff');
            cy.contains('Manage Staff').should('be.visible');

            cy.get('table tbody tr').last().find('.btn-primary').click();

            cy.url().should('include', '/staff/edit/');
            cy.contains('Edit Staff').should('be.visible');

            cy.get('#id_first_name').clear().type('UpdatedName');
            cy.get('button[type="submit"]').click();

            cy.contains('Successfully Updated').should('be.visible');
        });

        it('TC-20: Verify Delete Staff functionality', () => {
            cy.navigateTo('Manage Staff');
            cy.on('window:confirm', () => true);
            cy.get('table tbody tr').last().find('.btn-danger').click();
            cy.contains('Staff deleted successfully').should('be.visible');
        });
    });

    describe('Student Management - Extended', () => {
        it('TC-24: Verify Manage Student page and Edit functionality', () => {
            cy.navigateTo('Manage Student');
            cy.contains('Manage Student').should('be.visible');

            cy.get('table tbody tr').last().find('.btn-primary').click();

            cy.url().should('include', '/student/edit/');
            cy.contains('Edit Student').should('be.visible');

            cy.get('#id_first_name').clear().type('UpdatedStudent');
            cy.get('button[type="submit"]').click();

            cy.contains('Successfully Updated').should('be.visible');
        });

        it('TC-24-A: Verify Delete Student functionality', () => {
            cy.navigateTo('Manage Student');
            cy.on('window:confirm', () => true);
            cy.get('table tbody tr').last().find('.btn-danger').click();
            cy.contains('Student deleted successfully').should('be.visible');
        });
    });
});