# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/hangar_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.halloween.afk_banner_view_model import AfkBannerViewModel
from gui.impl.gen.view_models.views.lobby.halloween.daily_widget_view_model import DailyWidgetViewModel
from gui.impl.gen.view_models.views.lobby.halloween.hangar_tank_model import HangarTankModel
from gui.impl.gen.view_models.views.lobby.halloween.meta_widget_view_model import MetaWidgetViewModel

class HangarViewModel(ViewModel):
    __slots__ = ('onClose', 'onEscape', 'onTankChanged', 'onRedirectTo', 'onMoveSpace', 'onOverScene')
    INFO = 'info'
    REWARDS = 'rewards'
    DAILY = 'daily'
    MEMORIES = 'memories'
    PACKAGES = 'packages'
    STYLES = 'styles'

    def __init__(self, properties=7, commands=6):
        super(HangarViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def selectedTank(self):
        return self._getViewModel(0)

    @property
    def metaWidget(self):
        return self._getViewModel(1)

    @property
    def dailyWidget(self):
        return self._getViewModel(2)

    @property
    def afkBanner(self):
        return self._getViewModel(3)

    def getIsLoadedSetup(self):
        return self._getBool(4)

    def setIsLoadedSetup(self, value):
        self._setBool(4, value)

    def getTanks(self):
        return self._getArray(5)

    def setTanks(self, value):
        self._setArray(5, value)

    def getIsNeedReload(self):
        return self._getBool(6)

    def setIsNeedReload(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(HangarViewModel, self)._initialize()
        self._addViewModelProperty('selectedTank', HangarTankModel())
        self._addViewModelProperty('metaWidget', MetaWidgetViewModel())
        self._addViewModelProperty('dailyWidget', DailyWidgetViewModel())
        self._addViewModelProperty('afkBanner', AfkBannerViewModel())
        self._addBoolProperty('isLoadedSetup', False)
        self._addArrayProperty('tanks', Array())
        self._addBoolProperty('isNeedReload', False)
        self.onClose = self._addCommand('onClose')
        self.onEscape = self._addCommand('onEscape')
        self.onTankChanged = self._addCommand('onTankChanged')
        self.onRedirectTo = self._addCommand('onRedirectTo')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onOverScene = self._addCommand('onOverScene')
