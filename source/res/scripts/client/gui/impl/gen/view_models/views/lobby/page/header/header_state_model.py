# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/header_state_model.py
from enum import Enum
from frameworks.wulf import Map, ViewModel
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel

class HeaderType(Enum):
    HANGAR = 'hangar'
    DEFAULT = 'default'


class HeaderStateModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(HeaderStateModel, self).__init__(properties=properties, commands=commands)

    @property
    def router(self):
        return self._getViewModel(0)

    @staticmethod
    def getRouterType():
        return RouterModel

    def getFeatures(self):
        return self._getMap(1)

    def setFeatures(self, value):
        self._setMap(1, value)

    @staticmethod
    def getFeaturesType():
        return (unicode, bool)

    def getType(self):
        return HeaderType(self._getString(2))

    def setType(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(HeaderStateModel, self)._initialize()
        self._addViewModelProperty('router', RouterModel())
        self._addMapProperty('features', Map(unicode, bool))
        self._addStringProperty('type', HeaderType.DEFAULT.value)
