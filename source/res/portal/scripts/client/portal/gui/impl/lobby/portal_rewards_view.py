# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/portal_rewards_view.py
import typing
import logging
from helpers import dependency
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.server_events.bonuses import getNonQuestBonuses
from skeletons.gui.game_control import IHangarFeatureStateController
from frameworks.wulf import ViewSettings, WindowFlags, ViewFlags, WindowLayer
from portal.gui.impl.gen.view_models.views.lobby.portal_rewards_view_model import PortalRewardsViewModel, PortalRewardType
from portal.gui.impl.lobby.bonus_packer import packBonusModelAndTooltipData
from portal.gui.game_control.awards_controller import AwardType
from portal.skeletons.portal_event_controller import IPortalEventController
if typing.TYPE_CHECKING:
    from typing import Optional, List
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)

class PortalRewardsView(ViewImpl):
    __slots__ = ('__rewardsData', '__closeCallback', '__tooltipData')
    __hangarFeatureStateController = dependency.descriptor(IHangarFeatureStateController)
    __gameEventController = dependency.descriptor(IPortalEventController)

    def __init__(self, layoutID, rewardsData, closeCallback):
        settings = ViewSettings(layoutID)
        settings.model = PortalRewardsViewModel()
        settings.flags = ViewFlags.VIEW
        super(PortalRewardsView, self).__init__(settings)
        self.__rewardsData = rewardsData
        self.__closeCallback = closeCallback
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(PortalRewardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(PortalRewardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(PortalRewardsView, self)._onLoading(*args, **kwargs)
        self.__updateModel()
        self.__addListeners()

    def _onLoaded(self, *args, **kwargs):
        self.__hangarFeatureStateController.enter(self.layoutID, doHideHeader=True)

    def _finalize(self):
        self.__executeCloseCallback()
        self.__hangarFeatureStateController.exit(self.layoutID)
        self.__removeListeners()
        super(PortalRewardsView, self)._finalize()

    def __addListeners(self):
        self.viewModel.onApprove += self.__onCloseHandler

    def __removeListeners(self):
        self.viewModel.onApprove -= self.__onCloseHandler

    def __updateModel(self):
        rewards = self.__rewardsData['rewards']
        rewardType = self.__rewardsData['type']
        bonuses = self.__processBonuses(rewards)
        isSpecial = self.__checkIfSpecial(bonuses)
        with self.viewModel.transaction() as model:
            model.setIsSpecial(isSpecial)
            packBonusModelAndTooltipData(bonuses, model.getRewards(), self.__tooltipData)
            if rewardType == AwardType.PROGRESSION:
                self.__fillProgressionModel(model)
            elif rewardType == AwardType.LAST_LEVEL_VICTORY:
                self.__fillLastLevelVictoryModel(model)
            elif rewardType == AwardType.ALL_VEHICLES_UPGRADED:
                self.__fillAllVehiclesUpgradeModel(model)
            else:
                _logger.error('Unknown reward type %s', rewardType)

    def __fillProgressionModel(self, model):
        model.setRewardType(PortalRewardType.PROGRESSION)
        model.setLevel(self.__rewardsData['stage'])

    def __fillLastLevelVictoryModel(self, model):
        model.setRewardType(PortalRewardType.LAST_LEVEL_VICTORY)

    def __fillAllVehiclesUpgradeModel(self, model):
        model.setRewardType(PortalRewardType.ALL_VEHICLES_UPGRADED)

    def __onCloseHandler(self):
        self.__executeCloseCallback()
        self.destroyWindow()

    def __executeCloseCallback(self):
        if self.__closeCallback is not None:
            callback = self.__closeCallback
            self.__closeCallback = None
            callback()
        return

    @staticmethod
    def __processBonuses(bonusesData, ctx=None):
        resultBonuses = []
        for key, value in bonusesData.iteritems():
            bonuses = getNonQuestBonuses(key, value, ctx)
            resultBonuses.extend(bonuses)

        return resultBonuses

    @staticmethod
    def __checkIfSpecial(bonuses):
        for bonus in bonuses:
            if bonus.getName() == 'tankmen':
                return True
            if bonus.getName() == 'dossier' and PortalRewardsView.__isDossierSpecial(bonus):
                return True

        return False

    @staticmethod
    def __isDossierSpecial(dossierBonus):
        return dossierBonus.getAchievements() or dossierBonus.getBadges()


class PortalRewardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewardsData, closeCallback=None, parent=None):
        super(PortalRewardsViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PortalRewardsView(R.views.portal.lobby.PortalRewardsView(), rewardsData, closeCallback), parent=parent, layer=WindowLayer.TOP_WINDOW)
