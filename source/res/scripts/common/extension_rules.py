# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/extension_rules.py
import re
import ResMgr
from soft_exception import SoftException
EXTENSION_RULES_FILE = 'scripts/extension_rules.xml'
g_cache = None

class READ_METHOD(object):
    MERGE = 'merge'
    INCLUDE = 'include'
    INCLUDE_BY_PATH = 'includeByPath'


def prepareRuleParams(params):
    if params:
        params = params.replace('\r\n', ' ')
        params = params.replace('\n', ' ')
    return params


def init():
    global g_cache
    if g_cache is not None:
        return
    else:
        g_cache = {}
        sec = ResMgr.openSection(EXTENSION_RULES_FILE)
        if not sec:
            raise SoftException("Fail to read '%s'" % EXTENSION_RULES_FILE)
        whitelist = sec['xml_whitelist']

        def getParams(rule):
            params = None if rule['params'] is None else rule['params'].asString
            return prepareRuleParams(params)

        g_cache['merge_whitelist'] = [ (re.compile(rule['pattern'].asString), rule['type'].asString, getParams(rule)) for rule in whitelist.values() ]
        ResMgr.purge(EXTENSION_RULES_FILE, True)
        return


def isExtXML(path):
    path = path.replace('\\', '/')
    if g_cache is None:
        return (False, None, None)
    else:
        for pattern, method, params in g_cache.get('merge_whitelist', {}):
            if bool(pattern.match(path)):
                return (True, method, params)

        return (False, None, None)
