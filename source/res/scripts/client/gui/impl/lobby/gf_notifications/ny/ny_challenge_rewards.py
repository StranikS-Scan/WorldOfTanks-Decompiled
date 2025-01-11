# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/ny/ny_challenge_rewards.py
import BigWorld
import typing
from frameworks.wulf import Array
from frameworks.wulf.view.array import fillViewModelsArray
from gui.Scaleform.genConsts.BARRACKS_CONSTANTS import BARRACKS_CONSTANTS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_challenge_rewards_model import NyChallengeRewardsModel, Type
from gui.impl.lobby.gf_notifications.ny.award_notification_base import AwardNotificationBase, MAX_HUGE_REWARDS, MAX_ADD_REWARDS, fromRawBonusWithListsToBonuses
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.impl.new_year.navigation import ViewAliases, NewYearNavigation
from gui.impl.new_year.new_year_bonus_packer import getChallengeBonusPacker, packBonusModelAndTooltipData, formatedBonusSortOrder, isBonusInOrder
from gui.impl.new_year.new_year_helper import nyCreateToolTipContentDecorator, backportTooltipDecorator, ADDITIONAL_BONUS_NAME_GETTERS
from gui.Scaleform.daapi.view.lobby.customization.shared import isC11nEnabled
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showHangar
from gui.shared.utils import flashObject2Dict
from helpers import dependency
from new_year.ny_constants import NYObjects
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IGFNotificationsController
from skeletons.gui.server_events import IEventsCache
from skeletons.new_year import ICelebritySceneController
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
    from gui.impl.gen.view_models.common.bonus_model import BonusModel
_VALUABLE_BONUSES_NAMES = ('modernizedImprovedSightsEnhancedAimDrives2', 'modernizedImprovedSightsEnhancedAimDrives1', 'tmanToken', 'customizations_style', 'customizations', 'variadicDiscount', 'singleAchievements')
BONUSES_ORDER = ('tmanToken', 'customizations_style', 'vehicles', 'playerBadges', 'singleAchievements')

def __getAdditionalNameItems(bonus):
    item, _ = first(bonus.getItems().iteritems())
    return item.descriptor.name if item is not None else bonus.getName()


BONUS_NAME_GETTERS = {'items': __getAdditionalNameItems}
BONUS_NAME_GETTERS.update(ADDITIONAL_BONUS_NAME_GETTERS)

def _getBonusName(bonus):
    bonusName = bonus.getName()
    getAdditionalName = BONUS_NAME_GETTERS.get(bonusName)
    if getAdditionalName is not None:
        bonusName = getAdditionalName(bonus)
    return bonusName


def isValuableBonus(bonus):
    return _getBonusName(bonus) in _VALUABLE_BONUSES_NAMES


def checkAnyValuableBonus(bonuses):
    return any((isValuableBonus(bonus) for bonus in bonuses))


_VALUABLE_BONUSES_ORDER = ({'getName': 'customizations',
  'getIcon': 'attachment',
  'getRarity': 'legendary'},
 {'getName': 'customizations',
  'getIcon': 'attachment',
  'getRarity': 'epic'},
 {'getName': 'customizations',
  'getIcon': 'attachment',
  'getRarity': 'rare'},
 {'getName': 'tmanToken'},
 {'getName': 'items',
  'getOverlayType': 'equipmentModernized_2'},
 {'getName': 'items',
  'getOverlayType': 'equipmentModernized_1'},
 {'getName': 'customizations',
  'getIcon': 'style'},
 {'getName': 'customizations',
  'getIcon': 'projectionDecal'},
 {'getName': 'customizations',
  'getIcon': 'inscription'},
 {'getName': 'variadicDiscount',
  'getLevel': '10'},
 {'getName': 'variadicDiscount',
  'getLevel': '9'},
 {'getName': 'variadicDiscount',
  'getLevel': '8'},
 {'getName': 'variadicDiscount',
  'getLevel': '7'},
 {'getName': 'variadicDiscount',
  'getLevel': '6'},
 {'getName': 'variadicDiscount',
  'getLevel': '5'},
 {'getName': 'dossier_achievement'})

def isValuableBonusModel(bonusModel):
    return isBonusInOrder(bonusModel, _VALUABLE_BONUSES_ORDER)


def challengeNotificationBonusSortOrder(bonusItems):
    bonus, _, __ = bonusItems
    return formatedBonusSortOrder(bonus, _VALUABLE_BONUSES_ORDER)


def _bonusesSortOrder(bonus):
    bonusName = _getBonusName(bonus)
    return BONUSES_ORDER.index(bonusName) if bonusName in BONUSES_ORDER else len(BONUSES_ORDER)


class NyChallengeRewards(AwardNotificationBase):
    eventsCache = dependency.descriptor(IEventsCache)
    __customizationService = dependency.descriptor(ICustomizationService)
    __celebritySceneController = dependency.descriptor(ICelebritySceneController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    __gfNotificationController = dependency.descriptor(IGFNotificationsController)

    def __init__(self, resId, *args, **kwargs):
        model = NyChallengeRewardsModel()
        super(NyChallengeRewards, self).__init__(resId, model, *args, **kwargs)
        self.__bonuses = []
        self.__isFirstAttach = False
        self.__completedQuestsCount = 0
        self.__guestName = Type.CHALLENGE

    @property
    def viewModel(self):
        return super(NyChallengeRewards, self).getViewModel()

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
        self.__completedQuestsCount = data.get('completedQuestsCount', 0)
        self.__isFirstAttach = data.get('isFirstAttach', False)
        super(NyChallengeRewards, self)._onLoading(self)

    def _update(self):
        self.__setRewards()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NyChallengeRewards, self).createToolTip(event)

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        return NyGiftMachineTokenTooltip() if contentID == R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip() else super(NyChallengeRewards, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        events = super(NyChallengeRewards, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick),
         (self.viewModel.onRecruit, self.__onRecruit),
         (self.viewModel.onGoToExterior, self.__onGoToExterior),
         (self.viewModel.onGoToGarage, self.__onGoToGarage))

    def __setRewards(self):
        bonuses = self.__bonuses
        with self.getViewModel().transaction() as model:
            self._tooltips.clear()
            tempArray = Array()
            packBonusModelAndTooltipData(bonuses, tempArray, getChallengeBonusPacker(), self._tooltips, sortKey=challengeNotificationBonusSortOrder)
            valuableBonuses = []
            standartBonuses = []
            for bonusModel in tempArray:
                if isValuableBonusModel(bonusModel):
                    valuableBonuses.append(bonusModel)
                standartBonuses.append(bonusModel)

            hugeBonuses = valuableBonuses[:MAX_HUGE_REWARDS]
            addBonuses = valuableBonuses[MAX_HUGE_REWARDS:MAX_HUGE_REWARDS + MAX_ADD_REWARDS]
            fillViewModelsArray(hugeBonuses, model.hugeRewards.getItems())
            fillViewModelsArray(addBonuses, model.rewards.getItems())
            canNavigate = self._canNavigate() if self.__hasTmanToken(hugeBonuses) else self._canNavigate() and self._nyController.isEnabled()
            model.setIsButtonDisabled(not canNavigate)
            model.setIsPopUp(self._isPopUp)
            model.setCompletedQuestsQuantity(self.__completedQuestsCount)
            model.setTotalQuestsQuantity(self.__celebritySceneController.allQuestsCount)
            model.setQuestsQuantity(self.__celebritySceneController.questsCount)
            otherBonusCount = len(standartBonuses) + len(valuableBonuses[MAX_HUGE_REWARDS + MAX_ADD_REWARDS:])
            model.setOtherBonusCount(otherBonusCount)
            model.setIsFirstAttach(self.__isFirstAttach)

    @staticmethod
    def __hasTmanToken(bonuses):
        for bonus in bonuses:
            if bonus.getName() == 'tmanToken':
                return True

    def __onClick(self):
        if self._canNavigate() and self._nyController.isEnabled():
            viewName = NewYearNavigation.getCurrentViewName()
            currentObject = NewYearNavigation.getCurrentObject()
            if viewName == ViewAliases.CELEBRITY_VIEW and currentObject == NYObjects.CHALLENGE:
                return
            self._navigateToNy(NYObjects.CHALLENGE, ViewAliases.CELEBRITY_VIEW)

    def __onRecruit(self):
        if self._canNavigate():
            event_dispatcher.showBarracks(location=BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED)

    def __onGoToExterior(self):
        BigWorld.callback(0.0, lambda : self.__customizationService.showCustomization() if isC11nEnabled() else showHangar())

    def __onGoToGarage(self):
        if NewYearNavigation.getCurrentViewName() is not None:
            NewYearNavigation.closeMainView()
        else:
            self.__gfNotificationController.selectRandomBattle(showHangar)
        return
