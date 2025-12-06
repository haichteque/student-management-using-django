const mocha = require('mocha');
const fs = require('fs');
const path = require('path');

const createFolderStructure = (fullPath) => {
  const paths = fullPath.split(path.normalize(path.sep));

  let currentPath = '';

  paths.forEach((part) => {
    currentPath = path.join(currentPath, part);

    if (!fs.existsSync(currentPath)) {
      fs.mkdirSync(currentPath);
    }
  });
};

const removeParent = (tree) => {
  // eslint-disable-next-line no-param-reassign
  delete tree.parent;

  if (tree.children) {
    tree.children.forEach((node) => {
      removeParent(node);
    });
  }
};

const saveFile = (fullPath, fileName, json) => {
  fs.writeFileSync(
    path.join(fullPath, fileName),
    JSON.stringify(json)
  );
};

function JsonReporter(runner) {
  mocha.reporters.Base.call(this, runner);

  const jsonResult = {
    children: [],
    parent: undefined
  };

  let current;
  let testId = 1;
  let suiteId = 1;

  runner.on('suite', (suite) => {
    if (suite.root) {
      jsonResult.description = 'suite execution';
      current = jsonResult;
    } else {
      const node = {
        id: `suite${suiteId}`,
        description: suite.title,
        fullName: suite.fullTitle(),
        failedExpectations: [],
        children: [],
        parent: current
      };

      suiteId += 1;
      current.children.push(node);
      current = node;
    }
  });

  runner.on('suite end', () => {
    current = current.parent;
  });

  runner.on('pass', (test) => {
    const node = {
      id: `spec${testId}`,
      description: test.title,
      fullName: current.fullName ? `${current.fullName} ${test.title}` : test.title,
      passedExpectations: [
        {
          matcherName: test.body,
          message: 'Passed.',
          stack: '',
          passed: true
        }
      ],
      pendingReason: '',
      status: 'passed'
    };

    testId += 1;
    current.children.push(node);
  });

  runner.on('fail', (test, err) => {
    const node = {
      id: `spec${testId}`,
      description: test.title,
      fullName: test.fullTitle(),
      failedExpectations: [
        {
          matcherName: err.name,
          message: err.message,
          stack: err.stack,
          passed: false,
          expected: err.expected,
          actual: err.actual
        }
      ],
      passedExpectations: [],
      pendingReason: '',
      status: 'failed'
    };

    testId += 1;
    current.children.push(node);
  });

  runner.on('test end', (test) => {
    if (test.pending) {
      const node = {
        id: `spec${testId}`,
        description: test.title,
        fullName: test.fullTitle(),
        failedExpectations: [],
        passedExpectations: [],
        pendingReason: '',
        status: 'pending',
        children: []
      };

      testId += 1;
      current.children.push(node);
    }
  });

  runner.on('end', () => {
    removeParent(jsonResult);

    const reportPath = process.env.MOCHAJSONREPORT_PATH ? process.env.MOCHAJSONREPORT_PATH : 'report/json';
    const fileName = process.env.MOCHAJSONREPORT_FILENAME ? process.env.MOCHAJSONREPORT_FILENAME : 'result.json';

    createFolderStructure(reportPath);
    saveFile(reportPath, fileName, jsonResult);
    if (!fs.existsSync(reportPath)) {
      fs.mkdirSync(reportPath);
    }

    const fullFileName = path.join(reportPath, fileName);

    fs.writeFileSync(fullFileName, JSON.stringify(jsonResult));
  });
}

module.exports = JsonReporter;
