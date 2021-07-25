# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/detachment/commander_preset.py
import typing
import ResMgr
from crew2.settings_locator import Crew2Settings
from items import _xml

class CommanderPreset(object):
    __slots__ = ('_matrixID', '_firstNameID', '_secondNameID', '_portraitID', '_isFemale')

    def __init__(self, xmlCtx, section, settingsLocator):
        self._firstNameID = None
        self._secondNameID = None
        self._portraitID = None
        self._isFemale = None
        self.__load(xmlCtx, section)
        return

    @property
    def firstNameID(self):
        return self._firstNameID

    @property
    def secondNameID(self):
        return self._secondNameID

    @property
    def portraitID(self):
        return self._portraitID

    @property
    def isFemale(self):
        return self._isFemale

    def __load(self, xmlCtx, section):
        IDs = _xml.readIntOrNone(xmlCtx, section, 'characterIDs')
        if IDs is not None:
            self._firstNameID = self._secondNameID = self._portraitID = IDs
        else:
            self._firstNameID = _xml.readIntOrNone(xmlCtx, section, 'firstNameID')
            self._secondNameID = _xml.readIntOrNone(xmlCtx, section, 'secondNameID')
            self._portraitID = _xml.readIntOrNone(xmlCtx, section, 'portraitID')
        self._isFemale = _xml.readBoolOrNone(xmlCtx, section, 'isFemale')
        return
