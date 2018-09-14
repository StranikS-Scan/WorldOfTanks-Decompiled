# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/qualifiers/__init__.py
import os
import ResMgr
from constants import ITEM_DEFS_PATH, KNOWN_QUALIFIER_CONDITION_PARAMS
from itertools import chain
from debug_utils import *
from ._qualifier import QUALIFIER_TYPE, parseQualifier, CREW_ROLE, QUALIFIER_TYPE_NAMES
_XML_FILE = os.path.join(ITEM_DEFS_PATH, 'qualifiers.xml')
g_cache = None

class QualifiersCache(object):

    def __init__(self, qualifiers):
        self.qualifiers = {qualifier.id:qualifier for qualifier in qualifiers}

    @classmethod
    def fromXmlFile(cls, xmlPath):
        root = ResMgr.openSection(xmlPath)
        if root is None:
            raise Exception, 'Wrong xml with item qualifiers={0}'.format(xmlPath)
        res = []
        for name, section in root.items():
            if name != 'qualifier':
                LOG_ERROR('Unexpected tag in qualifiers', name)
                continue
            res.append(parseQualifier(section))

        return cls(res)

    def __getitem__(self, name):
        return self.qualifiers.get(name)


def init():
    global g_cache
    if g_cache is not None:
        return
    else:
        g_cache = QualifiersCache.fromXmlFile(_XML_FILE)
        items = (q.conditionParams for q in g_cache.qualifiers.itervalues())
        allParameters = set(chain(*items))
        diff = allParameters - KNOWN_QUALIFIER_CONDITION_PARAMS
        if diff:
            LOG_WARNING('During parsing {0} found unregistered condition parameters({1})'.format(_XML_FILE, ','.join(diff)))
        return
