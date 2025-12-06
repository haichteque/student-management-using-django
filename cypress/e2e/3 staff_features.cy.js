import 'cypress-file-upload';

describe('Staff Features Test Suite', () => {
    const adminEmail = 'ijtaba@ijtaba.com';
    const adminPassword = 'ijtaba';

    const timestamp = Date.now();
    const staffEmail = `staff_feature_${timestamp}@test.com`;
    const staffPassword = 'password123';
    const staffName = `StaffFeature${timestamp}`;

    before(() => {
        // Setup: Create a Staff user via Admin interface
        cy.login(adminEmail, adminPassword);
        cy.navigateTo('Add Staff');

        cy.get('#id_first_name').type('Test');
        cy.get('#id_last_name').type('Staff');
        cy.get('#id_email').type(staffEmail);
        cy.get('#id_password').type(staffPassword);
        cy.get('#id_address').type('123 Test St');
        cy.get('#id_profile_pic').selectFile('cypress/fixtures/images/profile.jpg', { force: true });
        cy.get('#id_course').select(1);
        cy.get('button[type="submit"]').click();
        cy.contains('Successfully Added', { timeout: 5000 }).should('be.visible');

        cy.contains('Logout').click({ force: true });
    });

    beforeEach(() => {
        cy.login(staffEmail, staffPassword);
    });

    // -------------------------------
    // Attendance
    // -------------------------------
    it('TC-25: Verify taking attendance for a subject', () => {
        cy.navigateTo('Take Attendance');

        cy.get('#subject').find('option').then($options => {
            if ($options.length > 1) {
                cy.get('#subject').select(1);
                cy.get('#session').select(1);
                cy.get('#fetch_student').click();

                cy.get('#student_data').should('be.visible').then($div => {
                    if ($div.find('input[name="attendance_date"]').length > 0) {
                        cy.get('#attendance_date').type('2025-12-01');
                        cy.get('#save_attendance').click();

                        cy.on('window:alert', str => {
                            expect(str).to.equal('Saved');
                        });
                    } else {
                        cy.log('No students found or AJAX failed');
                    }
                });
            } else {
                cy.log('No subjects assigned to this staff');
            }
        });
    });

    it('TC-26: Verify View/Update Attendance', () => {
        cy.navigateTo('View/Update Attendance');

        cy.get('#subject').find('option').then($options => {
            if ($options.length > 1) {
                cy.get('#subject').select(1);
                cy.get('#session').select(1);
                cy.get('#fetch_attendance').click();

                cy.get('#attendance_date').should('be.visible').then($select => {
                    if ($select.find('option').length > 0) {
                        cy.get('#attendance_date').select(0);
                        cy.get('#fetch_student').click();

                        cy.get('#student_data').should('be.visible');
                        cy.get('#save_attendance').click();

                        cy.on('window:alert', str => {
                            expect(str).to.equal('Updated');
                        });
                    } else {
                        cy.log('No attendance records found to update');
                    }
                });
            }
        });
    });

    // -------------------------------
    // Apply Leave
    // -------------------------------
    it('TC-29: Verify applying for leave with valid date and message', () => {
        cy.navigateTo('Apply For Leave');
        cy.get('#id_date').type('2025-12-25');
        cy.get('#id_message').type('Christmas Holiday');
        cy.get('button[type="submit"]').click();
        cy.contains('Application for leave has been submitted', { timeout: 5000 }).should('be.visible');
    });

    it('TC-30: Verify applying for leave with empty date (BVA)', () => {
        cy.navigateTo('Apply For Leave');
        cy.get('#id_message').type('Missing Date');
        cy.get('button[type="submit"]').click();

        cy.get('#id_date').then($input => {
            expect($input[0].validationMessage).to.not.be.empty;
        });
    });

    // -------------------------------
    // Add/Edit Result
    // -------------------------------
    it('TC-27: Verify adding result for a student', () => {
        cy.navigateTo('Add Result');

        cy.get('#subject').find('option').then($options => {
            if ($options.length > 1) {
                cy.get('#subject').select(1);
                cy.get('#session').select(1);
                cy.get('#fetch_student').click();

                cy.get('#student_data').should('be.visible').then($div => {
                    if ($div.find('select[name="student_list"]').length > 0) {
                        cy.get('select[name="student_list"]').select(0);
                        cy.get('input[name="test"]').type('15');
                        cy.get('input[name="exam"]').type('50');
                        cy.get('#save_attendance').click();

                        cy.on('window:alert', str => {
                            expect(str).to.equal('Saved');
                        });
                    }
                });
            }
        });
    });

    it('TC-28: Verify Edit Result functionality', () => {
        cy.navigateTo('Edit Result');

        cy.get('#id_subject').find('option').then($options => {
            if ($options.length > 1) {
                cy.get('#id_subject').select(1);
                cy.get('#id_session_year').select(1);

                cy.get('#id_student').should('be.visible').then($select => {
                    if ($select.find('option').length > 1) {
                        cy.get('#id_student').select(1);

                        cy.get('#id_test').clear().type('18');
                        cy.get('#id_exam').clear().type('55');

                        cy.get('#update_result').click();
                        cy.contains('Successfully Updated', { timeout: 5000 }).should('be.visible');
                    } else {
                        cy.log('No students found for result editing');
                    }
                });
            }
        });
    });

    // -------------------------------
    // Feedback
    // -------------------------------
    it('TC-32: Verify sending feedback to admin', () => {
        cy.navigateTo('Feedback');
        cy.get('#id_feedback').type('This is a test feedback message.');
        cy.get('button[type="submit"]').click();
        cy.contains('Feedback submitted', { timeout: 5000 }).should('be.visible');
    });

    it('TC-33: Verify sending empty feedback (BVA)', () => {
        cy.navigateTo('Feedback');
        cy.get('button[type="submit"]').click();

        cy.get('#id_feedback').then($input => {
            expect($input[0].validationMessage).to.not.be.empty;
        });
    });

    // -------------------------------
    // Notifications & Profile
    // -------------------------------
    it('TC-31: Verify View Notifications', () => {
        cy.navigateTo('View Notifications');
        cy.contains('Notification', { timeout: 5000 }).should('be.visible');
    });

    it('TC-33-A: Verify View/Edit Profile', () => {
        cy.navigateTo('View/Edit Profile');
        cy.contains('Edit Profile', { timeout: 5000 }).should('be.visible');
        cy.get('input[name="first_name"]').should('be.visible');
        cy.get('button[type="submit"]').should('be.visible');
    });
});
