# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/views/battle_quest_awards_view.py
import logging
import typing
from collections import defaultdict
from frameworks.wulf import ViewSettings, WindowFlags
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.prb_control.entities.base.listener import IPrbListener
from gui.server_events.bonuses import DossierBonus, VehiclesBonus, getNonQuestBonuses
from gui.shared import event_dispatcher
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_quest_awards_model import BattleQuestAwardsModel, BattleStatus
from historical_battles.gui.impl.lobby.views.bonus_packer import getBonusPacker
from historical_battles.gui.hb_helpers import isDiscountBonus, getDiscountFromEntitlementBonus, isVehicleTokenBonus, repackTokenToVehicle
from historical_battles.gui.shared.event_dispatcher import showShopView
from historical_battles.gui.sounds_constants import GENERAL_SOUND_SPACE
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from frameworks.wulf import WindowLayer
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import List, Optional, Dict
    from frameworks.wulf import Array
    from gui.server_events.bonuses import SimpleBonus
    from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
_MAIN_BONUSES = 'mainBonuses'
_REGULAR_BONUSES = 'regularBonuses'

def awardsFactory(bonusesData, ctx=None, hasHeroVehicle=False):
    resultBonuses = defaultdict(list)
    for key, value in bonusesData.iteritems():
        bonuses = getNonQuestBonuses(key, value, ctx)
        for bonus in bonuses:
            if _checkIsNeedSkip(bonus, hasHeroVehicle):
                continue
            if bonus.getName() == 'battleToken' and isVehicleTokenBonus(bonus):
                bonus = repackTokenToVehicle(bonus)
            isMain = bonus.getName() == VehiclesBonus.VEHICLES_BONUS or key == DossierBonus.DOSSIER_BONUS and DossierBonus.hasBadges(bonus)
            bonusKey = _MAIN_BONUSES if isMain else _REGULAR_BONUSES
            resultBonuses[bonusKey].append(bonus)

    return resultBonuses


def _checkIsNeedSkip(bonus, hasHeroVehicle):
    if isDiscountBonus(bonus):
        return hasHeroVehicle or getDiscountFromEntitlementBonus(bonus) >= 100
    return True if isVehicleTokenBonus(bonus) and hasHeroVehicle else False


class BattleQuestAwardsView(ViewImpl, IPrbListener):
    _COMMON_SOUND_SPACE = GENERAL_SOUND_SPACE
    _gameEventController = dependency.descriptor(IGameEventController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__tooltipData', '_stage')

    def __init__(self, stage):
        settings = ViewSettings(R.views.historical_battles.lobby.BattleQuestAwardsView())
        settings.model = BattleQuestAwardsModel()
        self.__tooltipData = {}
        self._stage = stage
        super(BattleQuestAwardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleQuestAwardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattleQuestAwardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def updateModel(self):
        level = self._stage.get('stage', 0)
        isFinishStage = self._stage.get('finishStage', False)
        rewardsData = self._stage.get('detailedRewards', {})
        hasHeroVehicle = self._gameEventController.heroTank.hasHeroVehicle()
        bonuses = awardsFactory(rewardsData, hasHeroVehicle=hasHeroVehicle)
        with self.viewModel.transaction() as model:
            model.setBattleStatus(BattleStatus.INPROGRESS if not isFinishStage else BattleStatus.COMPLETED)
            model.setLevel(level)
            model.setHasMainVehicle(hasHeroVehicle)
            self.__updatemodelRewards(model.getRewards(), bonuses[_REGULAR_BONUSES])
            self.__updatemodelRewards(model.getMainRewards(), bonuses[_MAIN_BONUSES])

    def _onLoading(self, *args, **kwargs):
        super(BattleQuestAwardsView, self)._onLoading(args, kwargs)
        self.updateModel()
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(BattleQuestAwardsView, self)._finalize()

    def __updatemodelRewards(self, rewardsArray, bonuses):
        packBonusModelAndTooltipData(bonuses, rewardsArray, self.__tooltipData, getBonusPacker())

    def __addListeners(self):
        with self.viewModel.transaction() as model:
            model.onClose += self.__onClose
            model.onApprove += self.__onApprove
            model.onShopClick += self.__onShopClick
            model.onHangarClick += self.__onHangarClick
        self._gameEventController.onCloseAllAwardsWindow += self.__onClose

    def __removeListeners(self):
        with self.viewModel.transaction() as model:
            model.onClose -= self.__onClose
            model.onApprove -= self.__onApprove
            model.onShopClick -= self.__onShopClick
            model.onHangarClick -= self.__onHangarClick
        self._gameEventController.onCloseAllAwardsWindow -= self.__onClose

    def __onClose(self):
        self.destroyWindow()

    def __onApprove(self):
        self.__onClose()

    def __onShopClick(self):
        showShopView()
        self.__onClose()

    def __onHangarClick(self):
        vehicleCD = self._gameEventController.heroTank.getVehicleCD()
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        if vehicle and vehicle.isInInventory:
            self._gameEventController.onCloseAllAwardsWindow()
            from historical_battles.gui.impl.lobby.hb_helpers.hangar_helpers import closeEvent
            event_dispatcher.selectVehicleInHangar(vehicleCD)
            closeEvent()


class BattleQuestAwardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, stage, parent=None):
        super(BattleQuestAwardsViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BattleQuestAwardsView(stage), parent=parent, layer=WindowLayer.TOP_WINDOW)
