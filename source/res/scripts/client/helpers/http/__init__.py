# Embedded file name: scripts/client/helpers/http/__init__.py
import urllib2
from debug_utils import LOG_WARNING, LOG_ERROR
from helpers import feedparser, time_utils, getFullClientVersion
_CLIENT_VERSION = getFullClientVersion()
_DEFAULT_TIMEOUT = 10.0
_VALID_RESPONSE = 200
_IS_NOT_MODIFIED = 304
_VALID_RESPONSE_CODES = (_VALID_RESPONSE, _IS_NOT_MODIFIED)
_HAS_DATA_RESPONSE_CODES = (_VALID_RESPONSE,)

def parsedate(httpDate):
    return time_utils.getTimestampFromUTC(feedparser._parse_date(httpDate))


def formatdate(timestamp):
    ts = time_utils.getTimeStructInUTC(timestamp)
    short_weekdays = ['Mon',
     'Tue',
     'Wed',
     'Thu',
     'Fri',
     'Sat',
     'Sun']
    months = ['Jan',
     'Feb',
     'Mar',
     'Apr',
     'May',
     'Jun',
     'Jul',
     'Aug',
     'Sep',
     'Oct',
     'Nov',
     'Dec']
    return '%s, %02d %s %04d %02d:%02d:%02d GMT' % (short_weekdays[ts[6]],
     ts[2],
     months[ts[1] - 1],
     ts[0],
     ts[3],
     ts[4],
     ts[5])


class _HttpResponse(object):

    def __init__(self, response):
        self._response = response
        self._data = self._readData(response)

    def isValid(self):
        return self._getCode() in _VALID_RESPONSE_CODES

    def hasData(self):
        return self._getCode() in _HAS_DATA_RESPONSE_CODES

    def getLastModified(self):
        modified = self._getHeader('Last-Modified')
        if modified:
            return parsedate(modified)
        else:
            return None

    def getExpires(self):
        expires = self._getHeader('Expires')
        if expires:
            return parsedate(expires)
        else:
            return None

    def isNotModified(self):
        return self._getCode() == _IS_NOT_MODIFIED

    def getData(self):
        return self._data

    def willClose(self):
        return hasattr(self._response, 'will_close') and self._response.will_close

    def _getHeader(self, header):
        return self._response and self._response.info().getheader(header)

    def _getCode(self):
        return getattr(self._response, 'code', None)

    def _readData(self, response):
        if self.hasData():
            return response.read()
        else:
            self._data = None
            return

    def __repr__(self):
        return 'HttpResponse(code = %s, datalen = %s, modified = %s, expires = %s)' % (self._getCode(),
         len(self._data) if self._data else None,
         self.getLastModified(),
         self.getExpires())


class _HttpConnResponse(_HttpResponse):

    def _getHeader(self, header):
        if self._response:
            return self._response.getheader(header)
        else:
            return None

    def _getCode(self):
        if self._response:
            return self._response.status
        else:
            return None

    def _readData(self, response):
        if response:
            return response.read()
        else:
            return None


def openUrl(url, timeout = _DEFAULT_TIMEOUT, modified = None, agent = _CLIENT_VERSION):
    response = None
    try:
        request = urllib2.Request(url)
        request.add_header('User-Agent', agent)
        if modified:
            request.add_header('If-Modified-Since', formatdate(modified))
            urlOpener = urllib2.build_opener(_NotModifiedHandler())
            response = urlOpener.open(request, timeout=timeout)
        else:
            urlOpener = urllib2.build_opener(urllib2.BaseHandler())
            response = urlOpener.open(request, timeout=timeout)
        return _HttpResponse(response)
    except urllib2.HTTPError as e:
        LOG_WARNING('urllib2.HTTPError', e.code, url)
    except urllib2.URLError as e:
        LOG_WARNING('urllib2.URLError', e.reason, url)
    except Exception as e:
        LOG_ERROR("Client couldn't download file", e, url)
    finally:
        if response:
            response.close()

    return _HttpResponse(response)


def openPage(connection, page, modified = None, agent = _CLIENT_VERSION):
    response = None
    try:
        headers = {'User-Agent': agent,
         'Connection': 'Keep-Alive'}
        if modified:
            headers['If-Modified-Since'] = formatdate(modified)
        connection.request('GET', page, headers=headers)
        response = connection.getresponse()
    except Exception as e:
        LOG_ERROR("Client couldn't download file", e, connection, page)

    return _HttpConnResponse(response)


class _NotModifiedHandler(urllib2.BaseHandler):

    def http_error_304(self, req, fp, code, message, headers):
        addinfourl = urllib2.addinfourl(fp, headers, req.get_full_url())
        addinfourl.code = code
        return addinfourl
