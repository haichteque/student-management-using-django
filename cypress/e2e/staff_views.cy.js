// cypress/support/commands.js
// This file should be placed in your cypress/support directory.

Cypress.Commands.add('login', (email, password) => {
  cy.session([email, password], () => {
    cy.visit('http://127.0.0.1:8000/login/'); // Assuming a /login/ endpoint
    cy.get('input[name="email"]').type(email);
    cy.get('input[name="password"]').type(password);
    cy.get('form').submit();
    // Assuming a successful login redirects away from /login/
    cy.url().should('not.include', '/login');
  }, {
    // Optional: Add a validation step to ensure the session is still active
    validate() {
      // Visit a known authenticated page and check for an element that confirms login
      cy.visit('http://127.0.0.1:8000/staff_home/', { failOnStatusCode: false });
      cy.get('body').should('not.contain', 'Login'); // Ensure login form is not visible
      cy.get('body').should('contain', 'Staff Panel'); // Ensure staff dashboard content is visible
    }
  });
});

// Helper for getting CSRF token if needed for cy.request to non-csrf_exempt POST endpoints
// (Not strictly necessary for the provided @csrf_exempt views, but good practice for other views)
Cypress.Commands.add('getCsrfToken', () => {
  return cy.request('http://127.0.0.1:8000/login/') // Visit any page that sets a CSRF cookie
    .its('headers')
    .then(headers => {
      const setCookieHeader = headers['set-cookie'];
      const csrftokenMatch = /csrftoken=([^;]+)/.exec(setCookieHeader);
      if (csrftokenMatch && csrftokenMatch[1]) {
        return csrftokenMatch[1];
      }
      return null;
    });
});

// cypress/e2e/staff_e2e_tests.cy.js
// This file should be placed in your cypress/e2e directory.

describe('Staff E2E Tests', () => {
  const BASE_URL = 'http://127.0.0.1:8000';
  const staffCredentials = {
    email: 'bill@ms.com',
    password: '123'
  };

  beforeEach(() => {
    // Log in as staff before each test. Cypress will cache the session.
    cy.login(staffCredentials.email, staffCredentials.password);

    // IMPORTANT: For these tests to pass consistently, your Django test
    // database should be seeded with predictable data:
    // - A staff user (bill@ms.com, 123)
    // - At least one course, subject, session, and student associated with the staff.
    // - Existing attendance records, leave reports, feedback, notifications, and results for update/view tests.
    // Example for seeding data (requires a custom Django management command or `cy.task`):
    // cy.exec('python manage.py seed_test_data');
  });

  it('should display staff home dashboard correctly', () => {
    cy.visit(`${BASE_URL}/staff_home/`);
    cy.url().should('include', '/staff_home/');
    cy.contains('Staff Panel').should('be.visible');
    cy.contains('Total Students').should('be.visible');
    cy.contains('Total Attendance').should('be.visible');
    cy.contains('Total Leave').should('be.visible');
    cy.contains('Total Subjects').should('be.visible');
    cy.get('#attendance-chart').should('exist'); // Assuming a chart element exists with this ID
  });

  it('should navigate to staff take attendance page and display form elements', () => {
    cy.visit(`${BASE_URL}/staff_take_attendance/`);
    cy.url().should('include', '/staff_take_attendance/');
    cy.contains('Take Attendance').should('be.visible');
    cy.get('select[name="subject"]').should('exist');
    cy.get('select[name="session"]').should('exist');
    cy.get('input[type="date"]').should('exist');
    cy.get('button[type="button"]').contains('Fetch Students').should('exist');
  });

  it('should successfully fetch students for attendance via AJAX', () => {
    // This test requires a subject and a session to exist in the database.
    // Using placeholder IDs. In a real scenario, these would be known from test data seeding.
    const subjectId = '1';
    const sessionId = '1';

    cy.request('POST', `${BASE_URL}/get_students/`, {
      subject: subjectId,
      session: sessionId
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.headers['content-type']).to.include('application/json');
      const students = JSON.parse(response.body);
      expect(students).to.be.an('array');
      if (students.length > 0) {
        expect(students[0]).to.have.property('id').and.to.be.a('number');
        expect(students[0]).to.have.property('name').and.to.be.a('string');
      }
    });
  });

  it('should successfully save attendance via AJAX', () => {
    // This test requires a subject, a session, and students to exist.
    // Using placeholder IDs and example student data.
    const subjectId = '1';
    const sessionId = '1';
    const studentIds = [{
      id: 1,
      status: true
    }, {
      id: 2,
      status: false
    }]; // Example: Student 1 present, Student 2 absent
    const attendanceDate = Cypress.moment().format('YYYY-MM-DD');

    cy.request('POST', `${BASE_URL}/save_attendance/`, {
      student_ids: JSON.stringify(studentIds),
      date: attendanceDate,
      subject: subjectId,
      session: sessionId
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.eq('OK');
    });
  });

  it('should navigate to staff update attendance page and display form elements', () => {
    cy.visit(`${BASE_URL}/staff_update_attendance/`);
    cy.url().should('include', '/staff_update_attendance/');
    cy.contains('Update Attendance').should('be.visible');
    cy.get('select[name="subject"]').should('exist');
    cy.get('select[name="session"]').should('exist');
    cy.get('select[name="date"]').should('exist'); // This dropdown will be populated dynamically after subject/session selection
    cy.get('button[type="button"]').contains('Fetch Student Data').should('exist');
  });

  it('should successfully fetch student attendance for a given date via AJAX', () => {
    // This requires an existing Attendance record.
    const attendanceDateId = '1'; // Example ID of an existing Attendance record

    cy.request('POST', `${BASE_URL}/get_student_attendance/`, {
      attendance_date_id: attendanceDateId
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.headers['content-type']).to.include('application/json');
      const studentAttendance = JSON.parse(response.body);
      expect(studentAttendance).to.be.an('array');
      if (studentAttendance.length > 0) {
        expect(studentAttendance[0]).to.have.property('id').and.to.be.a('number');
        expect(studentAttendance[0]).to.have.property('name').and.to.be.a('string');
        expect(studentAttendance[0]).to.have.property('status').and.to.be.a('boolean');
      }
    });
  });

  it('should successfully update attendance via AJAX', () => {
    // This requires an existing Attendance record and AttendanceReport records.
    const attendanceId = '1'; // Example ID of an existing Attendance record
    const updatedStudentData = [{
      id: 1,
      status: false
    }, {
      id: 2,
      status: true
    }]; // Example: Student 1 now absent, Student 2 now present

    cy.request('POST', `${BASE_URL}/update_attendance/`, {
      student_ids: JSON.stringify(updatedStudentData),
      date: attendanceId // The `date` parameter here is the ID of the Attendance object
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.eq('OK');
    });
  });

  it('should allow staff to apply for leave and view history', () => {
    cy.visit(`${BASE_URL}/staff_apply_leave/`);
    cy.url().should('include', '/staff_apply_leave/');
    cy.contains('Apply for Leave').should('be.visible');

    cy.get('input[name="leave_date"]').type('2024-12-25');
    cy.get('textarea[name="message"]').type('Family vacation for Christmas.');
    cy.get('form').submit();

    cy.url().should('include', '/staff_apply_leave/');
    cy.contains('Application for leave has been submitted for review').should('be.visible');
    // Verify the new leave entry appears in the history table
    cy.get('table').contains('td', '2024-12-25').should('be.visible');
    cy.get('table').contains('td', 'Family vacation for Christmas.').should('be.visible');
  });

  it('should allow staff to submit feedback and view history', () => {
    cy.visit(`${BASE_URL}/staff_feedback/`);
    cy.url().should('include', '/staff_feedback/');
    cy.contains('Add Feedback').should('be.visible');

    const feedbackText = 'This is a test feedback from staff for improvement.';
    cy.get('textarea[name="feedback"]').type(feedbackText);
    cy.get('form').submit();

    cy.url().should('include', '/staff_feedback/');
    cy.contains('Feedback submitted for review').should('be.visible');
    // Verify the new feedback appears in the history table
    cy.get('table').contains('td', feedbackText).should('be.visible');
  });

  it('should allow staff to view and update their profile', () => {
    cy.visit(`${BASE_URL}/staff_view_profile/`);
    cy.url().should('include', '/staff_view_profile/');
    cy.contains('View/Update Profile').should('be.visible');

    // Capture initial values to ensure changes are reflected
    let initialFirstName;
    cy.get('input[name="first_name"]').invoke('val').then(val => initialFirstName = val);

    // Fill the form with updated data
    cy.get('input[name="first_name"]').clear().type('UpdatedBill');
    cy.get('input[name="last_name"]').clear().type('UpdatedGates');
    cy.get('input[name="address"]').clear().type('New Address, Seattle');
    cy.get('select[name="gender"]').select('Male'); // Assuming 'Male' is an option

    // Password field is optional; profile_pic upload would require cypress-file-upload plugin
    // For simplicity, skipping password and file upload.
    // Example file upload (requires `cypress-file-upload` plugin and `cy.fixture`):
    // cy.get('input[name="profile_pic"]').attachFile('images/test-profile.png');

    cy.get('form').submit();

    cy.url().should('include', '/staff_view_profile/');
    cy.contains('Profile Updated!').should('be.visible');

    // Verify the updated data is reflected in the form fields
    cy.get('input[name="first_name"]').should('have.value', 'UpdatedBill');
    cy.get('input[name="last_name"]').should('have.value', 'UpdatedGates');
    cy.get('input[name="address"]').should('have.value', 'New Address, Seattle');
    cy.get('select[name="gender"]').should('have.value', 'Male');
  });

  it('should successfully update FCM token via AJAX', () => {
    const newToken = 'test_fcm_token_12345_unique'; // Use a unique token for testing
    cy.request('POST', `${BASE_URL}/staff_fcmtoken/`, {
      token: newToken
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.eq('True');
      // In a more robust test, you might verify this by checking the database or another API endpoint
    });
  });

  it('should display staff notifications', () => {
    cy.visit(`${BASE_URL}/staff_view_notification/`);
    cy.url().should('include', '/staff_view_notification/');
    cy.contains('View Notifications').should('be.visible');
    cy.get('table').should('exist'); // Expect a table of notifications
    cy.get('table tbody tr').should('have.length.greaterThan', 0); // Assuming there's at least one notification
  });

  it('should allow staff to add/update student results', () => {
    cy.visit(`${BASE_URL}/staff_add_result/`);
    cy.url().should('include', '/staff_add_result/');
    cy.contains('Result Upload').should('be.visible');

    // Requires selecting student and subject, and entering scores.
    // Using placeholder IDs.
    const studentId = '1';
    const subjectId = '1';
    const testScore = '85';
    const examScore = '92';

    // Select the student and subject (assuming they exist and dropdowns are populated)
    cy.get('select[name="student_list"]').select(studentId);
    cy.get('select[name="subject"]').select(subjectId);

    cy.get('input[name="test"]').clear().type(testScore);
    cy.get('input[name="exam"]').clear().type(examScore);
    cy.get('form').submit();

    cy.url().should('include', '/staff_add_result/');
    // Depending on whether it's a new entry or update, message varies
    cy.contains(/Scores Saved|Scores Updated/).should('be.visible');

    // Optional: Re-fetch results to verify the save/update
    cy.request('POST', `${BASE_URL}/fetch_student_result/`, {
      student: studentId,
      subject: subjectId
    }).then((response) => {
      expect(response.status).to.eq(200);
      const resultData = JSON.parse(response.body);
      expect(resultData.test).to.eq(testScore);
      expect(resultData.exam).to.eq(examScore);
    });
  });

  it('should successfully fetch student results via AJAX', () => {
    // This requires an existing StudentResult record.
    // Using placeholder IDs.
    const studentId = '1';
    const subjectId = '1';

    cy.request('POST', `${BASE_URL}/fetch_student_result/`, {
      student: studentId,
      subject: subjectId
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.headers['content-type']).to.include('application/json');
      const resultData = JSON.parse(response.body);
      expect(resultData).to.have.property('exam').and.to.be.a('string');
      expect(resultData).to.have.property('test').and.to.be.a('string');
      // Verify content if test data is predictable (e.g., '80', '75')
      // expect(resultData.exam).to.eq('75');
      // expect(resultData.test).to.eq('80');
    });
  });
});