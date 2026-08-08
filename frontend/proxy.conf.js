module.exports = {
  "/auth": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/employees": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/department": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/projects": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/issues": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/comments": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/attachments": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/dashboard": {
    "target": "http://localhost:8000",
    "secure": false,
    "bypass": function (req) {
      if (req.headers.accept && req.headers.accept.indexOf('html') !== -1) {
        return '/index.html';
      }
    }
  },
  "/uploads": {
    "target": "http://localhost:8000",
    "secure": false
  }
};
