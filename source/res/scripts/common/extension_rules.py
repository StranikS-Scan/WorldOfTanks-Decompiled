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
        g_cache['merge_whitelist'] = [ (re.compile(rule['pattern'].asString), rule['type'].asString) for rule in whitelist.values() ]
        ResMgr.purge(EXTENSION_RULES_FILE, True)
        return


def isExtXML(path):
    path = path.replace('\\', '/')
    if g_cache is None:
        return (False, None)
    else:
        for pattern, method in g_cache.get('merge_whitelist', {}):
            if bool(pattern.match(path)):
                return (True, method)

        return (False, None)
