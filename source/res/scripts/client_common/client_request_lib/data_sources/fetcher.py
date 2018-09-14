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
    *    Keyword arguments are supported for this function.
    *
    *    @param url    The URL to retrieve.
    *    @param callback    The callable object that receives the response object. The
    *        response object has <i>body</i> and <i>responseCode</i> properties.
    *    @param headers An optional sequence of strings to be added to the request's
    *            HTTP headers.
    *    @param timeout Optional argument for the number of seconds before this call
    *            should time out.
    *    @param method "GET", "PUT", "POST", "PATCH" or "DELETE" to indicate
    *            the HTTP method.
    *    @param postData Optional argument for the data posted along with the
    *            POST/PUT/PATCH request. If it is a Python dict, then this method will
    *            encode the data to MULTIPART/FORM-DATA format. Otherwise, if it is
    *            a Python string, the data will be posted to the HTTP server directly.
    *            In this case, the user of this method needs to make sure that
    *            the data is encoded in the right format(i.e. JSON/XML).
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
