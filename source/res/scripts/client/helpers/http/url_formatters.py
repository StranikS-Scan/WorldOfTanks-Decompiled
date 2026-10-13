# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/http/url_formatters.py
from __future__ import absolute_import
import typing
from future.moves.urllib import parse

class URL_PARTS_IDS(object):
    SCHEME = 0
    NETLOC = 1
    PATH = 2
    PARAMS = 3
    QUERY = 4
    FRAGMENT = 5


def addParamsToUrlQuery(url, params, keepBlankValues=False):
    urlParts = list(parse.urlparse(url))
    query = parse.parse_qs(urlParts[URL_PARTS_IDS.QUERY], keep_blank_values=keepBlankValues)
    query.update(params)
    urlParts[URL_PARTS_IDS.QUERY] = parse.urlencode(query, True)
    return parse.urlunparse(urlParts)


def separateQuery(url):
    urlParts = list(parse.urlparse(url))
    mainUrlParts = urlParts[:URL_PARTS_IDS.QUERY] + ['', '']
    queryParts = [''] * 4 + urlParts[URL_PARTS_IDS.QUERY:]
    return (parse.urlunparse(mainUrlParts), parse.urlunparse(queryParts))
