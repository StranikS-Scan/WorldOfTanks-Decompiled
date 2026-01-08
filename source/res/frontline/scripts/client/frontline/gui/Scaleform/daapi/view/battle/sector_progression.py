# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/sector_progression.py
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import MINIMAP_SIZE
from frameworks.wulf import ViewSettings, ViewFlags
from frontline.gui.impl.gen.view_models.views.battle.fl_progression_cmp_model import FlProgressionCmpModel, MapSize
from frontline.gui.impl.gen.view_models.views.battle.fl_progression_model import FlProgressionModel
from gui.Scaleform.daapi.view.meta.FLProgressionCmpMeta import FLProgressionCmpMeta
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.sounds.epic_sound_constants import EPIC_SOUND
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleController
DEFAULT_PROGRESS = (-1, -1)
_logger = logging.getLogger(__name__)

class SectorProgressionInject(FLProgressionCmpMeta):
    __epicBattleController = dependency.descriptor(IEpicBattleController)

    def _onPopulate(self):
        super(SectorProgressionInject, self)._onPopulate()
        self.as_updateVisibilityS(self.__isVisible())
        self.__epicBattleController.onProgressionModelChanged += self.__onProgressionModelChanged
        self.__epicBattleController.onCurrentSectorChanged += self.__onCurrentSectorChanged

    def _dispose(self):
        self.__epicBattleController.onProgressionModelChanged -= self.__onProgressionModelChanged
        self.__epicBattleController.onCurrentSectorChanged -= self.__onCurrentSectorChanged
        super(SectorProgressionInject, self)._dispose()

    def __onProgressionModelChanged(self, *_):
        self.as_updateVisibilityS(self.__isVisible())

    def __onCurrentSectorChanged(self, *_):
        self.as_updateVisibilityS(self.__isVisible())

    def __isVisible(self):
        return False if self._injectView is None else not self._injectView.isHidden()

    def _makeInjectView(self, *_):
        return SectorProgressionCmpView()


class SectorProgressionCmpView(ViewImpl):
    __epicBattleController = dependency.descriptor(IEpicBattleController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.frontline.battle.FLProgressionCmp(), flags=flags, model=FlProgressionCmpModel())
        super(SectorProgressionCmpView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(SectorProgressionCmpView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setIsHidden(self.isHidden())
            vm.setMapSize(self.__getMinimapSize())

    def _getEvents(self):
        return ((self.__epicBattleController.onProgressionModelChanged, self.__onProgressionModelChanged),
         (self.__epicBattleController.onCurrentSectorChanged, self.__onCurrentSectorChanged),
         (AccountSettings.onSettingsChanging, self.__onAccountSettingsChanging),
         (self.__epicBattleController.onSupplyActivated, self.__onSupplyActivated))

    @property
    def viewModel(self):
        return super(SectorProgressionCmpView, self).getViewModel()

    def __onAccountSettingsChanging(self, key, _):
        if key == MINIMAP_SIZE:
            with self.viewModel.transaction() as vm:
                vm.setMapSize(self.__getMinimapSize())

    def __onProgressionModelChanged(self, sectorName, progression):
        with self.viewModel.transaction() as vm:
            vm.setIsHidden(self.isHidden())
            vm.setSectorName(sectorName)
            self.fillProgressionArrayModels(progression, vm.getProgressions())

    def __onCurrentSectorChanged(self, _):
        with self.viewModel.transaction() as vm:
            vm.setIsHidden(self.isHidden())

    def isHidden(self):
        progression = self.__epicBattleController.getSectorProgression()
        return not progression or progression == DEFAULT_PROGRESS or not self.__epicBattleController.isOnOwnSector()

    @classmethod
    def fillProgressionArrayModels(cls, progression, container):
        container.clear()
        for milestone, percent in progression:
            firstSupply = FlProgressionModel()
            firstSupply.setName(milestone)
            firstSupply.setCurrent(percent)
            container.addViewModel(firstSupply)

        container.invalidate()

    @staticmethod
    def __getMinimapSize():
        sizeIdx = AccountSettings.getSettings(MINIMAP_SIZE)
        if sizeIdx < 2:
            return MapSize.SMALL
        return MapSize.MEDIUM if sizeIdx < 3 else MapSize.LARGE

    def __onSupplyActivated(self, _):
        self.soundManager.playSound(EPIC_SOUND.EB_UI_SUPPLY_UNLOCKED)
