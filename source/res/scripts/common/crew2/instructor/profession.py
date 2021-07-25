# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/instructor/profession.py
import typing
import ResMgr
from crew2.instructor.common import loadPerksIDsList
from items import _xml

class InstructorProfession(object):
    __slots__ = ('_id', '_uiName', '_uiDescription', '_perksIDs')

    def __init__(self, xmlCtx, section):
        self._id = _xml.readPositiveInt(xmlCtx, section, 'id')
        self._uiName = _xml.readString(xmlCtx, section, 'uiName')
        self._uiDescription = _xml.readString(xmlCtx, section, 'uiDescription')
        self._perksIDs = loadPerksIDsList(xmlCtx, section, self._id)

    @property
    def id(self):
        return self._id

    @property
    def uiName(self):
        return self._uiName

    @property
    def uiDescription(self):
        return self._uiDescription

    @property
    def perksIDs(self):
        return self._perksIDs

    def isPerksMatchToProfession(self, perksIDs):
        return all((perkID in self._perksIDs for perkID in perksIDs))
