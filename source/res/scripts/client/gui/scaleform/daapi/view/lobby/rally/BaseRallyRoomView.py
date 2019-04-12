# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/BaseRallyRoomView.py
import account_helpers
from CurrentVehicle import g_currentVehicle
from UnitBase import UNIT_SLOT
from adisp import process
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.meta.BaseRallyRoomViewMeta import BaseRallyRoomViewMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.prb_control.entities.base.unit.ctx import AssignUnitCtx, CloseSlotUnitCtx, LockUnitCtx, KickPlayerUnitCtx, ChangeCommentUnitCtx, ChangeOpenedUnitCtx, SetRostersSlotsUnitCtx, SetVehicleUnitCtx, RosterSlotCtx
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers import i18n
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from messenger.proto.events import g_messengerEvents
from skeletons.gui.shared import IItemsCache

class BaseRallyRoomView(BaseRallyRoomViewMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(BaseRallyRoomView, self).__init__()
        self._candidatesDP = None
        return

    def requestToAssign(self, pID, slotIdx):
        self.sendRequest(AssignUnitCtx(pID, slotIdx, 'prebattle/assign'))

    def requestToUnassign(self, pID):
        self.sendRequest(AssignUnitCtx(pID, UNIT_SLOT.REMOVE, 'prebattle/assign'))

    def requestToCloseSlot(self, slotIdx):
        slotState = self.prbEntity.getSlotState(slotIdx)
        self.sendRequest(CloseSlotUnitCtx(slotIdx, not slotState.isClosed, 'prebattle/change_settings'))

    def requestToKickUser(self, databaseID):
        self.sendRequest(KickPlayerUnitCtx(databaseID, 'prebattle/kick'))

    def requestToLock(self, isLocked):
        self.sendRequest(LockUnitCtx(isLocked, 'prebattle/change_settings'))

    def requestToOpen(self, isOpened):
        self.sendRequest(ChangeOpenedUnitCtx(isOpened, 'prebattle/change_settings'))

    def requestToChangeComment(self, comment):
        self.sendRequest(ChangeCommentUnitCtx(comment, 'prebattle/change_settings'))

    def requestToUpdateRoster(self, data):
        c = SetRostersSlotsUnitCtx('prebattle/change_settings')
        for i in range(0, len(data)):
            c.addRosterSlot(i * 2, self.__getRosterSlotCtx(data[i][0]))
            c.addRosterSlot(i * 2 + 1, self.__getRosterSlotCtx(data[i][1]))

        self.sendRequest(c)

    @process
    def sendRequest(self, request):
        yield self.prbDispatcher.sendPrbRequest(request)

    def onUnitPlayersListChanged(self):
        if self._candidatesDP is not None:
            self._candidatesDP.rebuild(self.prbEntity.getCandidates())
        self._updateRallyData()
        return

    def onUnitPlayerInfoChanged(self, pInfo):
        if pInfo.isInSlot:
            self._updateMembersData()
        elif self._candidatesDP is not None:
            self._candidatesDP.rebuild(self.prbEntity.getCandidates())
        return

    def onUnitPlayerStateChanged(self, pInfo):
        self.__setMemberStatus(pInfo)
        if pInfo.isCurrentPlayer() or self.prbEntity.isCommander():
            self._setActionButtonState()

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        if pInfo.isCurrentPlayer():
            self._setActionButtonState()
        self._updateMembersData()

    def onUnitPlayerOnlineStatusChanged(self, pInfo):
        if pInfo.isInSlot:
            self.as_setMemberOfflineS(pInfo.slotIdx, pInfo.isOffline())
        elif self._candidatesDP is not None:
            self._candidatesDP.setOnline(pInfo)
        return

    def onUnitPlayerEnterOrLeaveArena(self, pInfo):
        self.__setMemberStatus(pInfo)

    def onUnitPlayerBecomeCreator(self, pInfo):
        self._updateRallyData()

    def onUnitRejoin(self):
        self._updateRallyData()
        self._setActionButtonState()

    def onUnitPlayerVehDictChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self._updateRallyData()
            self._setActionButtonState()

    def onUnitRosterChanged(self):
        self._updateMembersData()

    def onUnitCurfewChanged(self):
        LOG_DEBUG('%s : onUnitCurfewChanged' % self)
        self._setActionButtonState()

    def _updateRallyData(self):
        pass

    def setData(self, initialData):
        LOG_DEBUG('CyberSportUnitView.setItemId passed team id is:', initialData)

    def getCoolDownRequests(self):
        return [REQUEST_TYPE.SET_PLAYER_STATE, REQUEST_TYPE.CHANGE_UNIT_STATE]

    def initCandidatesDP(self):
        pass

    def rebuildCandidatesDP(self):
        pass

    def _setActionButtonState(self):
        pass

    def startListening(self):
        g_currentVehicle.onChanged += self.__handleCurrentVehicleChanged

    def stopListening(self):
        g_currentVehicle.onChanged -= self.__handleCurrentVehicleChanged

    def _populate(self):
        super(BaseRallyRoomView, self)._populate()
        self.initCandidatesDP()
        self.startListening()
        self.addListener(events.CSVehicleSelectEvent.VEHICLE_SELECTED, self.__onVehicleSelectHandler)
        self._updateRallyData()
        self._setActionButtonState()
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived += self._onUsersReceived
        usersEvents.onUserActionReceived += self._onUserActionReceived

    def _dispose(self):
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived -= self._onUsersReceived
        usersEvents.onUserActionReceived -= self._onUserActionReceived
        self._closeSendInvitesWindow()
        HideEvent = events.HideWindowEvent
        self.fireEvent(HideEvent(HideEvent.HIDE_VEHICLE_SELECTOR_WINDOW))
        if self._candidatesDP is not None:
            self._candidatesDP.fini()
            self._candidatesDP = None
        self.stopListening()
        self.removeListener(events.CSVehicleSelectEvent.VEHICLE_SELECTED, self.__onVehicleSelectHandler)
        super(BaseRallyRoomView, self)._dispose()
        return

    def assignSlotRequest(self, slotIndex, playerId):
        if playerId == -1:
            if self.prbEntity.isCommander():
                LOG_DEBUG('Request to assign is ignored. Creator can not move to another slots')
                return
            playerId = account_helpers.getAccountDatabaseID()
        elif not self.isPlayerInUnit(playerId):
            return
        self.requestToAssign(playerId, slotIndex)

    def leaveSlotRequest(self, playerId):
        if self.isPlayerInSlot(playerId):
            self.requestToUnassign(playerId)

    def _chooseVehicleRequest(self, levelsRange):
        playerInfo = self.prbEntity.getPlayerInfo()
        slotIdx = playerInfo.slotIdx
        vehicles = playerInfo.getSlotsToVehicles(True).get(slotIdx)
        if vehicles is not None:
            vehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(vehicles))
        self.fireEvent(events.LoadViewEvent(CYBER_SPORT_ALIASES.VEHICLE_SELECTOR_POPUP_PY, ctx={'isMultiSelect': False,
         'vehicles': vehicles,
         'titleText': CYBERSPORT.WINDOW_VEHICLESELECTOR_TITLE,
         'selectButton': CYBERSPORT.WINDOW_VEHICLESELECTOR_BUTTONS_SELECT,
         'cancelButton': CYBERSPORT.WINDOW_VEHICLESELECTOR_BUTTONS_CANCEL,
         'infoText': self._getVehicleSelectorDescription(),
         'compatibleOnlyLabel': CYBERSPORT.WINDOW_VEHICLESELECTOR_FILTERS_MATCHES,
         'selectedVehicles': self._getVehicleSelectorVehicles(),
         'section': 'cs_unit_view_vehicle',
         'levelsRange': levelsRange}), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def chooseVehicleRequest(self):
        levelsRange = self.prbEntity.getRosterSettings().getLevelsRange()
        self._chooseVehicleRequest(levelsRange)

    def inviteFriendRequest(self):
        self.fireEvent(events.LoadViewEvent(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, ctx={'prbName': 'unit',
         'ctrlType': CTRL_ENTITY_TYPE.UNIT}), scope=EVENT_BUS_SCOPE.LOBBY)

    def toggleReadyStateRequest(self):
        self.prbEntity.doAction()

    def ignoreUserRequest(self, databaseID):
        playerInfo = self.prbEntity.getPlayerInfo()
        if playerInfo.isCommander():
            self.requestToKickUser(databaseID)

    def onSlotsHighlihgtingNeed(self, databaseID):
        availableSlots = self.getAvailableSlots(databaseID)
        self.as_highlightSlotsS(availableSlots)
        return availableSlots

    def getAvailableSlots(self, databaseID):
        availableSlots = list(self.prbEntity.getPlayerInfo(databaseID).getAvailableSlots(True))
        return availableSlots

    def editDescriptionRequest(self, description):
        LOG_DEBUG('EDIT DESCRIPTION: ', description)
        self.requestToChangeComment(description)

    def showFAQWindow(self):
        self.fireEvent(events.LoadViewEvent(MESSENGER_VIEW_ALIAS.FAQ_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onVehicleSelectHandler(self, event):
        self._selectVehicles(event.ctx)

    def _selectVehicles(self, items):
        if items:
            self.sendRequest(SetVehicleUnitCtx(vTypeCD=items[0], waitingID='prebattle/change_settings'))

    def _onUserActionReceived(self, _, user):
        self._updateRallyData()
        if self._candidatesDP is not None and self._candidatesDP.hasCandidate(user.getID()):
            self.rebuildCandidatesDP()
        return

    def _onUsersReceived(self, _):
        if self.prbEntity is not None:
            self._updateRallyData()
        return

    def _updateVehiclesLabel(self, minVal, maxVal):
        vehicleLvl = text_styles.main(i18n.makeString(CYBERSPORT.WINDOW_UNIT_RANGEVALUE, minVal=minVal, maxVal=maxVal))
        vehicleLbl = text_styles.standard(i18n.makeString(CYBERSPORT.WINDOW_UNIT_TEAMVEHICLESLBL, levelsRange=vehicleLvl))
        self.as_setVehiclesTitleS(vehicleLbl, {})

    def _closeSendInvitesWindow(self):
        self._destroyRelatedView(ViewTypes.WINDOW, PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY)

    def _destroyRelatedView(self, container, alias):
        container = self.app.containerManager.getContainer(container)
        if container is not None:
            view = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: alias})
            if view is not None:
                view.destroy()
        return

    def isPlayerInUnit(self, databaseID):
        result = False
        players = self.prbEntity.getPlayers()
        for dbId, _ in players.iteritems():
            if dbId == databaseID:
                result = True
                break

        return result

    def isPlayerInSlot(self, databaseID=None):
        pInfo = self.prbEntity.getPlayerInfo(dbID=databaseID)
        return pInfo.isInSlot

    def _getVehicleSelectorDescription(self):
        pass

    def _getVehicleSelectorVehicles(self):
        selected = []
        for vInfo in self.prbEntity.getVehiclesInfo():
            if not vInfo.isEmpty():
                selected.append(vInfo.vehTypeCD)

        return selected

    def __getRosterSlotCtx(self, item):
        if item is None:
            return RosterSlotCtx()
        elif item.selectedVehicle > 0:
            return RosterSlotCtx(item.selectedVehicle)
        else:
            settings = self.prbEntity.getRosterSettings()
            levels = (settings.getMinLevel(), settings.getMaxLevel())
            if len(item.vLevelRange) == 2:
                i0 = int(item.vLevelRange[0])
                i1 = int(item.vLevelRange[1])
                levels = (i0, i1) if i0 != i1 else i0
            elif len(item.vLevelRange) == 1:
                levels = int(item.vLevelRange[0])
            return RosterSlotCtx(nationNames=item.nationIDRange, levels=levels, vehClassNames=item.vTypeRange)
            return

    def __setMemberStatus(self, pInfo):
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            slotState = self.prbEntity.getSlotState(slotIdx)
            self.as_setMemberStatusS(slotIdx, vo_converters.getPlayerStatus(slotState, pInfo))

    def _updateMembersData(self):
        entity = self.prbEntity
        self.as_setMembersS(*vo_converters.makeSlotsVOs(entity, entity.getID()))
        self._setActionButtonState()

    def __handleCurrentVehicleChanged(self):
        self._setActionButtonState()
