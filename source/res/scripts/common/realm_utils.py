# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/realm_utils.py
import string
import ResMgr as rmgr
from constants import CURRENT_REALM, IS_CLIENT, IS_EDITOR

def getRealmFilePath(filepath):
    parts = filepath.split('.')
    return string.join(parts[:-1] + [CURRENT_REALM] + parts[-1:], '.')


class ResMgr(object):

    class __metaclass__(type):

        def __getattr__(self, item):
            return getattr(rmgr, item) if IS_CLIENT else getattr(self if item in ('openSection', 'purge') else rmgr, item)

    @staticmethod
    def openSection(filepath, createIfMissing=False):
        section = rmgr.openSection(getRealmFilePath(filepath)) if not IS_EDITOR else None
        return section if section is not None else rmgr.openSection(filepath, createIfMissing)

    @staticmethod
    def purge(filepath, recursive=False):
        if not filepath:
            return
        rmgr.purge(filepath, recursive)
        rmgr.purge(getRealmFilePath(filepath), recursive)
