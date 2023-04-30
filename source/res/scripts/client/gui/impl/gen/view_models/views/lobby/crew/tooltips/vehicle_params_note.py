# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/vehicle_params_note.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NoteThemeEnum(Enum):
    WARNING = 'warning'
    TEXTONLY = 'textOnly'
    CONTENT = 'content'
    AUTORELOADTIME = 'autoReloadTime'


class VehicleParamsNote(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(VehicleParamsNote, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getTheme(self):
        return NoteThemeEnum(self._getString(2))

    def setTheme(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(VehicleParamsNote, self)._initialize()
        self._addStringProperty('title', '')
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('theme')
