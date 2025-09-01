# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/widget/pm3_banner_tooltip_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class BannerTypeEnum(Enum):
    PM3ENTRYPOINTTEASER = 'PM3EntryPointTeaser'
    PM3ENTRYPOINTOPERATION1 = 'PM3EntryPointOperation1'
    PM3ENTRYPOINTOPERATION2 = 'PM3EntryPointOperation2'
    PM3ENTRYPOINTOPERATION3 = 'PM3EntryPointOperation3'


class Pm3BannerTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(Pm3BannerTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return BannerTypeEnum(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(Pm3BannerTooltipViewModel, self)._initialize()
        self._addStringProperty('type', BannerTypeEnum.PM3ENTRYPOINTTEASER.value)
