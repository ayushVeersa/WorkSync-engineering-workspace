const bypassSpaRoute = function (req) {
  if (
    req.method === 'GET' &&
    req.headers.accept &&
    req.headers.accept.includes('text/html') &&
    req.headers['sec-fetch-mode'] === 'navigate'
  ) {
    return '/index.html';
  }
};

module.exports = {
  "/auth": {
    "target": "http://localhost:8000",
    "secure": false,
    "bypass": bypassSpaRoute
  },
  "/employees": {
    "target": "http://localhost:8000",
    "secure": false,
    "bypass": bypassSpaRoute
  },
  "/department": {
    "target": "http://localhost:8000",
    "secure": false
  },
  "/projects": {
    "target": "http://localhost:8000",
    "secure": false,
    "bypass": bypassSpaRoute
  },
  "/issues": {
    "target": "http://localhost:8000",
    "secure": false,
    "bypass": bypassSpaRoute
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
    "bypass": bypassSpaRoute
  },
  "/reports": {
    "target": "http://localhost:8000",
    "secure": false,
    "bypass": bypassSpaRoute
  },
  "/activity": {
    "target": "http://localhost:8000",
    "secure": false,
    "bypass": bypassSpaRoute
  },
  "/integrations": {
    "target": "http://localhost:8000",
    "secure": false,
    "bypass": bypassSpaRoute
  },
  "/tasks": {
    "target": "http://localhost:8000",
    "secure": false,
    "bypass": bypassSpaRoute
  },
  "/me": {
    "target": "http://localhost:8000",
    "secure": false,
    "bypass": bypassSpaRoute
  },
  "/github": {
    "target": "http://localhost:8000",
    "secure": false,
    "bypass": bypassSpaRoute
  },
  "/uploads": {
    "target": "http://localhost:8000",
    "secure": false
  }
};
