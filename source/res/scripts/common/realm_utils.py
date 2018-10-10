# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/realm_utils.py
import BigWorld
import string
import ResMgr as rmgr
from constants import CURRENT_REALM, IS_CLIENT

class ResMgr(object):

    class __metaclass__(type):

        def __getattr__(self, item):
            return getattr(rmgr, item) if IS_CLIENT else getattr(self if item in ('openSection', 'purge') else rmgr, item)

    @staticmethod
    def openSection(filepath, createIfMissing=False):
        realm = CURRENT_REALM
        parts = filepath.split('.')
        section = rmgr.openSection(string.join(parts[:-1] + [realm] + parts[-1:], '.')) if BigWorld.component != 'editor' else None
        return section if section is not None else rmgr.openSection(filepath, createIfMissing)

    @staticmethod
    def purge(filepath, recursive=False):
        if not filepath:
            return
        parts = filepath.split('.')
        rmgr.purge(filepath, recursive)
        rmgr.purge(string.join(parts[:-1] + [CURRENT_REALM] + parts[-1:], '.'), recursive)
