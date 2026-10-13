# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/mode_selector/portal_mode_selector_item.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem, formatSeasonLeftTime
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, time_utils
from portal.gui.shared.event_dispatcher import showPortalInfoPage
from portal.skeletons.portal_event_controller import IPortalEventController
import typing
from portal_account_settings import getEventEntrypointIsNew, setEventEntrypointIsNew
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_portal_model import ModeSelectorPortalModel
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class PortalModeSelectorRewardID(Enum):
    PORTAL_STYLE = 'portal_style'
    PORTAL_MEDAL = 'portal_medal'


class PortalModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    __portalController = dependency.descriptor(IPortalEventController)
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.PORTAL
    _VIEW_MODEL = ModeSelectorPortalModel

    def _onInitializing(self):
        super(PortalModeSelectorItem, self)._onInitializing()
        self.__fillViewModel()
        self.__addListeners()

    def _onDisposing(self):
        self.__removeListeners()
        super(PortalModeSelectorItem, self)._onDisposing()

    def __addListeners(self):
        self.__portalController.onPrimeTimeStatusUpdated += self.__onUpdated
        self.__portalController.onPortalBattleConfigChanged += self.__onUpdated

    def __removeListeners(self):
        self.__portalController.onPortalBattleConfigChanged -= self.__onUpdated
        self.__portalController.onPrimeTimeStatusUpdated -= self.__onUpdated

    def __onUpdated(self, *_):
        if not self.__portalController.isEnabled():
            self.onCardChange()
            return
        self.__fillViewModel()

    def handleClick(self):
        setEventEntrypointIsNew(False)
        super(PortalModeSelectorItem, self).handleClick()

    def handleInfoPageClick(self):
        showPortalInfoPage()
        super(PortalModeSelectorItem, self).handleInfoPageClick()

    def __fillViewModel(self):
        with self.viewModel.transaction() as vm:
            portalStrings = R.strings.mode_selector.portal
            vm.widget.setIsEnabled(self.__portalController.isEnabled())
            vm.widget.setPerformance(self.__portalController.getPerformanceGroup())
            isNew = getEventEntrypointIsNew()
            vm.setIsNew(isNew)
            vm.setName(backport.text(portalStrings.title()))
            vm.setEventName(backport.text(portalStrings.title()))
            vm.setStatusActive(backport.text(portalStrings.statusActive()))
            vm.setDescription(backport.text(portalStrings.description()))
            vm.setConditions(backport.text(portalStrings.conditions()))
            vm.setTimeLeft(formatSeasonLeftTime(self.__portalController.getCurrentSeason()))
            self.__fillRewardList(vm.getRewardList())

    def __fillRewardList(self, rewardList):
        rewardList.clear()
        self._addReward(PortalModeSelectorRewardID.PORTAL_MEDAL)
        self._addReward(PortalModeSelectorRewardID.PORTAL_STYLE)

    def __getCurrentSeasonDates(self):
        currentSeason = self.__portalController.getCurrentSeason()
        return (self.__getDate(currentSeason.getStartDate()), self.__getDate(currentSeason.getEndDate())) if currentSeason is not None else ''

    def __getDate(self, date):
        timeStamp = time_utils.makeLocalServerTime(date)
        return backport.getShortDateFormat(timeStamp)

    @property
    def calendarTooltipText(self):
        start, end = self.__getCurrentSeasonDates()
        return backport.text(R.strings.mode_selector.portal.tooltip.body(), start=start, end=end)
