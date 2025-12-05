
// Custom login command for convenience
Cypress.Commands.add('login', (email, password) => {
  cy.visit(`${BASE_URL}/login/`);
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="password"]').type(password);
  cy.get('form').submit();
});

describe('Admin User E2E Tests', () => {
  let uniqueId;
  let createdCourseId;
  let createdStaffId;
  let createdSessionId;
  let createdStudentId;
  let createdSubjectId;

  beforeEach(() => {
    uniqueId = Cypress._.uniqueId('test_');
    cy.login('qasim@admin.com', 'admin');
    cy.url().should('include', '/admin/dashboard/');
  });

  it('should create a new Course', () => {
    cy.visit(`${BASE_URL}/admin/add-course/`);
    cy.get('input[name="name"]').type(`Cypress Course ${uniqueId}`);
    cy.get('form').submit();
    cy.url().should('include', '/admin/manage-course/');
    cy.contains(`Cypress Course ${uniqueId}`).should('exist');
    cy.get('table tbody tr').contains(`Cypress Course ${uniqueId}`).parent().find('a[href*="/edit-course/"]').first().invoke('attr', 'href').then((href) => {
        createdCourseId = href.match(/\/edit-course\/(\d+)/)[1];
    });
  });

  it('should create a new Session', () => {
    const startDate = Cypress.moment().format('YYYY-MM-DD');
    const endDate = Cypress.moment().add(1, 'year').format('YYYY-MM-DD');
    cy.visit(`${BASE_URL}/admin/add-session/`);
    cy.get('input[name="start_year"]').type(startDate);
    cy.get('input[name="end_year"]').type(endDate);
    cy.get('form').submit();
    cy.url().should('include', '/admin/manage-session/');
    cy.contains(startDate).should('exist');
    cy.get('table tbody tr').contains(startDate).parent().find('a[href*="/edit-session/"]').first().invoke('attr', 'href').then((href) => {
        createdSessionId = href.match(/\/edit-session\/(\d+)/)[1];
    });
  });

  it('should create a new Staff member', () => {
    cy.visit(`${BASE_URL}/admin/add-staff/`);
    cy.get('input[name="first_name"]').type(`StaffFn ${uniqueId}`);
    cy.get('input[name="last_name"]').type(`StaffLn ${uniqueId}`);
    cy.get('input[name="email"]').type(`staff_${uniqueId}@example.com`);
    cy.get('select[name="gender"]').select('Male');
    cy.get('input[name="password"]').type('password123');
    cy.get('textarea[name="address"]').type(`123 Staff Street, City ${uniqueId}`);
    cy.fixture('test_image.jpg', 'binary')
      .then(Cypress.Blob.binaryStringToBlob)
      .then(fileContent => {
        cy.get('input[type="file"][name="profile_pic"]').attachFile({
          fileContent,
          fileName: 'test_image.jpg',
          mimeType: 'image/jpeg'
        });
      });
    cy.get('select[name="course"]').select(1); // Select the first available course
    cy.get('form').submit();
    cy.url().should('include', '/admin/manage-staff/');
    cy.contains(`staff_${uniqueId}@example.com`).should('exist');
    cy.get('table tbody tr').contains(`staff_${uniqueId}@example.com`).parent().find('a[href*="/edit-staff/"]').first().invoke('attr', 'href').then((href) => {
        createdStaffId = href.match(/\/edit-staff\/(\d+)/)[1];
    });
  });

  it('should create a new Student member', () => {
    cy.visit(`${BASE_URL}/admin/add-student/`);
    cy.get('input[name="first_name"]').type(`StudentFn ${uniqueId}`);
    cy.get('input[name="last_name"]').type(`StudentLn ${uniqueId}`);
    cy.get('input[name="email"]').type(`student_${uniqueId}@example.com`);
    cy.get('select[name="gender"]').select('Female');
    cy.get('input[name="password"]').type('password123');
    cy.get('textarea[name="address"]').type(`456 Student Avenue, Town ${uniqueId}`);
    cy.fixture('test_image.jpg', 'binary')
      .then(Cypress.Blob.binaryStringToBlob)
      .then(fileContent => {
        cy.get('input[type="file"][name="profile_pic"]').attachFile({
          fileContent,
          fileName: 'test_image.jpg',
          mimeType: 'image/jpeg'
        });
      });
    cy.get('select[name="course"]').select(1); // Select first available course
    cy.get('select[name="session"]').select(1); // Select first available session
    cy.get('form').submit();
    cy.url().should('include', '/admin/manage-student/');
    cy.contains(`student_${uniqueId}@example.com`).should('exist');
    cy.get('table tbody tr').contains(`student_${uniqueId}@example.com`).parent().find('a[href*="/edit-student/"]').first().invoke('attr', 'href').then((href) => {
        createdStudentId = href.match(/\/edit-student\/(\d+)/)[1];
    });
  });

  it('should create a new Subject', () => {
    cy.visit(`${BASE_URL}/admin/add-subject/`);
    cy.get('input[name="name"]').type(`Cypress Subject ${uniqueId}`);
    cy.get('select[name="staff"]').select(1); // Select first available staff
    cy.get('select[name="course"]').select(1); // Select first available course
    cy.get('form').submit();
    cy.url().should('include', '/admin/manage-subject/');
    cy.contains(`Cypress Subject ${uniqueId}`).should('exist');
    cy.get('table tbody tr').contains(`Cypress Subject ${uniqueId}`).parent().find('a[href*="/edit-subject/"]').first().invoke('attr', 'href').then((href) => {
        createdSubjectId = href.match(/\/edit-subject\/(\d+)/)[1];
    });
  });

  it('should add a Student Result', () => {
    cy.visit(`${BASE_URL}/admin/add-student-result/`); // Assuming URL for adding results
    cy.get('select[name="session_year"]').select(1); // Select first available session
    cy.get('select[name="subject"]').select(1); // Select first available subject
    cy.get('select[name="student"]').select(1); // Select first available student
    cy.get('input[name="test"]').type('85');
    cy.get('input[name="exam"]').type('92');
    cy.get('form').submit();
    cy.url().should('include', '/admin/add-student-result/'); // Stays on same page or redirects
    cy.contains('Result Added Successfully').should('exist'); // Assuming a success message
  });

  it('should create a new Admin member (validation for duplicate email)', () => {
    cy.visit(`${BASE_URL}/admin/add-admin/`);
    cy.get('input[name="first_name"]').type(`AdminFn ${uniqueId}`);
    cy.get('input[name="last_name"]').type(`AdminLn ${uniqueId}`);
    cy.get('input[name="email"]').type(`admin_${uniqueId}@example.com`); // Unique email
    cy.get('select[name="gender"]').select('Male');
    cy.get('input[name="password"]').type('password123');
    cy.get('textarea[name="address"]').type(`789 Admin Road, Metropolis ${uniqueId}`);
    cy.fixture('test_image.jpg', 'binary')
      .then(Cypress.Blob.binaryStringToBlob)
      .then(fileContent => {
        cy.get('input[type="file"][name="profile_pic"]').attachFile({
          fileContent,
          fileName: 'test_image.jpg',
          mimeType: 'image/jpeg'
        });
      });
    cy.get('form').submit();
    cy.url().should('include', '/admin/manage-admin/');
    cy.contains(`admin_${uniqueId}@example.com`).should('exist');

    // Test duplicate email
    cy.visit(`${BASE_URL}/admin/add-admin/`);
    cy.get('input[name="first_name"]').type(`AdminFn2 ${uniqueId}`);
    cy.get('input[name="last_name"]').type(`AdminLn2 ${uniqueId}`);
    cy.get('input[name="email"]').type(`admin_${uniqueId}@example.com`); // Duplicate email
    cy.get('select[name="gender"]').select('Female');
    cy.get('input[name="password"]').type('password123');
    cy.get('textarea[name="address"]').type(`101 Admin Lane, Gotham ${uniqueId}`);
    cy.fixture('test_image.jpg', 'binary')
      .then(Cypress.Blob.binaryStringToBlob)
      .then(fileContent => {
        cy.get('input[type="file"][name="profile_pic"]').attachFile({
          fileContent,
          fileName: 'test_image.jpg',
          mimeType: 'image/jpeg'
        });
      });
    cy.get('form').submit();
    cy.contains("The given email is already registered").should('exist');
  });
});

describe('Staff User E2E Tests', () => {
  let uniqueId;

  beforeEach(() => {
    uniqueId = Cypress._.uniqueId('staff_test_');
    cy.login('bill@ms.com', '123');
    cy.url().should('include', '/staff/dashboard/');
  });

  it('should submit a leave request', () => {
    const leaveDate = Cypress.moment().add(7, 'days').format('YYYY-MM-DD');
    cy.visit(`${BASE_URL}/staff/apply-leave/`);
    cy.get('input[name="date"]').type(leaveDate);
    cy.get('textarea[name="message"]').type(`Urgent leave request for ${uniqueId}`);
    cy.get('form').submit();
    cy.url().should('include', '/staff/apply-leave/'); // Assuming no redirect after submit
    cy.contains('Leave request sent successfully').should('exist'); // Assuming success message
  });

  it('should submit feedback', () => {
    cy.visit(`${BASE_URL}/staff/feedback/`);
    cy.get('textarea[name="feedback"]').type(`Feedback from staff ${uniqueId}: Everything is great!`);
    cy.get('form').submit();
    cy.url().should('include', '/staff/feedback/'); // Assuming no redirect after submit
    cy.contains('Feedback sent successfully').should('exist'); // Assuming success message
  });
});

describe('Student User E2E Tests', () => {
  let uniqueId;

  beforeEach(() => {
    uniqueId = Cypress._.uniqueId('student_test_');
    cy.login('qasim@nu.edu.pk', '123');
    cy.url().should('include', '/student/dashboard/');
  });

  it('should submit a leave request', () => {
    const leaveDate = Cypress.moment().add(10, 'days').format('YYYY-MM-DD');
    cy.visit(`${BASE_URL}/student/apply-leave/`);
    cy.get('input[name="date"]').type(leaveDate);
    cy.get('textarea[name="message"]').type(`Requesting leave for personal reasons ${uniqueId}`);
    cy.get('form').submit();
    cy.url().should('include', '/student/apply-leave/'); // Assuming no redirect after submit
    cy.contains('Leave request sent successfully').should('exist'); // Assuming success message
  });

  it('should submit feedback', () => {
    cy.visit(`${BASE_URL}/student/feedback/`);
    cy.get('textarea[name="feedback"]').type(`Student feedback ${uniqueId}: I am learning a lot!`);
    cy.get('form').submit();
    cy.url().should('include', '/student/feedback/'); // Assuming no redirect after submit
    cy.contains('Feedback sent successfully').should('exist'); // Assuming success message
  });