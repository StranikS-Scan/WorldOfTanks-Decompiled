# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/http/url_formatters.py
import urllib
import urlparse

class URL_PARTS_IDS(object):
    """
    represents ids of parts on which url is split by urlparse function
    <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    """
    SCHEME = 0
    NETLOC = 1
    PATH = 2
    PARAMS = 3
    QUERY = 4
    FRAGMENT = 5


def addParamsToUrlQuery(url, params):
    """
    adds given get params to given. Handles cases when url already has some GET params
    """
    urlParts = list(urlparse.urlparse(url))
    query = urlparse.parse_qs(urlParts[URL_PARTS_IDS.QUERY])
    query.update(params)
    urlParts[URL_PARTS_IDS.QUERY] = urllib.urlencode(query, True)
    return urlparse.urlunparse(urlParts)


def separateQuery(url):
    """
    splits given url on 2 parts - main url and GET parameters part
    example: separateQuery('http://a.bc.com/?test=2') = 'http://a.bc.com/', '?test=2'
    """
    urlParts = list(urlparse.urlparse(url))
    mainUrlParts = urlParts[:URL_PARTS_IDS.QUERY] + ['', '']
    queryParts = [''] * 4 + urlParts[URL_PARTS_IDS.QUERY:]
    return (urlparse.urlunparse(mainUrlParts), urlparse.urlunparse(queryParts))
