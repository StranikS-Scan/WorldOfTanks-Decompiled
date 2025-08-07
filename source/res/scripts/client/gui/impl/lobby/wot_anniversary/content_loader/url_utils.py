# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/content_loader/url_utils.py
import re
PATH_CLEAN_RE = re.compile('^/*(.+?)/*$')

def makePathFromParts(*parts):
    if not parts:
        return ''
    hasLastSlash = parts[-1].endswith('/')
    cleanedParts = []
    for part in parts:
        partMatch = PATH_CLEAN_RE.match(part)
        cleanedParts.append(partMatch.group(1) if partMatch else '')

    result = '/' + '/'.join(cleanedParts)
    if hasLastSlash:
        result += '/'
    return result


def makeUrlFromParts(*parts):
    if not parts:
        return ''
    if parts[0] == 'http://' or parts[0] == 'https://':
        result = makePathFromParts(*parts[1:])
        return ''.join((parts[0], result.lstrip('/')))
    result = makePathFromParts(*parts)
    return result.lstrip('/')
