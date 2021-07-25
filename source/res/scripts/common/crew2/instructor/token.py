# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/instructor/token.py
import typing
from items import _xml, nations
if typing.TYPE_CHECKING:
    import ResMgr

class Token(object):
    __slots__ = ('_name', '_nameFromNationID', '_portrait')

    def __init__(self, xmlCtx, section):
        self._name = _xml.readString(xmlCtx, section, 'name')
        nameFromNation = _xml.readStringOrNone(xmlCtx, section, 'nameFromNation')
        if nameFromNation is not None and nameFromNation not in nations.NAMES:
            _xml.raiseWrongXml(xmlCtx, '', "Unknown nation '{}' in <nameFromNation>".format(nameFromNation))
        self._nameFromNationID = nations.INDICES.get(nameFromNation)
        self._portrait = _xml.readString(xmlCtx, section, 'portrait')
        return

    @property
    def name(self):
        return self._name

    @property
    def nameFromNationID(self):
        return self._nameFromNationID

    @property
    def portrait(self):
        return self._portrait
