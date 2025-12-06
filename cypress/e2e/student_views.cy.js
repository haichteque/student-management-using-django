// This file assumes 'cypress-file-upload' plugin is installed and configured if you're running the 'should upload a profile picture successfully' test.
// For example, by adding `import 'cypress-file-upload';` to your cypress/support/e2e.js or cypress/support/index.js.

const BASE_URL = 'http://127.0.0.1:8000';

Cypress.Commands.add('loginStudent', () => {
  cy.visit(`${BASE_URL}/login/`);
  cy.get('input[name="email"]').type('qasim@nu.edu.pk');
  cy.get('input[name="password"]').type('123', { log: false });
  cy.get('form').submit();
  cy.url().should('include', '/student_home');
  cy.contains('Student Homepage').should('be.visible');
});

describe('Student Module E2E Tests', () => {

  beforeEach(() => {
    cy.loginStudent();
  });

  describe('Student Home Page', () => {
    it('should display the student dashboard with attendance summary and subjects', () => {
      cy.url().should('eq', `${BASE_URL}/student_home/`);
      cy.get('h3').contains('Student Homepage').should('be.visible');
      cy.get('.card-total-attendance').should('exist');
      cy.get('.card-percent-present').should('exist');
      cy.get('.card-percent-absent').should('exist');
      cy.get('.card-total-subject').should('exist');
      cy.get('canvas#attendanceChart').should('be.visible');
      cy.get('.subject-list-container').should('exist');
    });
  });

  describe('Student View Attendance', () => {
    it('should display the attendance view form with subject and date inputs', () => {
      cy.visit(`${BASE_URL}/student_view_attendance/`);
      cy.url().should('eq', `${BASE_URL}/student_view_attendance/`);
      cy.get('h3').contains('View Attendance').should('be.visible');
      cy.get('select[name="subject"]').should('be.visible');
      cy.get('input[name="start_date"][type="date"]').should('be.visible');
      cy.get('input[name="end_date"][type="date"]').should('be.visible');
      cy.get('button[type="submit"]').contains('Fetch Attendance').should('be.visible');
    });

    it('should fetch attendance data via POST request and display it', () => {
      cy.intercept('POST', `${BASE_URL}/student_view_attendance/`).as('fetchAttendance');

      cy.visit(`${BASE_URL}/student_view_attendance/`);

      cy.get('select[name="subject"]').select('1', { force: true });
      cy.get('input[name="start_date"]').type('2023-01-01');
      cy.get('input[name="end_date"]').type('2023-01-31');
      cy.get('form').submit();

      cy.wait('@fetchAttendance').then((interception) => {
        expect(interception.request.body).to.include('subject=1');
        expect(interception.request.body).to.include('start_date=2023-01-01');
        expect(interception.request.body).to.include('end_date=2023-01-31');
        expect(interception.response.statusCode).to.eq(200);
        expect(interception.response.body).to.be.a('string');
        const responseBody = JSON.parse(interception.response.body);
        expect(responseBody).to.be.an('array');
        if (responseBody.length > 0) {
          expect(responseBody[0]).to.have.all.keys('date', 'status');
          cy.get('.attendance-data-display').should('exist');
        } else {
          cy.get('.no-attendance-data-message').should('exist');
        }
      });
    });
  });

  describe('Student Apply Leave', () => {
    it('should display the leave application form and history table', () => {
      cy.visit(`${BASE_URL}/student_apply_leave/`);
      cy.url().should('eq', `${BASE_URL}/student_apply_leave/`);
      cy.get('h3').contains('Apply for leave').should('be.visible');
      cy.get('input[name="start_date"][type="date"]').should('be.visible');
      cy.get('input[name="end_date"][type="date"]').should('be.visible');
      cy.get('textarea[name="message"]').should('be.visible');
      cy.get('button[type="submit"]').contains('Apply for Leave').should('be.visible');
      cy.get('.leave-history-table').should('exist');
    });

    it('should submit a new leave application successfully and show in history', () => {
      cy.visit(`${BASE_URL}/student_apply_leave/`);
      const today = Cypress.moment().format('YYYY-MM-DD');
      const tomorrow = Cypress.moment().add(1, 'days').format('YYYY-MM-DD');
      const leaveMessage = `Cypress leave request ${Cypress._.random(0, 1e6)}`;

      cy.get('input[name="start_date"]').type(today);
      cy.get('input[name="end_date"]').type(tomorrow);
      cy.get('textarea[name="message"]').type(leaveMessage);
      cy.get('form').submit();

      cy.url().should('eq', `${BASE_URL}/student_apply_leave/`);
      cy.get('.alert-success').contains('Application for leave has been submitted for review').should('be.visible');
      cy.get('.leave-history-table tbody').contains(leaveMessage).should('be.visible');
    });

    it('should show an error message for invalid leave application data (e.g., end date before start date)', () => {
      cy.visit(`${BASE_URL}/student_apply_leave/`);
      const today = Cypress.moment().format('YYYY-MM-DD');
      const yesterday = Cypress.moment().subtract(1, 'days').format('YYYY-MM-DD');

      cy.get('input[name="start_date"]').type(today);
      cy.get('input[name="end_date"]').type(yesterday);
      cy.get('textarea[name="message"]').type('Invalid date range test');
      cy.get('form').submit();

      cy.url().should('eq', `${BASE_URL}/student_apply_leave/`);
      cy.get('.alert-error').contains('Form has errors!').should('be.visible');
      cy.get('.leave-history-table').should('not.contain', 'Invalid date range test');
    });
  });

  describe('Student Feedback', () => {
    it('should display the feedback form and history', () => {
      cy.visit(`${BASE_URL}/student_feedback/`);
      cy.url().should('eq', `${BASE_URL}/student_feedback/`);
      cy.get('h3').contains('Student Feedback').should('be.visible');
      cy.get('textarea[name="message"]').should('be.visible');
      cy.get('button[type="submit"]').contains('Submit Feedback').should('be.visible');
      cy.get('.feedback-history-table').should('exist');
    });

    it('should submit new feedback successfully and display it in history', () => {
      cy.visit(`${BASE_URL}/student_feedback/`);
      const feedbackMessage = `Great experience with the system! ${Cypress._.random(0, 1e6)}`;

      cy.get('textarea[name="message"]').type(feedbackMessage);
      cy.get('form').submit();

      cy.url().should('eq', `${BASE_URL}/student_feedback/`);
      cy.get('.alert-success').contains('Feedback submitted for review').should('be.visible');
      cy.get('.feedback-history-table tbody').contains(feedbackMessage).should('be.visible');
    });

    it('should show an error message for invalid feedback data (e.g., empty message if required)', () => {
      cy.visit(`${BASE_URL}/student_feedback/`);
      cy.get('textarea[name="message"]').clear();
      cy.get('form').submit();

      cy.url().should('eq', `${BASE_URL}/student_feedback/`);
      cy.get('.alert-error').contains('Form has errors!').should('be.visible');
    });
  });

  describe('Student View/Edit Profile', () => {
    it('should display the profile edit form with current student data', () => {
      cy.visit(`${BASE_URL}/student_view_profile/`);
      cy.url().should('eq', `${BASE_URL}/student_view_profile/`);
      cy.get('h3').contains('View/Edit Profile').should('be.visible');
      cy.get('input[name="first_name"]').should('have.value', 'Qasim');
      cy.get('input[name="last_name"]').should('have.value', 'Student');
      cy.get('input[name="address"]').should('exist');
      cy.get('select[name="gender"]').should('exist');
      cy.get('input[type="file"][name="profile_pic"]').should('exist');
      cy.get('input[name="password"][type="password"]').should('exist');
    });

    it('should update student profile details (first name, address, gender) successfully', () => {
      cy.visit(`${BASE_URL}/student_view_profile/`);
      const newFirstName = `UpdatedFN_${Cypress._.random(0, 1e6)}`;
      const newAddress = `123 Cypress Street, Updated City, CY ${Cypress._.random(0, 1e6)}`;

      cy.get('input[name="first_name"]').clear().type(newFirstName);
      cy.get('input[name="address"]').clear().type(newAddress);
      cy.get('select[name="gender"]').select('Female');

      cy.get('form').submit();

      cy.url().should('eq', `${BASE_URL}/student_view_profile/`);
      cy.get('.alert-success').contains('Profile Updated!').should('be.visible');

      cy.reload();
      cy.get('input[name="first_name"]').should('have.value', newFirstName);
      cy.get('input[name="address"]').should('have.value', newAddress);
      cy.get('select[name="gender"]').should('have.value', 'Female');
    });

    it('should update student password successfully and allow re-login with the new password', () => {
      const originalPassword = '123';
      const newPassword = 'new_secure_password';

      cy.visit(`${BASE_URL}/student_view_profile/`);
      cy.get('input[name="password"]').type(newPassword, { log: false });
      cy.get('form').submit();

      cy.url().should('eq', `${BASE_URL}/student_view_profile/`);
      cy.get('.alert-success').contains('Profile Updated!').should('be.visible');

      cy.visit(`${BASE_URL}/logout/`);
      cy.url().should('include', '/login');

      cy.get('input[name="email"]').type('qasim@nu.edu.pk');
      cy.get('input[name="password"]').type(newPassword, { log: false });
      cy.get('form').submit();
      cy.url().should('include', '/student_home');
      cy.contains('Student Homepage').should('be.visible');

      cy.visit(`${BASE_URL}/student_view_profile/`);
      cy.get('input[name="password"]').type(originalPassword, { log: false });
      cy.get('form').submit();
      cy.get('.alert-success').contains('Profile Updated!').should('be.visible');
    });

    it('should upload a profile picture successfully', () => {
      cy.visit(`${BASE_URL}/student_view_profile/`);
      const fileName = 'cypress_profile_pic.png';

      cy.fixture(fileName, 'binary').then(fileContent => {
        cy.get('input[type="file"][name="profile_pic"]').attachFile({
          fileContent: fileContent,
          fileName: fileName,
          mimeType: 'image/png'
        });
      });

      cy.get('form').submit();

      cy.url().should('eq', `${BASE_URL}/student_view_profile/`);
      cy.get('.alert-success').contains('Profile Updated!').should('be.visible');

      cy.reload();
      cy.get('img.profile-pic').should('have.attr', 'src').and('include', fileName);
    });

    it('should show an error message for invalid profile data', () => {
      cy.visit(`${BASE_URL}/student_view_profile/`);
      cy.get('input[name="first_name"]').clear().type('a');
      cy.get('form').submit();

      cy.url().should('eq', `${BASE_URL}/student_view_profile/`);
      cy.get('.alert-error').contains('Invalid Data Provided').should('be.visible');
    });
  });

  describe('Student FCM Token Update (API Endpoint)', () => {
    it('should successfully update the FCM token via POST request', () => {
      const testToken = `test_fcm_token_${Cypress._.random(0, 1e6)}`;
      cy.request({
        method: 'POST',
        url: `${BASE_URL}/student_fcmtoken/`,
        body: { token: testToken },
        form: true,
      }).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.eq('True');
      });
    });
  });

  describe('Student View Notifications', () => {
    it('should display a list of student notifications', () => {
      cy.visit(`${BASE_URL}/student_view_notification/`);
      cy.url().should('eq', `${BASE_URL}/student_view_notification/`);
      cy.get('h3').contains('View Notifications').should('be.visible');
      cy.get('.notification-list').should('exist');
      cy.get('.notification-list > li').should('have.length.at.least', 0);
    });
  });

  describe('Student View Results', () => {
    it('should display a list of student results', () => {
      cy.visit(`${BASE_URL}/student_view_result/`);
      cy.url().should('eq', `${BASE_URL}/student_view_result/`);
      cy.get('h3').contains('View Results').should('be.visible');
      cy.get('.results-table').should('exist');
      cy.get('.results-table tbody tr').should('have.length.at.least', 0);
    });
  });

});