# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/wt_event/battle_progression_view.py
from frameworks.wulf import ViewFlags, WindowFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.wt_event.hunters_battle_progression_view_model import HuntersBattleProgressionViewModel
from gui.shared.gui_items.Vehicle import VEHICLE_EVENT_TYPE
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter

class HuntersBattleProgressionView(ViewImpl):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.battle.wt_event.battle_progression_view.HuntersBattleProgressionView(), flags=ViewFlags.COMPONENT, model=HuntersBattleProgressionViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(HuntersBattleProgressionView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(HuntersBattleProgressionView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        arenaInfoCtrl = self.__sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onPowerPointsChanged += self.__onPowerPointsChanged
        self.__updateViewModel()
        return

    def _finalize(self):
        arenaInfoCtrl = self.__sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onPowerPointsChanged -= self.__onPowerPointsChanged
        return

    def __updateViewModel(self):
        with self.viewModel.transaction() as model:
            self.__updateProgress(model)
            self.__updateMaxLevel(model)
            self.__updateEnemyMode(model)

    def __updateProgress(self, model):
        arenaInfoCtrl = self.__sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            model.setProgress(arenaInfoCtrl.powerPoints)
        return

    def __updateMaxLevel(self, model):
        arenaInfoCtrl = self.__sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            model.setMaxLevel(arenaInfoCtrl.maxPowerPoints)
        return

    def __updateEnemyMode(self, model):
        vehicleDescr = avatar_getter.getVehicleTypeDescriptor()
        if vehicleDescr is not None:
            model.setIsEnemyMode(VEHICLE_EVENT_TYPE.EVENT_BOSS in vehicleDescr.type.tags)
        return

    def __onPowerPointsChanged(self, _):
        with self.viewModel.transaction() as model:
            self.__updateProgress(model)


class HuntersBattleProgressionWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(HuntersBattleProgressionWindow, self).__init__(WindowFlags.WINDOW, content=HuntersBattleProgressionView(), parent=parent)
