# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/platoon_presenter.py
from __future__ import absolute_import
import json
import typing as t
import BigWorld
from constants import PREBATTLE_TYPE, SquadManStates, EPlatoonButtonState, QUEUE_TYPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.game_control.platoon_controller import PopoverParams
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.page.footer.platoon_member_model import PlatoonMemberModel
from gui.impl.gen.view_models.views.lobby.page.footer.platoon_model import PlatoonModel
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control import prb_getters
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IPlatoonController, IBattleRoyaleController, IHangarGuiController
if t.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent, Window
    from gui.impl.lobby.platoon.platoon_config import SquadInfo

class PlatoonPresenter(ViewComponent[PlatoonModel], IGlobalListener):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __appLoader = dependency.descriptor(IAppLoader)
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)

    def __init__(self):
        super(PlatoonPresenter, self).__init__(model=PlatoonModel)
        self.app = None
        return

    @property
    def viewModel(self):
        return super(PlatoonPresenter, self).getViewModel()

    def createPopOver(self, event):
        if event.contentID == R.aliases.common.popOver.Backport():
            if event.getArgument('popoverId') == VIEW_ALIAS.SQUAD_TYPE_SELECT_POPOVER:
                self.__platoonCtrl.setPopoverParams(PopoverParams(event.bbox, event.direction))
                if self.prbDispatcher:
                    return self.__platoonCtrl.evaluateVisibility(toggleUI=event.isOn)
                return None
        return super(PlatoonPresenter, self).createPopOver(event)

    def onPrbEntitySwitched(self):
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onSquadSizeChanged += self._onUpdatePlatoon
        self._onUpdatePlatoon()

    def onEnqueued(self, *args, **kwargs):
        self._onUpdatePlatoon()

    def onDequeued(self, *args, **kwargs):
        self._onUpdatePlatoon()

    def onEnqueueError(self, *args, **kwargs):
        self._onUpdatePlatoon()

    def onArenaJoinFailure(self, *args, **kwargs):
        self._onUpdatePlatoon()

    def onKickedFromQueue(self, *args, **kwargs):
        self._onUpdatePlatoon()

    def onKickedFromArena(self, *args, **kwargs):
        self._onUpdatePlatoon()

    def _initialize(self, *args, **kwargs):
        self.startGlobalListening()
        super(PlatoonPresenter, self)._initialize(args, kwargs)

    def _finalize(self):
        self.stopGlobalListening()
        self.app = None
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr and unitMgr.unit:
            unitMgr.unit.onSquadSizeChanged -= self._onUpdatePlatoon
        super(PlatoonPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((self.__platoonCtrl.onMembersUpdate, self._onUpdatePlatoon), (self.viewModel.onInPlatoonAction, self._onInPlatoonAction))

    def _getListeners(self):
        return ((events.LobbyHeaderMenuEvent.UPDATE_PREBATTLE_CONTROLS, self.__onUpdatePrbControls, EVENT_BUS_SCOPE.LOBBY),)

    def _onLoading(self, *args, **kwargs):
        self._onUpdatePlatoon()
        self.app = self.__appLoader.getApp()
        super(PlatoonPresenter, self)._onLoading()

    def _onInPlatoonAction(self):
        if self.prbDispatcher:
            self.__platoonCtrl.evaluateVisibility(toggleUI=True)

    def __onUpdatePrbControls(self, *_):
        self._onUpdatePlatoon()

    def _onUpdatePlatoon(self):
        isSquadControlEnabled = self.__battleRoyaleController.isSquadButtonEnabled()
        self.setEnabled(isSquadControlEnabled)
        if not isSquadControlEnabled:
            return
        pFuncState = self.prbDispatcher.getFunctionalState()
        isInSquad = any((pFuncState.isInUnit(prbType) for prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES))
        isSquadEnabled = isInSquad or self.__platoonCtrl.getPermissions().canCreateSquad()
        extendedSquadInfoVo = self.__platoonCtrl.buildExtendedSquadInfoVo()
        isInQueue = self.prbEntity.isInQueue()
        header, body, params = self.__getTooltip(extendedSquadInfoVo, isInSquad)
        self.viewModel.setTooltipHeader(header)
        self.viewModel.setTooltipBody(body)
        self.viewModel.setTooltipParams(json.dumps(params))
        if not isSquadEnabled or isInQueue and not isInSquad or self.__isNotAllowedQueueType():
            self.viewModel.setState(self.viewModel.DISABLED)
            return
        self.viewModel.setCommanderIndex(extendedSquadInfoVo.commanderIndex)
        self.viewModel.setPlayerIndex(self.__getPlayerIndex())
        self.viewModel.setState(extendedSquadInfoVo.platoonState)
        members = self.viewModel.getMembers()
        members.clear()
        for state in extendedSquadInfoVo.squadManStates:
            member = PlatoonMemberModel()
            member.setState(state if state != SquadManStates.NOT_READY_PLAYER.value else member.NOT_READY)
            members.addViewModel(member)

        members.invalidate()

    def __getTooltip(self, extendedSquadInfoVo, isInSquad):
        controlsHelper = self.__hangarGuiCtrl.getLobbyHeaderHelper()
        params = {}
        if extendedSquadInfoVo.platoonState == EPlatoonButtonState.SEARCHING_STATE.value:
            searching = R.strings.platoon.headerButton.tooltips.searching
            header = searching.header()
            body = searching.body()
        elif controlsHelper is not None:
            pValidation = self.prbEntity.canPlayerDoAction()
            header, body, params = controlsHelper.getSquadControlTooltipData(pValidation, isInSquad)
        else:
            headerTooltips = R.strings.platoon.headerButton.tooltips
            squadTooltip = headerTooltips.inSquad if isInSquad else headerTooltips.squad
            header = squadTooltip.header()
            body = squadTooltip.body()
        return (header, body, params)

    def __getPlayerIndex(self):
        slotsData = self.__platoonCtrl.getPlatoonSlotsData()
        accID = BigWorld.player().id
        for idx, it in enumerate(slotsData):
            player = it['player']
            if player is not None and player['accID'] == accID:
                return idx

        return -1

    def __isNotAllowedQueueType(self):
        return self.prbEntity.getQueueType() in (QUEUE_TYPE.SPEC_BATTLE,)
