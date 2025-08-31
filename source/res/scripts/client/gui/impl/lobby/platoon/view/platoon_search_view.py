# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/view/platoon_search_view.py
import logging
import time
from gui.prb_control import prb_getters
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.game_control import IPlatoonController
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.platoon.searching_dropdown_model import SearchingDropdownModel
from gui.impl.lobby.platoon.view.subview.platoon_tiers_limit_subview import TiersLimitSubview
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl import backport
from gui.shared import g_eventBus
from gui.shared.events import PlatoonDropdownEvent
from gui.impl.lobby.premacc.squad_bonus_tooltip_content import SquadBonusTooltipContent
from gui.impl.lobby.platoon.platoon_helpers import formatSearchEstimatedTime, getQueueInfoByQueueType, Position
from PlayerEvents import g_playerEvents
from UnitBase import UNDEFINED_ESTIMATED_TIME
from frameworks.wulf.gui_constants import ViewStatus, WindowLayer
from gui.impl.lobby.platoon.platoon_helpers import PreloadableWindow
from constants import QUEUE_TYPE
_logger = logging.getLogger(__name__)

class SearchView(ViewImpl, CallbackDelayer):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    _layoutID = R.views.lobby.platoon.SearchingDropdown()
    QUEUE_INFO_UPDATE_TIME = 5
    searchTimestamp = 0

    def __init__(self):
        settings = ViewSettings(layoutID=self._layoutID, model=SearchingDropdownModel())
        self.__tiersLimitSubview = TiersLimitSubview()
        self.__prbEntityType = self.__platoonCtrl.getPrbEntityType()
        super(SearchView, self).__init__(settings)

    def getPrbEntityType(self):
        return self.__prbEntityType

    @staticmethod
    def resetState():
        SearchView.searchTimestamp = time.time()

    def _finalize(self):
        self.__removeListeners()
        self.clearCallbacks()

    def _onLoading(self, *args, **kwargs):
        self.__addListeners()
        self.setChildView(self.__tiersLimitSubview.layoutID, self.__tiersLimitSubview)
        self.delayCallback(0, self.__askForPlayerQueueInfo)
        self.__initButtons()
        with self.viewModel.transaction() as model:
            model.setSearchStartTime(SearchView.searchTimestamp)
        self.__updateEstimatedTime()
        self._setBackgroundImage()

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return SquadBonusTooltipContent() if contentID == R.views.lobby.premacc.squad_bonus_tooltip_content.SquadBonusTooltipContent() else super(SearchView, self).createToolTipContent(event=event, contentID=contentID)

    def __addListeners(self):
        with self.viewModel.transaction() as model:
            model.btnCancelSearch.onClick += self.__cancelSearch
            model.onOutsideClick += self.__onOutsideClick
        g_playerEvents.onQueueInfoReceived += self.__onQueueInfoReceived
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onUnitEstimateInQueueChanged += self.__updateEstimatedTime

    def __removeListeners(self):
        with self.viewModel.transaction() as model:
            model.btnCancelSearch.onClick -= self.__cancelSearch
            model.onOutsideClick -= self.__onOutsideClick
        g_playerEvents.onQueueInfoReceived -= self.__onQueueInfoReceived
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onUnitEstimateInQueueChanged -= self.__updateEstimatedTime

    def __onOutsideClick(self):
        if not self.getParentWindow().isHidden():
            g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': False}))

    def __initButtons(self):
        with self.viewModel.transaction() as model:
            model.btnCancelSearch.setCaption(backport.text(R.strings.platoon.buttons.cancelSearch.caption()))
            model.btnCancelSearch.setDescription(backport.text(R.strings.platoon.buttons.cancelSearch.description()))

    def __askForPlayerQueueInfo(self):
        self.__platoonCtrl.requestPlayerQueueInfo()
        return self.QUEUE_INFO_UPDATE_TIME

    def __cancelSearch(self):
        self.__platoonCtrl.cancelSearch()
        self.__platoonCtrl.leavePlatoon(ignoreConfirmation=True)

    def __onQueueInfoReceived(self, queueInfo):
        actualQueueInfo = getQueueInfoByQueueType(queueInfo, self.__platoonCtrl.getQueueType())
        numInQueue = actualQueueInfo['numInQueue']
        with self.viewModel.transaction() as model:
            model.setSeekers(numInQueue)

    def __updateEstimatedTime(self):
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            estimatedTime = unitMgr.unit.getEstimatedTimeInQueue()
            if estimatedTime != UNDEFINED_ESTIMATED_TIME:
                with self.viewModel.transaction() as model:
                    model.setEstimatedTime(formatSearchEstimatedTime(estimatedTime))

    def _setBackgroundImage(self):
        queueType = self.__platoonCtrl.getQueueType()
        backgrounds = R.images.gui.maps.icons.platoon.dropdown_backgrounds
        background = backgrounds.squad()
        with self.viewModel.transaction() as model:
            if queueType == QUEUE_TYPE.EVENT_BATTLES:
                background = backgrounds.event()
            elif queueType == QUEUE_TYPE.EPIC:
                background = backgrounds.epic()
            elif queueType == QUEUE_TYPE.BATTLE_ROYALE:
                background = backgrounds.battle_royale()
        model.setBackgroundImage(backport.image(background))


class SearchWindow(PreloadableWindow):
    previousPosition = None

    def __init__(self, initialPosition=None):
        super(SearchWindow, self).__init__(wndFlags=WindowFlags.POP_OVER, content=SearchView(), layer=WindowLayer.WINDOW)
        if initialPosition:
            SearchWindow.previousPosition = initialPosition
        if SearchWindow.previousPosition:
            self.move(SearchWindow.previousPosition.x, SearchWindow.previousPosition.y)

    def _finalize(self):
        if self.content.viewStatus > ViewStatus.LOADING:
            SearchWindow.previousPosition = Position(self.position[0], self.position[1])
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': False}))

    def _onContentReady(self):
        if not self.isPreloading():
            g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': True}))
        super(SearchWindow, self)._onContentReady()

    def show(self, focus=True):
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': True}))
        super(SearchWindow, self).show(focus)

    def hide(self, destroy=False):
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': False}))
        super(SearchWindow, self).hide(destroy)
