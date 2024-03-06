# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/player_subscriptions/player_subscriptions_reward_window_view.py
import logging
import typing
from constants import OFFER_TOKEN_PREFIX
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.player_subscriptions.main_reward_model import MainRewardModel
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub import ViewImpl
from gui.server_events.bonuses import getTutorialBonuses, splitBonuses
from gui.shared.event_dispatcher import showOfferGiftsWindow
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, TokenBonusUIPacker
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.offers import IOffersDataProvider
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.player_subscriptions.subscription_reward_view_model import SubscriptionRewardViewModel
    from gui.shared.missions.packers.bonus import BaseBonusUIPacker
    from frameworks.wulf import Array
_logger = logging.getLogger(__name__)
BASE_EVENT_NAME = 'base'
MAIN_REWARD_PREFIX = 'mainReward_'

class PlayerSubscriptionRewardWindowView(ViewImpl):
    _offersProvider = dependency.descriptor(IOffersDataProvider)
    _BONUSES_ORDER = ('dossier',
     'customizations',
     'premium_plus',
     Currency.GOLD,
     'vehicles',
     'items',
     'crewBooks')

    def __init__(self, settings, ctx=None):
        super(PlayerSubscriptionRewardWindowView, self).__init__(settings, ctx)
        if ctx is not None:
            self._eventName = ctx.get('eventName', BASE_EVENT_NAME)
            self._quest = ctx.get('quest', None)
            self._vehicles = ctx.get('bonusVehicles', {})
        else:
            self._quest = None
            self._vehicles = {}
        self._tooltips = {}
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = int(event.getArgument('tooltipId'))
            window = BackportTooltipWindow(self._tooltips[tooltipId], self.getParentWindow()) if tooltipId is not None and tooltipId in self._tooltips else None
            if window is not None:
                window.load()
            return window
        elif event.contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = event.getArgument('showCount')
            if showCount is None:
                return
            packedBonuses = self.viewModel.getRewards()[int(showCount):]
            window = DecoratedTooltipWindow(AdditionalRewardsTooltip(packedBonuses), useDecorator=False)
            window.load()
            window.move(event.mouse.positionX, event.mouse.positionY)
            return window
        else:
            return super(PlayerSubscriptionRewardWindowView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(PlayerSubscriptionRewardWindowView, self)._initialize(*args, **kwargs)
        self._setTitles()
        self._setMainRewards()
        self._initRewardsList()

    def _setTitles(self):
        res = R.strings.ingame_gui.rewardWindow.dyn(self._eventName, None)
        if res:
            title = backport.text(res.dyn('headerText')())
            desc = backport.text(res.dyn('descText')())
            self.viewModel.setSubscriptionTitle(title)
            self.viewModel.setDescText(desc)
            offer = self.__getOffer()
            self.viewModel.setHasSelectiveRewards(offer is not None)
        return

    def _setMainRewards(self):
        stringResources = R.strings.ingame_gui.rewardWindow.dyn(self._eventName, None)
        index = 1
        with self.viewModel.transaction() as tx:
            mainRewardsModel = tx.getMainRewards()
            while True:
                imgName = ''.join((self._eventName,
                 '_',
                 MAIN_REWARD_PREFIX,
                 str(index)))
                descr = stringResources.dyn(MAIN_REWARD_PREFIX + str(index))
                if descr:
                    model = MainRewardModel()
                    model.setImage(imgName)
                    model.setDescription(backport.text(descr()))
                    mainRewardsModel.addViewModel(model)
                    index += 1
                break

        return

    def _getEvents(self):
        return ((self.viewModel.onCloseButtonClick, self.__onCloseButtonClick), (self.viewModel.onChooseButtonClick, self.__onChoseButtonClick))

    def _initRewardsList(self):
        with self.getViewModel().transaction() as tx:
            rewardsList = tx.getRewards()
            bonuses = self._getBonuses()
            packerMap = self.__getPackerMap()
            for index, bonus in enumerate(bonuses):
                packer = packerMap.get(bonus.getName())
                if packer:
                    tooltipsData = packer.getToolTip(bonus)
                    for bonusIdx, bonusModel in enumerate(packer.pack(bonus)):
                        bonusModel.setTooltipId(str(index))
                        tooltip = tooltipsData[bonusIdx]
                        rewardsList.addViewModel(bonusModel)
                        self._tooltips[index] = tooltip

    def _getBonuses(self):
        if self._quest is not None:
            allBonuses = getMissionInfoData(self._quest).getSubstituteBonuses()
            bonuses = [ bonus for bonus in allBonuses if bonus.getName() != 'vehicles' ]
            vehBonus = getTutorialBonuses('vehicles', self._vehicles)
            bonuses.extend(vehBonus)
            bonuses = splitBonuses(bonuses)
            bonuses.sort(key=self.__keySortOrder)
            return bonuses
        else:
            return []

    def __onCloseButtonClick(self):
        self.destroyWindow()

    def __onChoseButtonClick(self):
        offer = self.__getOffer()
        if offer:
            showOfferGiftsWindow(offer.id)
        else:
            self.destroyWindow()

    def __getOffer(self):
        bonuses = self._quest.getBonuses('tokens')
        for bonus in bonuses:
            for tID in bonus.getTokens():
                if tID.startswith(OFFER_TOKEN_PREFIX):
                    for offer in self._offersProvider.getUnlockedOffers(onlyVisible=True):
                        if offer.token == tID:
                            return offer

        return None

    def __keySortOrder(self, bonus):
        return self._BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in self._BONUSES_ORDER else len(self._BONUSES_ORDER)

    def __getPackerMap(self):
        packer = getDefaultBonusPackersMap()
        packer['tokens'] = PSTokenBonusUIPacker()
        packer['tmanToken'] = TmanTemplateBonusPacker()
        return packer


class PSTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setValue(str(bonus.getCount()))
        model.setName('bonus_battle_task')
        return model
