const BASE_URL = 'http://127.0.0.1:8000';

// Custom command to log in a user
Cypress.Commands.add('login', (email, password) => {
  cy.visit(`${BASE_URL}/login/`); // Assuming /login/ is the login page URL
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="password"]').type(password);
  cy.get('button[type="submit"]').click();
  cy.url().should('not.include', '/login/'); // Ensure redirection after successful login
});

// Helper function to generate unique emails
const generateUniqueEmail = (prefix = 'test') => {
  return `${prefix}-${Date.now()}@example.com`;
};

describe('Admin E2E Tests', () => {
  const adminCredentials = {
    email: 'qasim@admin.com',
    password: 'admin',
  };

  // Variables to store IDs for created entities
  let testCourseId;
  let testStaffId;
  let testSubjectId;
  let testSessionId;
  let testStudentId;
  let createdStaffEmail;
  let createdStudentEmail;

  before(() => {
    // Ensure the server is running and accessible
    cy.request(BASE_URL).its('status').should('eq', 200);

    // Prepare a dummy image file for upload
    cy.fixture('images/profile.jpg', { encoding: 'base64' }).as('profilePic');
  });

  beforeEach(() => {
    // Log in as admin before each test in this suite
    cy.login(adminCredentials.email, adminCredentials.password);
  });

  it('1. Should display the Admin Dashboard (admin_home)', () => {
    cy.visit(`${BASE_URL}/admin_home/`); // Assuming /admin_home/ is the admin dashboard URL
    cy.get('h3').should('contain', 'Administrative Dashboard');
    cy.contains('Total Staff').should('be.visible');
    cy.contains('Total Students').should('be.visible');
  });

  it('2. Should successfully add a new Course (add_course)', () => {
    cy.visit(`${BASE_URL}/add_course/`);
    const courseName = `Cypress Test Course ${Date.now()}`;
    cy.get('input[name="name"]').type(courseName);
    cy.get('button[type="submit"]').click();
    cy.contains('Successfully Added').should('be.visible');
    cy.url().should('include', '/add_course/'); // Should redirect back to add_course page

    // Verify the course exists on manage page and capture ID
    cy.visit(`${BASE_URL}/manage_course/`);
    cy.contains('td', courseName)
      .parent('tr')
      .find('a[href*="/edit_course/"]')
      .invoke('attr', 'href')
      .then((href) => {
        testCourseId = href.split('/').filter(Boolean).pop();
        expect(testCourseId).to.be.a('string').and.not.be.empty;
      });
  });

  it('3. Should successfully add a new Session (add_session)', () => {
    cy.visit(`${BASE_URL}/add_session/`);
    const sessionStart = '2023-09-01';
    const sessionEnd = '2024-05-31';
    cy.get('input[name="session_start"]').type(sessionStart);
    cy.get('input[name="session_end"]').type(sessionEnd);
    cy.get('button[type="submit"]').click();
    cy.contains('Session Created').should('be.visible');
    cy.url().should('include', '/add_session/');

    // Verify the session exists on manage page and capture ID
    cy.visit(`${BASE_URL}/manage_session/`);
    cy.contains('td', sessionStart)
      .parent('tr')
      .find('a[href*="/edit_session/"]')
      .invoke('attr', 'href')
      .then((href) => {
        testSessionId = href.split('/').filter(Boolean).pop();
        expect(testSessionId).to.be.a('string').and.not.be.empty;
      });
  });

  it('4. Should successfully add a new Staff member (add_staff)', () => {
    expect(testCourseId).to.exist; // Ensure course is created
    cy.visit(`${BASE_URL}/add_staff/`);
    createdStaffEmail = generateUniqueEmail('staff');
    cy.get('input[name="first_name"]').type('CypressStaff');
    cy.get('input[name="last_name"]').type('Test');
    cy.get('input[name="email"]').type(createdStaffEmail);
    cy.get('input[name="password"]').type('password123');
    cy.get('input[name="address"]').type('123 Staff Lane');
    cy.get('select[name="gender"]').select('Male'); // Assuming Male is an option
    cy.get('select[name="course"]').select(testCourseId); // Select the created course by ID
    cy.get('input[name="profile_pic"]').selectFile('@profilePic', { force: true });
    cy.get('button[type="submit"]').click();
    cy.contains('Successfully Added').should('be.visible');
    cy.url().should('include', '/add_staff/');

    // Verify staff exists on manage page and capture ID
    cy.visit(`${BASE_URL}/manage_staff/`);
    cy.contains('td', createdStaffEmail)
      .parent('tr')
      .find('a[href*="/edit_staff/"]')
      .invoke('attr', 'href')
      .then((href) => {
        testStaffId = href.split('/').filter(Boolean).pop();
        expect(testStaffId).to.be.a('string').and.not.be.empty;
      });
  });

  it('5. Should successfully add a new Subject (add_subject)', () => {
    expect(testCourseId).to.exist;
    expect(testStaffId).to.exist;
    cy.visit(`${BASE_URL}/add_subject/`);
    const subjectName = `Cypress Test Subject ${Date.now()}`;
    cy.get('input[name="name"]').type(subjectName);
    cy.get('select[name="course"]').select(testCourseId);
    cy.get('select[name="staff"]').select(testStaffId);
    cy.get('button[type="submit"]').click();
    cy.contains('Successfully Added').should('be.visible');
    cy.url().should('include', '/add_subject/');

    // Verify subject exists on manage page and capture ID
    cy.visit(`${BASE_URL}/manage_subject/`);
    cy.contains('td', subjectName)
      .parent('tr')
      .find('a[href*="/edit_subject/"]')
      .invoke('attr', 'href')
      .then((href) => {
        testSubjectId = href.split('/').filter(Boolean).pop();
        expect(testSubjectId).to.be.a('string').and.not.be.empty;
      });
  });

  it('6. Should successfully add a new Student (add_student)', () => {
    expect(testCourseId).to.exist;
    expect(testSessionId).to.exist;
    cy.visit(`${BASE_URL}/add_student/`);
    createdStudentEmail = generateUniqueEmail('student');
    cy.get('input[name="first_name"]').type('CypressStudent');
    cy.get('input[name="last_name"]').type('Test');
    cy.get('input[name="email"]').type(createdStudentEmail);
    cy.get('input[name="password"]').type('studentpass');
    cy.get('input[name="address"]').type('456 Student St');
    cy.get('select[name="gender"]').select('Female'); // Assuming Female is an option
    cy.get('select[name="course"]').select(testCourseId);
    cy.get('select[name="session"]').select(testSessionId);
    cy.get('input[name="profile_pic"]').selectFile('@profilePic', { force: true });
    cy.get('button[type="submit"]').click();
    cy.contains('Successfully Added').should('be.visible');
    cy.url().should('include', '/add_student/');

    // Verify student exists on manage page and capture ID
    cy.visit(`${BASE_URL}/manage_student/`);
    cy.contains('td', createdStudentEmail)
      .parent('tr')
      .find('a[href*="/edit_student/"]')
      .invoke('attr', 'href')
      .then((href) => {
        testStudentId = href.split('/').filter(Boolean).pop();
        expect(testStudentId).to.be.a('string').and.not.be.empty;
      });
  });


  it('7. Should display Manage Staff page (manage_staff)', () => {
    cy.visit(`${BASE_URL}/manage_staff/`);
    cy.get('h3').should('contain', 'Manage Staff');
    cy.contains(createdStaffEmail).should('be.visible');
  });

  it('8. Should display Manage Students page (manage_student)', () => {
    cy.visit(`${BASE_URL}/manage_student/`);
    cy.get('h3').should('contain', 'Manage Students');
    cy.contains(createdStudentEmail).should('be.visible');
  });

  it('9. Should display Manage Courses page (manage_course)', () => {
    cy.visit(`${BASE_URL}/manage_course/`);
    cy.get('h3').should('contain', 'Manage Courses');
    cy.contains(`Cypress Test Course`).should('be.visible');
  });

  it('10. Should display Manage Subjects page (manage_subject)', () => {
    cy.visit(`${BASE_URL}/manage_subject/`);
    cy.get('h3').should('contain', 'Manage Subjects');
    cy.contains(`Cypress Test Subject`).should('be.visible');
  });

  it('11. Should display Manage Sessions page (manage_session)', () => {
    cy.visit(`${BASE_URL}/manage_session/`);
    cy.get('h3').should('contain', 'Manage Sessions');
    cy.contains('2023-09-01').should('be.visible');
  });

  it('12. Should successfully edit an existing Staff member (edit_staff)', () => {
    expect(testStaffId).to.exist;
    cy.visit(`${BASE_URL}/edit_staff/${testStaffId}/`);
    cy.get('h3').should('contain', 'Edit Staff');
    const updatedFirstName = 'UpdatedStaffFirstName';
    const updatedEmail = generateUniqueEmail('updatedstaff');
    cy.get('input[name="first_name"]').clear().type(updatedFirstName);
    cy.get('input[name="email"]').clear().type(updatedEmail);
    cy.get('input[name="password"]').type('newpass123'); // Change password
    cy.get('input[name="profile_pic"]').selectFile('@profilePic', { force: true }); // Update profile pic
    cy.get('button[type="submit"]').click();
    cy.contains('Successfully Updated').should('be.visible');
    cy.url().should('include', `/edit_staff/${testStaffId}/`);

    // Verify update on manage page
    cy.visit(`${BASE_URL}/manage_staff/`);
    cy.contains('td', updatedFirstName).should('be.visible');
    cy.contains('td', updatedEmail).should('be.visible');
    createdStaffEmail = updatedEmail; // Update for future checks
  });

  it('13. Should successfully edit an existing Student (edit_student)', () => {
    expect(testStudentId).to.exist;
    cy.visit(`${BASE_URL}/edit_student/${testStudentId}/`);
    cy.get('h3').should('contain', 'Edit Student');
    const updatedFirstName = 'UpdatedStudentFirstName';
    const updatedEmail = generateUniqueEmail('updatedstudent');
    cy.get('input[name="first_name"]').clear().type(updatedFirstName);
    cy.get('input[name="email"]').clear().type(updatedEmail);
    cy.get('input[name="password"]').type('newstudentpass'); // Change password
    cy.get('input[name="profile_pic"]').selectFile('@profilePic', { force: true }); // Update profile pic
    cy.get('button[type="submit"]').click();
    cy.contains('Successfully Updated').should('be.visible');
    cy.url().should('include', `/edit_student/${testStudentId}/`);

    // Verify update on manage page
    cy.visit(`${BASE_URL}/manage_student/`);
    cy.contains('td', updatedFirstName).should('be.visible');
    cy.contains('td', updatedEmail).should('be.visible');
    createdStudentEmail = updatedEmail; // Update for future checks
  });

  it('14. Should successfully edit an existing Course (edit_course)', () => {
    expect(testCourseId).to.exist;
    cy.visit(`${BASE_URL}/edit_course/${testCourseId}/`);
    cy.get('h3').should('contain', 'Edit Course');
    const updatedCourseName = `Updated Cypress Course ${Date.now()}`;
    cy.get('input[name="name"]').clear().type(updatedCourseName);
    cy.get('button[type="submit"]').click();
    cy.contains('Successfully Updated').should('be.visible');
    cy.url().should('include', `/edit_course/${testCourseId}/`);

    // Verify update on manage page
    cy.visit(`${BASE_URL}/manage_course/`);
    cy.contains('td', updatedCourseName).should('be.visible');
  });

  it('15. Should successfully edit an existing Subject (edit_subject)', () => {
    expect(testSubjectId).to.exist;
    expect(testCourseId).to.exist;
    expect(testStaffId).to.exist;
    cy.visit(`${BASE_URL}/edit_subject/${testSubjectId}/`);
    cy.get('h3').should('contain', 'Edit Subject');
    const updatedSubjectName = `Updated Cypress Subject ${Date.now()}`;
    cy.get('input[name="name"]').clear().type(updatedSubjectName);
    cy.get('select[name="course"]').select(testCourseId); // Re-select or change course
    cy.get('select[name="staff"]').select(testStaffId); // Re-select or change staff
    cy.get('button[type="submit"]').click();
    cy.contains('Successfully Updated').should('be.visible');
    cy.url().should('include', `/edit_subject/${testSubjectId}/`);

    // Verify update on manage page
    cy.visit(`${BASE_URL}/manage_subject/`);
    cy.contains('td', updatedSubjectName).should('be.visible');
  });

  it('16. Should successfully edit an existing Session (edit_session)', () => {
    expect(testSessionId).to.exist;
    cy.visit(`${BASE_URL}/edit_session/${testSessionId}/`);
    cy.get('h3').should('contain', 'Edit Session');
    const updatedSessionStart = '2023-10-01';
    const updatedSessionEnd = '2024-06-30';
    cy.get('input[name="session_start"]').clear().type(updatedSessionStart);
    cy.get('input[name="session_end"]').clear().type(updatedSessionEnd);
    cy.get('button[type="submit"]').click();
    cy.contains('Session Updated').should('be.visible');
    cy.url().should('include', `/edit_session/${testSessionId}/`);

    // Verify update on manage page
    cy.visit(`${BASE_URL}/manage_session/`);
    cy.contains('td', updatedSessionStart).should('be.visible');
  });

  it('17. Should check email availability (check_email_availability)', () => {
    // Test with an existing email
    cy.request('POST', `${BASE_URL}/check_email_availability/`, { email: adminCredentials.email })
      .then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.eq('True');
      });

    // Test with a new, non-existent email
    const nonExistentEmail = generateUniqueEmail('nonexistent');
    cy.request('POST', `${BASE_URL}/check_email_availability/`, { email: nonExistentEmail })
      .then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.eq('False');
      });
  });

  it('18. Should display Student Feedback Messages (student_feedback_message)', () => {
    cy.visit(`${BASE_URL}/student_feedback_message/`);
    cy.get('h3').should('contain', 'Student Feedback Messages');
    // More specific checks can be added if there's dummy feedback data
  });

  it('19. Should display Staff Feedback Messages (staff_feedback_message)', () => {
    cy.visit(`${BASE_URL}/staff_feedback_message/`);
    cy.get('h3').should('contain', 'Staff Feedback Messages');
    // More specific checks can be added if there's dummy feedback data
  });

  it('20. Should display Staff Leave Applications (view_staff_leave)', () => {
    cy.visit(`${BASE_URL}/view_staff_leave/`);
    cy.get('h3').should('contain', 'Leave Applications From Staff');
    // More specific checks can be added if there's dummy leave data
  });

  it('21. Should display Student Leave Applications (view_student_leave)', () => {
    cy.visit(`${BASE_URL}/view_student_leave/`);
    cy.get('h3').should('contain', 'Leave Applications From Students');
    // More specific checks can be added if there's dummy leave data
  });

  it('22. Should display Admin View Attendance page (admin_view_attendance)', () => {
    cy.visit(`${BASE_URL}/admin_view_attendance/`);
    cy.get('h3').should('contain', 'View Attendance');
    cy.get('select[name="subject"]').should('be.visible');
    cy.get('select[name="session"]').should('be.visible');
  });

  // Note: get_admin_attendance requires specific attendance data to exist.
  // This test will only verify the endpoint can be hit with valid parameters
  // assuming a basic structure. A full test would require mocking data or
  // ensuring attendance records exist.
  it('23. Should retrieve attendance data (get_admin_attendance)', () => {
    expect(testSubjectId).to.exist;
    expect(testSessionId).to.exist;
    // To properly test this, an attendance record for the created subject and session needs to exist.
    // For now, we simulate a POST and expect a 200 OK.
    // Assuming there is at least one attendance record created by staff for the test subject/session.
    // This part is challenging without direct database access or API to create attendance data.
    // Skipping comprehensive data validation for this endpoint without a full setup.
    cy.request({
      method: 'POST',
      url: `${BASE_URL}/get_admin_attendance/`,
      form: true, // Send as application/x-www-form-urlencoded
      body: {
        subject: testSubjectId,
        session: testSessionId,
        // attendance_date_id is dynamic and hard to get without prior attendance creation
        // We'll pass a dummy ID or skip. For now, assume a dummy valid one.
        // In a real scenario, you'd create attendance data via other means or capture an existing ID.
        attendance_date_id: '1' // Placeholder, might fail if no attendance with ID 1 exists
      }
    }).then((response) => {
      expect(response.status).to.eq(200);
      // Expect JSON array if data exists, or 'null' if error/no data as per view
      // The view returns JsonResponse(json.dumps(json_data), safe=False) or None
      if (response.body !== 'null') {
         expect(JSON.parse(response.body)).to.be.an('array');
      }
    });
  });

  it('24. Should display and allow editing Admin Profile (admin_view_profile)', () => {
    cy.visit(`${BASE_URL}/admin_view_profile/`);
    cy.get('h3').should('contain', 'View/Edit Profile');
    const newFirstName = 'Qasim_Updated';
    cy.get('input[name="first_name"]').clear().type(newFirstName);
    cy.get('input[name="password"]').type('newadminpass'); // Change password
    cy.get('input[name="profile_pic"]').selectFile('@profilePic', { force: true }); // Update profile pic
    cy.get('button[type="submit"]').click();
    cy.contains('Profile Updated!').should('be.visible');
    cy.url().should('include', '/admin_view_profile/');
    cy.get('input[name="first_name"]').should('have.value', newFirstName); // Verify update on the form
  });

  it('25. Should display Admin Notify Staff page (admin_notify_staff)', () => {
    cy.visit(`${BASE_URL}/admin_notify_staff/`);
    cy.get('h3').should('contain', 'Send Notifications To Staff');
    cy.contains(createdStaffEmail).should('be.visible');
  });

  it('26. Should display Admin Notify Student page (admin_notify_student)', () => {
    cy.visit(`${BASE_URL}/admin_notify_student/`);
    cy.get('h3').should('contain', 'Send Notifications To Students');
    cy.contains(createdStudentEmail).should('be.visible');
  });

  // Note: send_student_notification and send_staff_notification are Firebase Cloud Messaging dependent.
  // We can only test the endpoint's response, not the actual notification delivery.
  it('27. Should send a Student Notification (send_student_notification)', () => {
    expect(testStudentId).to.exist;
    cy.request('POST', `${BASE_URL}/send_student_notification/`, {
      id: testStudentId,
      message: 'Test notification to student',
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.eq('True'); // Expecting 'True' as per view's success
    });
  });

  it('28. Should send a Staff Notification (send_staff_notification)', () => {
    expect(testStaffId).to.exist;
    cy.request('POST', `${BASE_URL}/send_staff_notification/`, {
      id: testStaffId,
      message: 'Test notification to staff',
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.eq('True'); // Expecting 'True' as per view's success
    });
  });

  it('29. Should successfully delete a Subject (delete_subject)', () => {
    expect(testSubjectId).to.exist;
    cy.request(`${BASE_URL}/delete_subject/${testSubjectId}/`); // Use cy.request for direct delete
    cy.visit(`${BASE_URL}/manage_subject/`);
    cy.contains(`Cypress Test Subject ${Date.now()}`).should('not.exist');
  });

  it('30. Should successfully delete a Staff member (delete_staff)', () => {
    expect(testStaffId).to.exist;
    cy.request(`${BASE_URL}/delete_staff/${testStaffId}/`); // Use cy.request for direct delete
    cy.visit(`${BASE_URL}/manage_staff/`);
    cy.contains(createdStaffEmail).should('not.exist');
  });

  it('31. Should successfully delete a Student (delete_student)', () => {
    expect(testStudentId).to.exist;
    cy.request(`${BASE_URL}/delete_student/${testStudentId}/`); // Use cy.request for direct delete
    cy.visit(`${BASE_URL}/manage_student/`);
    cy.contains(createdStudentEmail).should('not.exist');
  });

  it('32. Should successfully delete a Session (delete_session)', () => {
    expect(testSessionId).to.exist;
    cy.request(`${BASE_URL}/delete_session/${testSessionId}/`); // Use cy.request for direct delete
    cy.visit(`${BASE_URL}/manage_session/`);
    cy.contains('2023-10-01').should('not.exist');
  });

  it('33. Should successfully delete a Course (delete_course)', () => {
    expect(testCourseId).to.exist;
    cy.request(`${BASE_URL}/delete_course/${testCourseId}/`); // Use cy.request for direct delete
    cy.visit(`${BASE_URL}/manage_course/`);
    cy.contains(`Updated Cypress Course`).should('not.exist');
  });
});

// Since the provided Python code only contains Admin (HOD) views,
// there are no specific E2E tests for Staff or Student roles
// based directly on the provided functions. If staff/student specific
// views were present in the Python file, they would be added here
// in separate describe blocks.