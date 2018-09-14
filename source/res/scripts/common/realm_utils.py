# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/realm_utils.py
import BigWorld
import string
import ResMgr as rmgr
from constants import CURRENT_REALM

class ResMgr(object):
    """
    A replacement of traditional ResMgr to support knowledge of current realm
    without modification of ResMgr code.
    Class alters openSection and purge methods as follows:
     2 phase open section: open region specific version first if exist, then loads default file;
     two purge attempts: first file supplied then regional file
    Regional version of the file must reside at the same path and having *.realm.xml instead of just
    *.xml
    """

    class __metaclass__(type):

        def __getattr__(self, item):
            return getattr(self if item in ('openSection', 'purge') else rmgr, item)

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
