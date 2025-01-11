# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/ny/ny_attached_3d_rewards.py
import BigWorld
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from frameworks.wulf import Array
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_attached_3d_rewards_model import NyAttached3DRewardsModel
from gui.impl.lobby.gf_notifications.ny.award_notification_base import AwardNotificationBase, MAX_HUGE_REWARDS, fromRawBonusWithListsToBonuses
from gui.impl.new_year.new_year_bonus_packer import getChallengeBonusPacker, packBonusModelAndTooltipData, formatedBonusSortOrder
from gui.impl.new_year.new_year_helper import nyCreateToolTipContentDecorator, backportTooltipDecorator
from gui.Scaleform.daapi.view.lobby.customization.shared import isC11nEnabled
from gui.shared.event_dispatcher import showHangar
from gui.shared.utils import flashObject2Dict
from gui.impl.new_year.navigation import NewYearNavigation
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
from skeletons.new_year import ICelebritySceneController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IGFNotificationsController
_RARITY_BONUSES_ORDER = ({'getName': 'customizations',
  'getIcon': 'attachment',
  'getRarity': 'legendary'}, {'getName': 'customizations',
  'getIcon': 'attachment',
  'getRarity': 'epic'}, {'getName': 'customizations',
  'getIcon': 'attachment',
  'getRarity': 'rare'})

def attached3DNotificationBonusSortOrder(bonusItems):
    bonus, _, __ = bonusItems
    return formatedBonusSortOrder(bonus, _RARITY_BONUSES_ORDER)


class NyAttached3DRewards(AwardNotificationBase):
    eventsCache = dependency.descriptor(IEventsCache)
    __customizationService = dependency.descriptor(ICustomizationService)
    __celebritySceneController = dependency.descriptor(ICelebritySceneController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    __gfNotificationController = dependency.descriptor(IGFNotificationsController)

    def __init__(self, resId, *args, **kwargs):
        model = NyAttached3DRewardsModel()
        super(NyAttached3DRewards, self).__init__(resId, model, *args, **kwargs)
        self.__bonuses = []

    @property
    def viewModel(self):
        return super(NyAttached3DRewards, self).getViewModel()

    @staticmethod
    def __prepareRawData(rawData):
        rewards = {}
        for key, data in rawData.iteritems():
            if isinstance(data, list):
                listOfBonuses = []
                for item in data:
                    listOfBonuses.append(flashObject2Dict(item))

                rewards[key] = listOfBonuses
            rewards[key] = data

        return rewards

    def _onLoading(self, *args, **kwargs):
        data = self._linkageData.toDict()
        self.__bonuses = fromRawBonusWithListsToBonuses(data.get('bonuses', {}))
        super(NyAttached3DRewards, self)._onLoading(self)

    def _update(self):
        self.__setRewards()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NyAttached3DRewards, self).createToolTip(event)

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        return super(NyAttached3DRewards, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        events = super(NyAttached3DRewards, self)._getEvents()
        return events + ((self.viewModel.onGoToExterior, self.__onGoToExterior), (self.viewModel.onGoToGarage, self.__onGoToGarage))

    def __setRewards(self):
        bonuses = self.__bonuses
        with self.getViewModel().transaction() as model:
            self._tooltips.clear()
            tempArray = Array()
            packBonusModelAndTooltipData(bonuses, tempArray, getChallengeBonusPacker(), self._tooltips, sortKey=attached3DNotificationBonusSortOrder)
            valuableBonuses = []
            for bonusModel in tempArray:
                valuableBonuses.append(bonusModel)

            hugeBonuses = valuableBonuses[:MAX_HUGE_REWARDS]
            fillViewModelsArray(hugeBonuses, model.hugeRewards.getItems())
            canNavigate = self._canNavigate() and self._nyController.isEnabled()
            model.setIsButtonDisabled(not canNavigate)
            model.setIsPopUp(self._isPopUp)
            model.setIsFirstAttach(not self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.NEW_C11N_SECTION_HINT))

    def __onGoToExterior(self):
        BigWorld.callback(0.0, lambda : self.__customizationService.showCustomization() if isC11nEnabled() else self.__onGoToGarage())

    def __onGoToGarage(self):
        if NewYearNavigation.getCurrentViewName() is not None:
            NewYearNavigation.closeMainView()
        else:
            self.__gfNotificationController.selectRandomBattle(showHangar)
        return
