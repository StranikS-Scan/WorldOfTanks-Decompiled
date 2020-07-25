# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/stronghold_battle_room.py
import weakref
from UnitBase import UNIT_OP
from adisp import process
from constants import PREBATTLE_TYPE_NAMES, PREBATTLE_TYPE
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.MinimapGrid import MinimapGrid
from gui.Scaleform.daapi.view.lobby.MinimapLobby import MinimapLobby
from gui.Scaleform.daapi.view.lobby.fortifications.vo_converters import FILTER_STATE, makeStrongholdsSlotsVOs, makeSortieVO
from gui.Scaleform.daapi.view.lobby.prb_windows.stronghold_action_button_state_vo import StrongholdActionButtonStateVO
from gui.Scaleform.daapi.view.lobby.rally import rally_dps
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.lobby.strongholds.sound_controller import g_strongholdSoundController
from gui.Scaleform.daapi.view.lobby.strongholds.web_handlers import createStrongholdsWebHandlers
from gui.Scaleform.daapi.view.meta.FortClanBattleRoomMeta import FortClanBattleRoomMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.clans.clan_helpers import getStrongholdChangeModeUrl
from gui.impl import backport
from gui.prb_control import settings
from gui.prb_control.entities.base.unit.listener import IStrongholdListener
from gui.prb_control.entities.base.unit.listener import IUnitListener
from gui.prb_control.entities.stronghold.unit.ctx import SetReserveUnitCtx, UnsetReserveUnitCtx
from gui.prb_control.entities.base.external_battle_unit.base_external_battle_ctx import ChangeVehTypesInSlotFilterCtx, ChangeVehiclesInSlotFilterCtx
from gui.prb_control.items.stronghold_items import REQUISITION_TYPE
from gui.prb_control.settings import CTRL_ENTITY_TYPE, FUNCTIONAL_FLAG
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils.functions import getViewName, makeTooltip
from gui.shared.view_helpers import UsersInfoHelper
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency, i18n
from helpers import int2roman
from helpers import time_utils
from messenger.ext import channel_num_gen
from messenger.gui import events_dispatcher
from messenger.proto.events import g_messengerEvents
from nation_change.nation_change_helpers import iterVehTypeCDsInNationGroup, hasNationGroup
from shared_utils import CONST_CONTAINER
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBrowserController
from skeletons.gui.shared import IItemsCache
from gui import makeHtmlString

class StrongholdBattleRoom(FortClanBattleRoomMeta, IUnitListener, IStrongholdListener, UsersInfoHelper):
    browserCtrl = dependency.descriptor(IBrowserController)
    itemsCache = dependency.descriptor(IItemsCache)
    appLoader = dependency.descriptor(IAppLoader)

    class TIMER_GLOW_COLORS(CONST_CONTAINER):
        NORMAL = int('BB6200', 16)
        ALERT = int('BB2B00', 16)

    def __init__(self):
        super(StrongholdBattleRoom, self).__init__()
        self.__minimap = None
        self.__minimapGrid = None
        self.__isOpened = False
        self.__proxy = None
        self.__changeModeBrowserId = 0
        self.__firstShowMainForm = False
        self.__maintenanceWindowVisible = False
        self.__enemyReadyIndicator = False
        self.__vehTypesInSlotFilters = {}
        self.__vehiclesInSlotFilters = {}
        return

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.__setReadyStatus()
        self._setActionButtonState()
        if self.prbEntity.isStrongholdSettingsValid():
            self._updateConfigureButtonState(self.prbEntity.isFirstBattle(), not self.prbEntity.isStrongholdUnitFreezed())
            if flags.isExternalLegionariesMatchingChanged() and not flags.isInExternalLegionariesMatching() and not flags.isFreezed():
                strongholdSettings = self.prbEntity.getStrongholdSettings()
                self._updateReserves(strongholdSettings.getReserve(), strongholdSettings.getReserveOrder())
            self._updateMembersData()
            self._updateRallyData()

    def onUnitPlayerStateChanged(self, pInfo):
        self.__setMemberStatus(pInfo)
        if pInfo.isCurrentPlayer() or self.prbEntity.isCommander():
            self._setActionButtonState()
        self._updateRallyData()

    def onTimerAlert(self):
        g_strongholdSoundController.playBattleRoomTimerAlert()

    def isPlayerInUnit(self, databaseID):
        result = False
        players = self.prbEntity.getPlayers()
        for dbId, playerInfo in players.iteritems():
            if dbId == databaseID and not playerInfo.isInvite():
                result = True
                break

        return result

    def onUnitSettingChanged(self, opCode, value):
        if opCode == UNIT_OP.SET_COMMENT:
            self.as_setCommentS(self.prbEntity.getCensoredComment())
        elif opCode in [UNIT_OP.CLOSE_SLOT, UNIT_OP.OPEN_SLOT]:
            self._setActionButtonState()

    def onUnitVehiclesChanged(self, dbID, vInfos):
        pInfo = self.prbEntity.getPlayerInfo(dbID=dbID)
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            if vInfos and not vInfos[0].isEmpty():
                vInfo = vInfos[0]
                vehicleVO = vo_converters.makeVehicleVO(self.itemsCache.items.getItemByCD(vInfo.vehTypeCD), self.prbEntity.getRosterSettings().getLevelsRange(), isCurrentPlayer=pInfo.isCurrentPlayer())
                slotCost = vInfo.vehLevel
            else:
                slotState = self.prbEntity.getSlotState(slotIdx)
                vehicleVO = None
                if slotState.isClosed:
                    slotCost = settings.UNIT_CLOSED_SLOT_COST
                else:
                    slotCost = 0
            self.as_setMemberVehicleS(slotIdx, slotCost, vehicleVO)
        if pInfo.isCurrentPlayer() or pInfo.isCommander():
            self._setActionButtonState()
        return

    def onUnitPlayersListChanged(self):
        self._rebuildCandidatesDP()
        self._updateRallyData()

    def onStrongholdOnReadyStateChanged(self):
        if self._candidatesDP:
            self._rebuildCandidatesDP()
            self._updateMembersData()
            self._updateRallyData()

    def onUnitMembersListChanged(self):
        self._rebuildCandidatesDP()
        self._updateMembersData()
        self._updateRallyData()

    def onUnitRejoin(self):
        super(StrongholdBattleRoom, self).onUnitRejoin()
        self._rebuildCandidatesDP()
        self._updateMembersData()
        self._updateRallyData()

    def initCandidatesDP(self):
        self._candidatesDP = rally_dps.SortieCandidatesLegionariesDP()
        self._candidatesDP.init(self.app, self.as_getCandidatesDPS(), self.prbEntity.getCandidates())

    def inviteFriendRequest(self):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.STRONGHOLD_SEND_INVITES_WINDOW_PY, ctx={'prbName': PREBATTLE_TYPE_NAMES[PREBATTLE_TYPE.STRONGHOLD],
         'ctrlType': CTRL_ENTITY_TYPE.UNIT,
         'showClanOnly': False}), scope=EVENT_BUS_SCOPE.LOBBY)

    def toggleRoomStatus(self):
        self.requestToOpen(not self.__isOpened)

    def chooseVehicleRequest(self):
        self._chooseVehicleRequest(self.prbEntity.getRosterSettings().getLevelsRange())

    @process
    def openConfigureWindow(self):
        url = getStrongholdChangeModeUrl()
        title = i18n.makeString(TOOLTIPS.CYBERSPORT_MODECHANGEFROZEN_HEADER)
        windowSize = GUI_SETTINGS.lookup('StrongholdsPopupWebWindowSize')
        browserSize = (windowSize.get('width', 800), windowSize.get('height', 600))
        self.__changeModeBrowserId = yield self.browserCtrl.load(url=url, title=title, browserSize=browserSize, isModal=True, showCreateWaiting=True, handlers=createStrongholdsWebHandlers(), showActionBtn=False)
        browser = self.browserCtrl.getBrowser(self.__changeModeBrowserId)
        if browser:
            browser.ignoreKeyEvents = True
        else:
            self.__changeModeBrowserId = 0

    def onUpdateHeader(self, header, isFirstBattle, isUnitFreezed):
        self._updateMiniMapData(header.getCurrentBattle(), header.getClan())
        self._updateTableHeader(header.getMaxPlayersCount(), header.getMaxLegionariesCount())
        self._updateBuildings(header.getCurrentBattle(), header.getEnemyClan(), header.getBattleIdx())
        self._updateTitle(header.isSortie(), header.getDirection(), header.getIndustrialResourceMultiplier())
        self._updateConfigureButtonState(isFirstBattle, not isUnitFreezed)
        self.__setReadyStatus()
        self._updateMembersData()
        self._updateRallyData()
        if not self.__firstShowMainForm:
            self.__firstShowMainForm = True
            self.as_setBattleRoomDataS(self._makeFortClanBattleRoomVO(0, '', '', '', '', False, False, header.isSortie()))
            self.addListener(events.StrongholdEvent.STRONGHOLD_ON_TIMER, self._onMatchmakingTimerChanged, scope=EVENT_BUS_SCOPE.STRONGHOLD)
            self.prbEntity.forceTimerEvent()

    def onUpdateTimer(self, timer):
        pass

    def onUpdateState(self, state):
        self._updateOpenRoomBattleState(state.getPublic())

    def onUpdateReserve(self, reserve, reserveOrder):
        self._updateReserves(reserve, reserveOrder)

    def onStrongholdDataChanged(self, header, isFirstBattle, reserve, reserveOrder):
        self.invalidateStrongholdWaiting()
        self.onUpdateReserve(reserve, reserveOrder)
        self._updateMembersData()
        self._updateRallyData()

    def onSlotVehileFiltersChanged(self):
        self._updateRallyData()

    def onStrongholdDoBattleQueue(self, isFirstBattle, readyButtonEnabled, reserveOrder):
        self._updateConfigureButtonState(isFirstBattle, readyButtonEnabled)
        self.as_setReservesEnabledS([ readyButtonEnabled for _ in reserveOrder ])

    def onStrongholdMaintenance(self, showWindow):
        self.__maintenanceWindowVisible = showWindow
        if not self.__maintenanceWindowVisible:
            self.__forceUpdateBuildings()

    def setProxy(self, parent):
        self.__proxy = weakref.proxy(parent)
        self.invalidateStrongholdWaiting()

    def invalidateStrongholdWaiting(self):
        if self.__proxy:
            self.__proxy.showStrongholdWaiting(not self.prbEntity.isStrongholdSettingsValid())

    def resetFilters(self, slotIndex):
        self.__setFilters(slotIndex, 0)
        self.__setVehicles(slotIndex, None)
        self._updateMembersData()
        return

    def onFiltersChange(self, slotIndex, filters):
        self.__setFilters(slotIndex, filters)
        self._updateMembersData()

    def _populate(self):
        super(StrongholdBattleRoom, self)._populate()
        self.as_setFiltersDataS(self.__packFiltersData(self.__packTypeFiltersItems()))
        g_messengerEvents.users.onUserStatusUpdated += self.__onUserStatusUpdated
        g_messengerEvents.users.onUserActionReceived += self.__onUserDataChanged
        self.addListener(events.CSReserveSelectEvent.RESERVE_SELECTED, self.__onReserveSelectHandler)
        self.addListener(events.StrongholdEvent.STRONGHOLD_VEHICLES_SELECTED, self.__onUpdateFilterVehicles)
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__onFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.prbEntity.updateStrongholdData()
        self.prbEntity.forceTimerEvent()
        self.__postMinimiseFilterUpdate()
        self.__validateNationGroup()

    def _dispose(self):
        self.__proxy = None
        g_messengerEvents.users.onUserStatusUpdated -= self.__onUserStatusUpdated
        g_messengerEvents.users.onUserActionReceived -= self.__onUserDataChanged
        self.removeListener(events.StrongholdEvent.STRONGHOLD_ON_TIMER, self._onMatchmakingTimerChanged, scope=EVENT_BUS_SCOPE.STRONGHOLD)
        self.removeListener(events.CSReserveSelectEvent.RESERVE_SELECTED, self.__onReserveSelectHandler)
        self.removeListener(events.StrongholdEvent.STRONGHOLD_VEHICLES_SELECTED, self.__onUpdateFilterVehicles)
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__onFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        super(StrongholdBattleRoom, self)._dispose()
        if self.__changeModeBrowserId:
            self.__destroyChangeModeWindow()
        return

    def _closeSendInvitesWindow(self):
        self._destroyRelatedView(ViewTypes.WINDOW, FORTIFICATION_ALIASES.STRONGHOLD_SEND_INVITES_WINDOW_PY)

    def _rebuildCandidatesDP(self):
        if self._candidatesDP:
            self._candidatesDP.rebuild(self.prbEntity.getCandidates())

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(StrongholdBattleRoom, self)._onRegisterFlashComponent(viewPy, alias)
        if isinstance(viewPy, MinimapGrid):
            self.__minimapGrid = viewPy
            events_dispatcher.rqActivateChannel(self.__getClientID(), viewPy)
        if isinstance(viewPy, MinimapLobby):
            self.__minimap = viewPy

    def _onUnregisterFlashComponent(self, viewPy, alias):
        super(StrongholdBattleRoom, self)._onUnregisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.MINIMAP_GRID:
            events_dispatcher.rqDeactivateChannel(self.__getClientID())

    def _updateRallyData(self):
        entity = self.prbEntity
        unitPermissions = entity.getPermissions()
        havePermissions = unitPermissions.canChangeUnitState()
        canInvite = unitPermissions.canSendInvite()
        unitFreezed = entity.isStrongholdUnitFreezed() or entity.isStrongholdUnitWaitingForData()
        if entity.isStrongholdSettingsValid():
            maxPlayerCount = entity.getStrongholdSettings().getHeader().getMaxPlayersCount()
        else:
            maxPlayerCount = vo_converters.MAX_PLAYER_COUNT_ALL
        data = makeSortieVO(entity, havePermissions, unitMgrID=entity.getID(), canInvite=canInvite, maxPlayerCount=maxPlayerCount)
        if self.__changeModeBrowserId and not havePermissions:
            self.__destroyChangeModeWindow()
        if self.__minimapGrid:
            self.__minimapGrid.as_clickEnabledS(havePermissions and not unitFreezed)
        self.as_updateRallyS(data)

    def _makeFortClanBattleRoomVO(self, mapId, headerDescr, mineClanName, enemyClanName, waitForBattleDescr, isMapEnabled, isBattleTimerVisible, isSortie):
        vo = vo_converters.makeFortClanBattleRoomVO(mapId, headerDescr, mineClanName, enemyClanName, waitForBattleDescr, isMapEnabled, isBattleTimerVisible, isSortie)
        vo['levelsRange'] = self.prbEntity.getRosterSettings().getLevelsRange()
        return vo

    def _updateMembersData(self):
        entity = self.prbEntity
        self._setActionButtonState()
        if entity.isStrongholdSettingsValid():
            header = entity.getStrongholdSettings().getHeader()
            maxPlayerCount = header.getMaxPlayersCount()
            self._updateTableHeader(maxPlayerCount, header.getMaxLegionariesCount())
            isRosterSet, slots = makeStrongholdsSlotsVOs(entity, entity.getID(), maxPlayerCount=maxPlayerCount)
            self.as_setMembersS(isRosterSet, slots)

    def _getVehicleSelectorDescription(self):
        return FORTIFICATIONS.SORTIE_VEHICLESELECTOR_DESCRIPTION

    def _setActionButtonState(self):
        if self.__unitActive():
            self.as_setActionButtonStateS(StrongholdActionButtonStateVO(self.prbEntity))

    def _selectReserve(self, ctx):
        reserveID = ctx.get('newId', None)
        isRemove = ctx.get('isRemove', None)
        if reserveID is not None:
            if not isRemove:
                self.sendRequest(SetReserveUnitCtx(reserveID, waitingID='prebattle/change_settings', isRemove=isRemove))
            else:
                self.sendRequest(UnsetReserveUnitCtx(reserveID, waitingID='prebattle/change_settings', isRemove=isRemove))
        return

    def _updateMiniMapData(self, currentBattle, clan):
        if currentBattle:
            playerTeam = 1 if clan.getId() == currentBattle.getFirstClanId() else 2
            self.__minimap.setPlayerTeam(playerTeam)
            self.__minimap.setArena(currentBattle.getMapId())

    def _updateReserves(self, reserve, reserveOrder):
        slots = []
        enabled = []
        for index, groupType in enumerate(reserveOrder):
            reserveVO, enable = self.__updateReserve(groupType, reserve, index)
            slots.append(reserveVO)
            enabled.append(enable)

        self.as_setReservesDataS(slots)
        self.as_setReservesEnabledS(enabled)

    def _updateBuildings(self, currentBattle, enemyClan, battleIdx):
        data = self.prbEntity.getStrongholdSettings()
        if data.isValid() and data.getHeader() and not data.getHeader().isSortie():
            waitingForData = self.prbEntity.isStrongholdUnitWaitingForData() or self.__maintenanceWindowVisible
            if not waitingForData:
                if currentBattle is not None and enemyClan is not None:
                    index = currentBattle.getIndex()
                    attacker = currentBattle.getAttacker() != enemyClan.getId()
                else:
                    index = None
                    attacker = None
                self.as_setDirectionS(vo_converters.makeDirectionVO(index, attacker, battleIdx), self.prbEntity.animationNotAvailable())
            self.as_updateReadyDirectionsS(not waitingForData)
        return

    def _updateReadyDirections(self, readyButtonEnabled):
        ready = readyButtonEnabled
        self.as_updateReadyDirectionsS(ready)

    def _updateOpenRoomBattleState(self, isOpened):
        self.__isOpened = isOpened
        self.as_setOpenedS(*vo_converters.makeOpenRoomButtonVO(self.__isOpened))

    def _updateTableHeader(self, maxPlayerCount, maxLegCount):
        pCount = 0
        lCount = 0
        fullData = self.prbEntity.getUnitFullData()
        for slotInfo in fullData.slotsIterator:
            player = slotInfo.player
            if player is not None:
                pCount += 1
                if player.isLegionary():
                    lCount += 1

        self.as_setTableHeaderS(vo_converters.makeTableHeaderVO(pCount, maxPlayerCount, lCount, maxLegCount))
        return

    def _updateTitle(self, isSortie, direction, resourceMultiplier):
        if isSortie:
            title = i18n.makeString(FORTIFICATIONS.STRONGHOLDTITLE_SORTIE)
        else:
            direction = vo_converters.getDirection(direction)
            title = i18n.makeString(FORTIFICATIONS.STRONGHOLDTITLE_STRONGHOLD) % {'direction': direction}
            if resourceMultiplier > 1:
                title += ' (x%s)' % resourceMultiplier
        self.fireEvent(events.RenameWindowEvent(events.RenameWindowEvent.RENAME_WINDOW, ctx={'data': title}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _updateConfigureButtonState(self, isFirstBattle, readyButtonEnabled):
        flags = self.prbEntity.getFlags()
        isEnabled = readyButtonEnabled and isFirstBattle and not flags.isInQueue() and not flags.isInArena()
        vo = vo_converters.makeConfigureButtonVO(isEnabled, True)
        self.as_setConfigureButtonStateS(vo)

    def _onMatchmakingTimerChanged(self, event):
        data = event.ctx
        isBattleTimerVisible = False
        wfbDescr = None
        playerClanName = None
        enemyClanName = None
        currentBattle = data['currentBattle']
        mapId = currentBattle.getMapId() if currentBattle else 0
        enemyclanData = data['enemyClan']
        enemyVisible = enemyclanData is not None
        isInBattle = self.prbEntity.getFlags().isInArena()
        textid = data['textid']
        maxLvl = data['maxLevel']
        level = int2roman(maxLvl)
        if data['isSortie']:
            headerDescr = i18n.makeString(FORTIFICATIONS.STRONGHOLDINFO_SORTIE) % {'level': level}
            timetext = None
            if textid == FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_ENDOFBATTLESOON or textid == FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLESOON:
                timetext = makeHtmlString('html_templates:lobby/fortifications/introView', 'fortBattles', {'text': time_utils.getTimeLeftFormat(data['dtime'])})
            elif textid == FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETOMORROW or textid == FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETODAY:
                timetext = makeHtmlString('html_templates:lobby/fortifications/introView', 'fortBattles', {'text': backport.getShortTimeFormat(data['peripheryStartTimestamp'])})
            wfbDescr = i18n.makeString(textid, nextDate=timetext)
        else:
            direction = vo_converters.getDirection(data['direction'])
            headerDescr = i18n.makeString(FORTIFICATIONS.STRONGHOLDINFO_STRONGHOLD) % {'direction': direction}
            if textid != FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLESOON:
                timetext = None
                if textid == FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETOMORROW or textid == FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETODAY:
                    timetext = makeHtmlString('html_templates:lobby/fortifications/introView', 'fortBattles', {'text': backport.getShortTimeFormat(data['matchmakerNextTick'])})
                wfbDescr = i18n.makeString(textid, nextDate=timetext)
            else:
                isBattleTimerVisible = True
                fontColors = GUI_SETTINGS.lookup('StrongholdsTimerColors')
                colorRegular = fontColors.get('regular', '#FFDD99')
                colorAlarm = fontColors.get('alarm', '#ff7f00')
                enemyClanName = '?'
                if enemyVisible:
                    clColor = enemyclanData.getColor()
                    clColor = '#%06x' % clColor if clColor else '#ffffff'
                    enemyClanName = "<b><font face='$FieldFont' color='{0}'>[{1}]</font></b>".format(clColor, enemyclanData.getTag())
                clan = data['clan']
                if clan:
                    clColor = clan.getColor()
                    clColor = '#%06x' % clColor if clColor else '#ffffff'
                    playerClanName = "<b><font face='$FieldFont' color='{0}'>[{1}]</font></b>".format(clColor, clan.getTag())
                self.as_setTimerDeltaS(vo_converters.makeClanBattleTimerVO(data['dtime'] if not isInBattle else 0, "<font face='$FieldFont' size='18' color='{0}'>###</font>".format(colorRegular), "<font face='$FieldFont' size='18' color='{0}'>###</font>".format(colorAlarm), self.TIMER_GLOW_COLORS.NORMAL, self.TIMER_GLOW_COLORS.ALERT, '00', 0 if data['isFirstBattle'] else 1))
                self.as_updateReadyStatusS(self.prbEntity.getFlags().isInQueue(), self.__enemyReadyIndicator)
        self.as_setBattleRoomDataS(self._makeFortClanBattleRoomVO(mapId, headerDescr, playerClanName, enemyClanName, wfbDescr, enemyVisible, isBattleTimerVisible, data['isSortie']))
        if data['forceUpdateBuildings']:
            self.__forceUpdateBuildings()
        return

    def _onCacheResync(self, reason, diff):
        super(StrongholdBattleRoom, self)._onCacheResync(reason, diff)
        if GUI_ITEM_TYPE.VEHICLE in diff:
            mnVehs = {vehCD:self.itemsCache.items.getItemByCD(vehCD) for vehCD in diff[GUI_ITEM_TYPE.VEHICLE] if hasNationGroup(vehCD)}
            if mnVehs:
                for slotIndex, vehCDs in self.__vehiclesInSlotFilters.iteritems():
                    for cd in vehCDs:
                        if cd in mnVehs and not mnVehs[cd].activeInNationGroup:
                            vehCDs[vehCDs.index(cd)] = iterVehTypeCDsInNationGroup(cd).next()

                    self.sendRequest(ChangeVehiclesInSlotFilterCtx(slotIndex, vehCDs or [], waitingID='prebattle/change_settings'))

    def __postMinimiseFilterUpdate(self):
        filterData = self.prbEntity.getSlotFilters()
        for slotIndex, data in filterData.iteritems():
            vehCDs = data['vehicle_cds'][:]
            for cd in vehCDs:
                if hasNationGroup(cd):
                    vehItem = self.itemsCache.items.getItemByCD(cd)
                    if not vehItem.activeInNationGroup:
                        vehCDs[vehCDs.index(cd)] = iterVehTypeCDsInNationGroup(cd).next()

            self.__setVehicles(slotIndex, vehCDs)

    def __validateNationGroup(self):
        selected = self._getVehicleSelectorVehicles()
        if selected:
            vehicle = self.itemsCache.items.getItemByCD(selected[0])
            if not vehicle.activeInNationGroup:
                itemCD = iterVehTypeCDsInNationGroup(vehicle.intCompactDescr).next()
                self._selectVehicles([itemCD])

    def __forceUpdateBuildings(self):
        data = self.prbEntity.getStrongholdSettings()
        if data.isValid() and data.getHeader():
            header = data.getHeader()
            self._updateBuildings(header.getCurrentBattle(), header.getEnemyClan(), header.getBattleIdx())

    def __setMemberStatus(self, pInfo):
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            slotState = self.prbEntity.getSlotState(slotIdx)
            self.as_setMemberStatusS(slotIdx, vo_converters.getPlayerStatus(slotState, pInfo))

    def __onReserveSelectHandler(self, event):
        self._selectReserve(event.ctx)

    def __onUpdateFilterVehicles(self, event):
        slotIndex = event.ctx.get('slotIndex', -1)
        if slotIndex:
            self.__setVehicles(slotIndex, event.ctx.get('items', None))
            self._updateMembersData()
        return

    def __onFightButtonUpdated(self, event):
        self._setActionButtonState()

    def __updateReserve(self, groupType, reserveData, slotIndex):
        current = None
        group = reserveData.getUniqueReservesByGroupType(groupType)
        selectedReserves = reserveData.getSelectedReserves()
        for reserve in group:
            if reserve in selectedReserves:
                current = reserve
                break

        unitPermissions = self.prbEntity.getPermissions()
        havePermissions = unitPermissions.canChangeConsumables()
        notChosen = current is None
        if current:
            slotType = current.getType()
            level = current.getLevel()
            title = current.getTitle()
            description = current.getDescription()
            reserveId = current.getId()
        else:
            slotType = None
            level = 0
            title = ''
            description = ''
            reserveId = 0
        isRequsition = groupType == REQUISITION_TYPE
        disabledByRequisition = isRequsition and not self.prbEntity.isFirstBattle()
        empty = len(group) == 0
        isInBattle = self.prbEntity.getFlags().isInArena()
        enabled = havePermissions and not empty and not isInBattle and not disabledByRequisition
        tooltip, tooltiptype = vo_converters.makeReserveSlotTooltipVO(groupType, title, description, empty, notChosen, havePermissions, isInBattle, disabledByRequisition)
        vo = vo_converters.makeReserveSlotVO(slotType, groupType, reserveId, level, slotIndex, tooltip, tooltiptype)
        return (vo, enabled)

    def __setReadyStatus(self):
        self.__enemyReadyIndicator = False
        data = self.prbEntity.getStrongholdSettings()
        if data.isValid() and data.getHeader().getEnemyClan():
            self.__enemyReadyIndicator = data.getHeader().getEnemyClan().getReadyStatus()
        self.as_updateReadyStatusS(self.prbEntity.getFlags().isInQueue(), self.__enemyReadyIndicator)

    def __onUserDataChanged(self, _, user, shadowMode):
        if self._candidatesDP:
            candidates = self.prbEntity.getCandidates()
            if user.getID() in candidates:
                self._rebuildCandidatesDP()
                self._updateRallyData()

    def __onUserStatusUpdated(self, user):
        if self._candidatesDP:
            candidates = self.prbEntity.getCandidates()
            if user.getID() in candidates:
                self._rebuildCandidatesDP()
                self._updateRallyData()

    def __destroyChangeModeWindow(self):
        if self.browserCtrl.getBrowser(self.__changeModeBrowserId):
            app = self.appLoader.getApp()
            if app is not None and app.containerManager is not None:
                windowAlias = getViewName(VIEW_ALIAS.BROWSER_WINDOW_MODAL, self.__changeModeBrowserId)
                window = app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.UNIQUE_NAME: windowAlias})
                if window:
                    window.destroy()
        self.__changeModeBrowserId = 0
        return

    def __unitActive(self):
        flags = self.prbEntity.getFunctionalFlags()
        entityActive = flags & FUNCTIONAL_FLAG.STRONGHOLD > 0
        unitActive = flags & FUNCTIONAL_FLAG.UNIT > 0 and entityActive
        return unitActive

    def __getClientID(self):
        return channel_num_gen.getClientID4Prebattle(PREBATTLE_TYPE.STRONGHOLD)

    def __setVehicles(self, slotIndex, vehicles=None):
        self.__vehiclesInSlotFilters[slotIndex] = vehicles
        self.sendRequest(ChangeVehiclesInSlotFilterCtx(slotIndex, vehicles or [], waitingID='prebattle/change_settings'))

    def __packTypeFiltersItems(self):
        filters = []
        for bType, vType in FILTER_STATE.VEHICLE_TYPES:
            filters.append(self.__packFilterItem(vType, bType))

        return filters

    @staticmethod
    def __packFiltersData(items):
        return {'items': items,
         'minSelectedItems': 0}

    @staticmethod
    def __packFilterItem(vType, value):
        return {'icon': ''.join(('../maps/icons/filters/tanks/', vType, '.png')),
         'filterValue': value,
         'selected': False,
         'tooltip': makeTooltip('#menu:carousel_tank_filter/{}'.format(vType), '#fortifications:tooltip/vehicleTypes/body')}

    def __setFilters(self, slotIndex, filterState):
        self.__vehTypesInSlotFilters[slotIndex] = filterState
        vehTypesInFilter = [ vehType for bType, vehType in FILTER_STATE.VEHICLE_TYPES if filterState & bType ]
        self.sendRequest(ChangeVehTypesInSlotFilterCtx(slotIndex, vehTypesInFilter, waitingID='prebattle/change_settings'))
