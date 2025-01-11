# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_tournament_completed.py
import logging
import typing
from frameworks.wulf import Array
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.backport.backport_pop_over import BackportPopOverContent, createPopOverData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.discount_bonus_model import DiscountBonusModel
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.new_year_bonus_packer import getChallengeBonusPacker, packBonusModelAndTooltipData, challengeQuestBonusSortOrder
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, nyCreateToolTipContentDecorator
from gui.server_events.bonuses import mergeBonuses
from gui.shared import event_dispatcher, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showStylePreview
from gui.shared.events import NySelectVehiclePopOver
from helpers import dependency, uniprof
from new_year.celebrity.celebrity_quests_helpers import getCelebrityMarathonQuests, getAllRewardsQuests
from new_year.ny_constants import SyncDataKeys, NYObjects
from new_year.ny_preview import getVehiclePreviewID
from new_year.variadic_discount import VARIADIC_DISCOUNT_NAME
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import NewYearChallengeModel
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.ny_challenge_completed_model import NyChallengeCompletedModel
_logger = logging.getLogger(__name__)

class NewYearChallengeTournamentCompleted(NyHistoryPresenter):
    __slots__ = ('_tooltips', '_remainingBonuses')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NewYearChallengeTournamentCompleted, self).__init__(viewModel, parentView, soundConfig)
        self._tooltips = {}
        self._remainingBonuses = []

    @property
    def viewModel(self):
        model = self.getViewModel()
        return model.completedModel

    @uniprof.regionDecorator(label='ny_challenge_tournament_completed', scope='enter')
    def initialize(self, *args, **kwargs):
        super(NewYearChallengeTournamentCompleted, self).initialize(self, *args, **kwargs)
        self.__fillModel()

    @uniprof.regionDecorator(label='ny_challenge_tournament_completed', scope='exit')
    def finalize(self):
        super(NewYearChallengeTournamentCompleted, self).finalize()

    def clear(self):
        self._tooltips.clear()
        super(NewYearChallengeTournamentCompleted, self).clear()

    def createPopOverContent(self, event):
        if event.contentID == R.views.common.pop_over_window.backport_pop_over.BackportPopOverContent():
            if event.getArgument('popoverId') == DiscountBonusModel.NEW_YEAR_DISCOUNT_APPLY_POPOVER_ID:
                alias = VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER
                variadicID = event.getArgument('variadicID')
                data = createPopOverData(alias, {'variadicID': variadicID,
                 'parentWindow': self.getParentWindow()})
                return BackportPopOverContent(popOverData=data)
        return super(NewYearChallengeTournamentCompleted, self).createPopOverContent(event)

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = int(event.getArgument('showCount', 0))
            return AdditionalRewardsTooltip(self._remainingBonuses[-showCount:], showCount)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NewYearChallengeTournamentCompleted, self).createToolTip(event)

    def _getListeners(self):
        listeners = super(NewYearChallengeTournamentCompleted, self)._getListeners()
        return listeners + ((NySelectVehiclePopOver.SHOW, self.__onPopoverOpened, EVENT_BUS_SCOPE.DEFAULT), (NySelectVehiclePopOver.HIDE, self.__onPopoverClosed, EVENT_BUS_SCOPE.DEFAULT))

    def _getEvents(self):
        events = super(NewYearChallengeTournamentCompleted, self)._getEvents()
        return events + ((self.viewModel.onStylePreview, self.__onShowStylePreview), (self._nyController.onDataUpdated, self.__onDataUpdated))

    def __fillModel(self):
        with self.viewModel.transaction() as tx:
            marathonQuests = getCelebrityMarathonQuests()
            if not marathonQuests:
                _logger.warning("Can't find marathon quests")
                return
            discountRewards = tx.getDiscountRewards()
            remainingRewards = tx.getRemainingRewards()
            discountRewards.clear()
            remainingRewards.clear()
            self._remainingBonuses[:] = []
            bonuses = []
            for quest in marathonQuests.values():
                bonuses.extend(quest.getBonuses())

            for q in getAllRewardsQuests().values():
                bonuses.extend(q.getBonuses())

            merged = mergeBonuses(bonuses)
            tempList = Array()
            packBonusModelAndTooltipData(merged, tempList, getChallengeBonusPacker(), self._tooltips, sortKey=challengeQuestBonusSortOrder)
            for item in tempList:
                if item.getName() == VARIADIC_DISCOUNT_NAME:
                    discountRewards.addViewModel(item)
                remainingRewards.addViewModel(item)
                self._remainingBonuses.append(item)

            remainingRewards.invalidate()
            discountRewards.invalidate()

    def __onCelebActionTokenUpdated(self, token):
        self.__fillModel()

    def __onDataUpdated(self, keys, _):
        if SyncDataKeys.SELECTED_DISCOUNTS in keys:
            self.__fillModel()

    def __onShowStylePreview(self, args):
        styleIntCD = int(args.get('intCD'))
        styleItem = self.__itemsCache.items.getItemByCD(styleIntCD)
        if styleItem is None:
            return
        else:

            def _backCallback():
                if not self._nyController.isEnabled():
                    event_dispatcher.showHangar()
                else:
                    NewYearNavigation.switchFromStyle(viewAlias=ViewAliases.CELEBRITY_VIEW, objectName=NYObjects.CHALLENGE, forceShowMainView=True)

            showStylePreview(getVehiclePreviewID(styleItem), styleItem, styleItem.getDescription(), backCallback=_backCallback)
            return

    def __onPopoverOpened(self, event):
        if event.ctx:
            self.viewModel.setDiscountPopoverId(event.ctx.get('discountID', ''))

    def __onPopoverClosed(self, event):
        self.viewModel.setDiscountPopoverId('')
