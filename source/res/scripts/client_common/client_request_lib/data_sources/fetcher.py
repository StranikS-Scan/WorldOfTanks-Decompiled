# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/client_request_lib/data_sources/fetcher.py


class FakeResponse(object):

    def __init__(self, r):
        """
                Create wrapper for response object
        """
        self.responseCode = r.status_code
        self.body = r.raw.read()
        self._headers = r.headers

    def headers(self):
        return self._headers

    def __repr__(self):
        return '[HTTP status: {}] {}'.format(self.responseCode, self.body)


def fetchURL(url, callback, headers={}, timeout=30, method='GET', postData=''):
    """
            Simple synchronous implementation via requests library
            see http://docs.python-requests.org/en/latest/
    """
    import requests
    data = postData
    if isinstance(headers, (list, tuple)):
        res = {}
        for header in headers:
            a, b = header.split(':')
            res[a] = b

        headers = res
    if not isinstance(data, str) and data is not None:
        raise Exception('Unsupported parameter {}'.format(data))
    methods = {'GET': requests.get,
     'PUT': requests.put,
     'POST': requests.post,
     'PATCH': requests.patch,
     'DELETE': requests.delete}
    if method in methods:
        response = methods[method](url, headers=headers, data=data, verify=False, stream=True)
    else:
        raise Exception('Unsupported method {}'.format(method))
    callback(FakeResponse(response))
    return
