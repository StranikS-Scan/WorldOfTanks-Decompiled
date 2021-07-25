# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/instructor/nation_settings.py
from typing import List, Tuple, TYPE_CHECKING
import ResMgr
from crew2.int_collection import parseIntCollection
from items import _xml
if TYPE_CHECKING:
    from crew2.settings_locator import Crew2Settings

class InstructorNationSettings(object):
    __slots__ = ('_firstNameIDs', '_secondNameIDs', '_portraitIDs')

    def __init__(self):
        self._firstNameIDs = []
        self._secondNameIDs = []
        self._portraitIDs = []

    @property
    def firstNameIDs(self):
        return self._firstNameIDs

    @property
    def secondNameIDs(self):
        return self._secondNameIDs

    @property
    def portraitIDs(self):
        return self._portraitIDs

    def loadFromXml(self, xmlCtx, section, settingsLocator):
        IDsStr = _xml.readStringOrNone(xmlCtx, section, 'characterIDs')
        if IDsStr is not None:
            IDs = parseIntCollection(IDsStr)
            self._firstNameIDs = self._secondNameIDs = self._portraitIDs = IDs
        else:
            firstNameIDsStr = _xml.readString(xmlCtx, section, 'firstNameIDs')
            self._firstNameIDs = parseIntCollection(firstNameIDsStr)
            secondNameIDsStr = _xml.readString(xmlCtx, section, 'secondNameIDs')
            self._secondNameIDs = parseIntCollection(secondNameIDsStr)
            portraitIDsStr = _xml.readString(xmlCtx, section, 'portraitIDs')
            self._portraitIDs = parseIntCollection(portraitIDsStr)
        return
