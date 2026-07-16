# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/challenges/challenge_missions_tab.py
from __future__ import absolute_import
import typing
from account_helpers.AccountSettings import ChallengesMissions
from challenges_common import ChallengeDifficulties, ChallengeMainRewardTypes
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.challenges.challenges_decorators import createTooltipContentDecorator
from gui.challenges.challenges_helpers import getSettings, setSettings, setVisitedChallenge
from gui.customization.shared import getPurchaseGoldForCredits
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.challenge_missions.challenge_missions import ChallengeMissions
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.challenge_missions.challenges_pack import ChallengesPack
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.challenges.views_helpers import updateChallengeModel, getSuitableVehicles
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.user_missions.hub.update_children_mixin import UpdateChildrenMixin
from gui.impl.lobby.user_missions.tooltips.challenges_restart_tooltip import ChallengesRestartTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showExchangeCurrencyWindowModal, showStylePreview, showVehicleHubOverview, selectVehicleInHangar, showAttachmentsSetPreview
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency, Money
from gui.shop import showBuyGoldForBundle
from helpers import dependency
from skeletons.gui.challenges import IChallengesController
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from shared_utils import first, findFirst
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.challenges.challenge_item import ChallengeItem

class ChallengeMissionsTab(UpdateChildrenMixin, ViewComponent[ChallengeMissions]):
    LAYOUT_ID = R.aliases.user_missions.hub.challengeMissions.MainView()
    __challenges = dependency.descriptor(IChallengesController)
    __customizationService = dependency.descriptor(ICustomizationService)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, challengeID):
        self.__challengeID = challengeID
        self.__enabled = False
        self.__selectedChallenge = None
        self.__isSuitableVehicles = False
        self.__commands = {}
        self.__missionTooltipData = {}
        super(ChallengeMissionsTab, self).__init__(model=ChallengeMissions)
        return

    @property
    def viewModel(self):
        return super(ChallengeMissionsTab, self).getViewModel()

    @property
    def selectedChallenge(self):
        return self.__selectedChallenge

    def update(self, challengeID=None):
        if challengeID is not None and challengeID in self.__getAvailableChallengesIDs():
            self.__challengeID = challengeID
            self.__selectedChallenge = self.__challenges.getChallenge(self.__challengeID)
            self.__setVisitedChallenge()
        self.__updateModel()
        return

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ChallengeMissionsTab, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return ChallengesRestartTooltip(self.__selectedChallenge) if contentID == R.views.mono.user_missions.tooltips.challenges_restart_tooltip() else super(ChallengeMissionsTab, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            missionId = event.getArgument('missionId')
            return None if missionId is None else self.__missionTooltipData.get(missionId, {}).get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(ChallengeMissionsTab, self)._onLoading()
        self.__enabled = self.__getAvailability()
        self.__isSuitableVehicles = bool(getSuitableVehicles())
        self.__commands = {ChallengeMissions.ACTION_ACTIVATE: self.__challenges.activateChallenge,
         ChallengeMissions.ACTION_RESTART: self.__challenges.restartChallenge,
         ChallengeMissions.ACTION_SURRENDER: self.__challenges.surrenderChallenge}
        if self.__enabled:
            if not getSettings(ChallengesMissions.CHALLENGES_BUNDLE_SHOWN, False):
                setSettings(ChallengesMissions.CHALLENGES_BUNDLE_SHOWN, True)
            if self.__challengeID is not None and self.__challengeID in self.__getAvailableChallengesIDs():
                self.__selectedChallenge = self.__challenges.getChallenge(self.__challengeID)
            else:
                self.__chooseSelectedChallenge()
        self.__setVisitedChallenge()
        self.__updateModel()
        return

    def _finalize(self):
        super(ChallengeMissionsTab, self)._finalize()
        self.__commands = None
        self.__selectedChallenge = None
        self.__missionTooltipData = None
        return

    def _getCallbacks(self):
        moneyCallbacks = tuple((('stats.{}'.format(c), self.__onMoneyUpdated) for c in Currency.ALL))
        return super(ChallengeMissionsTab, self)._getCallbacks() + moneyCallbacks + (('inventory.1.compDescr', self.__onVehiclesSyncCompleted),)

    def _getEvents(self):
        return ((self.__challenges.onChallengesSettingsChanged, self.__onSettingsChanged),
         (self.__challenges.onActiveChallengeChanged, self.__onSettingsChanged),
         (self.__challenges.onChallengesClientUpdated, self.__updateChallenges),
         (self.viewModel.onSelectChallenge, self.__onSelectedChallengeChanged),
         (self.viewModel.onAction, self.__onAction),
         (self.viewModel.openPreview, self.__openPreview))

    def __onSettingsChanged(self, *_):
        self.__enabled = self.__getAvailability()
        if self.__enabled:
            if self.__challengeID in self.__getAvailableChallengesIDs():
                self.__selectedChallenge = self.__challenges.getChallenge(self.__challengeID)
            else:
                self.__chooseSelectedChallenge()
        self.__setVisitedChallenge()
        self.__updateModel()

    def __onVehiclesSyncCompleted(self, _):
        self.__isSuitableVehicles = bool(getSuitableVehicles())
        self.__updateModel()

    def __onMoneyUpdated(self, _):
        self.__updateChallenges()

    @args2params(int)
    def __onSelectedChallengeChanged(self, selectedChallengeID):
        self.__challengeID = selectedChallengeID
        self.__selectedChallenge = self.__challenges.getChallenge(self.__challengeID)
        self.__setVisitedChallenge()
        self.viewModel.setSelectedChallengeID(self.__selectedChallenge.challengeID)
        self.viewModel.setSelectedChallengeExpireTime(self.__selectedChallenge.expireTime)

    @args2params(str, bool)
    def __onAction(self, action, isFree):
        if action == ChallengeMissions.ACTION_RESTART:
            if not isFree and not self.__challenges.isEnoughMoneyForRestart(self.__selectedChallenge):
                price = self.__selectedChallenge.restartPrice
                currency, cost = first(price.items())
                if currency == Currency.GOLD:
                    showBuyGoldForBundle(cost, {})
                    return
                if currency == Currency.CREDITS:
                    gold = getPurchaseGoldForCredits(Money(**price))
                    showExchangeCurrencyWindowModal(gold=gold)
                    return
            self.__commands[action](self.__selectedChallenge.challengeID, isFree)
        else:
            self.__commands[action](self.__selectedChallenge.challengeID)

    def __getAvailableChallengesIDs(self):
        return [ ch.challengeID for ch in self.__challenges.availableChallenges() ]

    def __setVisitedChallenge(self):
        if self.__selectedChallenge is not None and not self.__selectedChallenge.isVisited:
            setVisitedChallenge(self.__selectedChallenge.challengeID)
        return

    def __getAvailability(self):
        return self.__challenges.isEnabled and bool(self.__challenges.availableChallenges())

    def __chooseSelectedChallenge(self):
        if self.__challenges.activeChallengeID:
            self.__selectedChallenge = self.__challenges.getChallenge(self.__challenges.activeChallengeID)
        else:
            self.__selectedChallenge = findFirst(lambda c: not self.__challenges.isChallengeCompleted(c), self.__challenges.getSortedChallenges(), default=self.__challenges.getSortedChallenges()[0])
        self.__challengeID = self.__selectedChallenge.challengeID

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            model.setEnabled(self.__enabled)
            if self.__enabled:
                model.setIsSuitableVehicles(self.__isSuitableVehicles)
                self.__updateChallenges(model=model)

    @replaceNoneKwargsModel
    def __updateChallenges(self, model=None):
        self.__missionTooltipData = {}
        model.setActiveChallengeID(self.__challenges.activeChallengeID)
        model.setSelectedChallengeID(self.__selectedChallenge.challengeID)
        model.setSelectedChallengeExpireTime(self.__selectedChallenge.expireTime)
        challengesPacks = model.getChallengesPacks()
        challengesPacks.clear()
        for difficulty in ChallengeDifficulties:
            challengesPacks.addViewModel(self.__updateChallengePack(difficulty))

        challengesPacks.invalidate()

    def __updateChallengePack(self, difficulty):
        packModel = ChallengesPack()
        packModel.setComplexity(difficulty.name.lower())
        challengesModel = packModel.getChallenges()
        challengesModel.clear()
        for challenge in self.__challenges.getSortedChallenges():
            if challenge.difficulty == difficulty:
                challengesModel.addViewModel(updateChallengeModel(challenge, self.__missionTooltipData))

        challengesModel.invalidate()
        return packModel

    @args2params(str, int, int, str)
    def __openPreview(self, bonusType, bonusId, styleID, attachmentsToken):
        if bonusType == ChallengeMainRewardTypes.ATTACHMENTS_SET.value:
            showAttachmentsSetPreview(attachmentsToken)
        elif bonusType == ChallengeMainRewardTypes.STYLE_2D.value:
            style = self.__customizationService.getItemByID(GUI_ITEM_TYPE.STYLE, bonusId)
            vehicleCD = getVehicleCDForStyle(style)
            showStylePreview(vehicleCD, style)
        elif bonusType == ChallengeMainRewardTypes.VEHICLE.value:
            vehicle = self.__itemsCache.items.getItemByCD(bonusId)
            if vehicle is None:
                return
            if vehicle.isInInventory:
                selectVehicleInHangar(bonusId)
            else:
                style = self.__customizationService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID) if styleID else None
                showVehicleHubOverview(bonusId, style=style)
        return
