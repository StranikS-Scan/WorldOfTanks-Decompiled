# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/multiple_icons_set_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.dialogs.sub_views.icon_view_model import IconViewModel

class IconPositionLogicEnum(Enum):
    BOTTOMALIGNMENT = 'bottomAlignment'
    CENTREDANDTHROUGHCONTENT = 'centredAndThroughContent'
    MOVECONTENTBELOW = 'moveContentBelow'


class MultipleIconsSetViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(MultipleIconsSetViewModel, self).__init__(properties=properties, commands=commands)

    def getBackgrounds(self):
        return self._getArray(0)

    def setBackgrounds(self, value):
        self._setArray(0, value)

    @staticmethod
    def getBackgroundsType():
        return IconViewModel

    def getOverlays(self):
        return self._getArray(1)

    def setOverlays(self, value):
        self._setArray(1, value)

    @staticmethod
    def getOverlaysType():
        return IconViewModel

    def getIcons(self):
        return self._getArray(2)

    def setIcons(self, value):
        self._setArray(2, value)

    @staticmethod
    def getIconsType():
        return IconViewModel

    def getIconPositionLogic(self):
        return self._getString(3)

    def setIconPositionLogic(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(MultipleIconsSetViewModel, self)._initialize()
        self._addArrayProperty('backgrounds', Array())
        self._addArrayProperty('overlays', Array())
        self._addArrayProperty('icons', Array())
        self._addStringProperty('iconPositionLogic', 'centredAndThroughContent')
