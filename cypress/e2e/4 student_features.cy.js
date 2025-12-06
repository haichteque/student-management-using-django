import 'cypress-file-upload';

describe('Student Features Test Suite', () => {
    const adminEmail = 'ijtaba@ijtaba.com';
    const adminPassword = 'ijtaba';

    // --- Global Test Data ---
    const timestamp = Date.now();
    const studentEmail = `student_feature_${timestamp}@test.com`;
    const studentPassword = 'password123';
    const studentName = `StudentFeature${timestamp}`;
    const courseName = `CourseFeature${timestamp}`;

    before(() => {
        cy.login(adminEmail, adminPassword);

        // Create Course first
        cy.navigateTo('Add Course');
        cy.get('#id_name').type(courseName);
        cy.get('button[type="submit"]').click();
        cy.contains('Successfully Added', { timeout: 5000 }).should('be.visible');

        // Create Student
        cy.navigateTo('Add Student');
        cy.get('#id_first_name').type('Test');
        cy.get('#id_last_name').type('Student');
        cy.get('#id_email').type(studentEmail);
        cy.get('#id_password').type(studentPassword);
        cy.get('#id_address').type('123 Test St');
        cy.get('#id_gender').select('Male');

        // Select the course we just created
        cy.get('#id_course').should('be.visible').then($select => {
            const option = $select.find('option').filter((i, el) => el.text === courseName);
            if (option.length) {
                cy.get('#id_course').select(option.val());
            } else {
                cy.log('Course option not found!');
            }
        });

        cy.get('#id_session').select(1);
        cy.get('#id_profile_pic').selectFile('cypress/fixtures/images/profile.jpg', { force: true });

        cy.get('button[type="submit"]').click();
        cy.contains('Successfully Added', { timeout: 5000 }).should('be.visible');

        // Logout Admin
        cy.contains('Logout').click({ force: true });
    });

    beforeEach(() => {
        cy.login(studentEmail, studentPassword);
    });

    // -------------------------------
    // View Attendance
    // -------------------------------
    it('TC-34: Verify viewing attendance records', () => {
        cy.navigateTo('View Attendance');
        cy.contains('View Attendance', { timeout: 5000 }).should('be.visible');

        cy.contains('Fetch Attendance').should('exist');
    });

    // -------------------------------
    // View Results
    // -------------------------------
    it('TC-35: Verify viewing exam results', () => {
        cy.navigateTo('View Results');
        cy.contains('View Result', { timeout: 5000 }).should('be.visible');
    });

    // -------------------------------
    // Apply Leave
    // -------------------------------
    it('TC-36: Verify applying for leave with valid date', () => {
        cy.navigateTo('Apply For Leave');
        cy.get('#id_date').type('2025-12-30');
        cy.get('#id_message').type('New Year Holiday');
        cy.get('button[type="submit"]').click();
        cy.contains('Application for leave has been submitted', { timeout: 5000 }).should('be.visible');
    });

    it('TC-37: Verify applying for leave with empty date (BVA)', () => {
        cy.navigateTo('Apply For Leave');
        cy.get('#id_message').type('Missing Date');
        cy.get('button[type="submit"]').click();

        cy.get('#id_date').then($input => {
            expect($input[0].validationMessage).to.not.be.empty;
        });
    });

    // -------------------------------
    // Feedback
    // -------------------------------
    it('TC-38: Verify sending feedback to admin', () => {
        cy.navigateTo('Feedback');
        cy.get('#id_feedback').type('Student Feedback Message');
        cy.get('button[type="submit"]').click();
        cy.contains('Feedback submitted', { timeout: 5000 }).should('be.visible');
    });

    // -------------------------------
    // Notifications
    // -------------------------------
    it('TC-39: Verify View Notifications', () => {
        cy.navigateTo('View Notifications');
        cy.contains('Notification', { timeout: 5000 }).should('be.visible');
    });

    // -------------------------------
    // Profile
    // -------------------------------
    it('TC-40: Verify View/Edit Profile', () => {
        cy.navigateTo('View/Edit Profile');
        cy.contains('Edit Profile', { timeout: 5000 }).should('be.visible');
        cy.get('input[name="first_name"]').should('be.visible');
        cy.get('button[type="submit"]').should('be.visible');
    });
});
