# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/universal_flag/universal_flag_entry_point_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.universal_flag.details.universal_flag_background import UniversalFlagBackground

class VisibilityState(Enum):
    HIDDEN = 'hidden'
    SHOWN = 'shown'
    MAINTENANCE = 'maintenance'


class UniversalFlagEntryPointModel(ViewModel):
    __slots__ = ('openEvent',)

    def __init__(self, properties=3, commands=1):
        super(UniversalFlagEntryPointModel, self).__init__(properties=properties, commands=commands)

    @property
    def background(self):
        return self._getViewModel(0)

    @staticmethod
    def getBackgroundType():
        return UniversalFlagBackground

    def getVisibilityState(self):
        return VisibilityState(self._getString(1))

    def setVisibilityState(self, value):
        self._setString(1, value.value)

    def getPrevState(self):
        return VisibilityState(self._getString(2))

    def setPrevState(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(UniversalFlagEntryPointModel, self)._initialize()
        self._addViewModelProperty('background', UniversalFlagBackground())
        self._addStringProperty('visibilityState')
        self._addStringProperty('prevState')
        self.openEvent = self._addCommand('openEvent')
