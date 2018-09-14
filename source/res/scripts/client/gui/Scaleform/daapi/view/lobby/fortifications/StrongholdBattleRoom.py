# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/StrongholdBattleRoom.py
import BigWorld
import weakref
from helpers import time_utils
from UnitBase import UNIT_OP
from adisp import process
from constants import PREBATTLE_TYPE_NAMES, PREBATTLE_TYPE
from helpers import dependency, i18n
from debug_utils import LOG_CURRENT_EXCEPTION
from shared_utils import CONST_CONTAINER
from gui import GUI_SETTINGS, SystemMessages
from gui.app_loader import g_appLoader
from gui.clans.clan_helpers import getStrongholdUrl
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.MinimapLobby import MinimapLobby
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.rally import rally_dps
from gui.Scaleform.daapi.view.meta.FortClanBattleRoomMeta import FortClanBattleRoomMeta
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO, MAX_PLAYER_COUNT_ALL
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.strongholds import createStrongholdsWebHandlers
from gui.Scaleform.daapi.view.lobby.prb_windows.StrongholdActionButtonStateVO import StrongholdActionButtonStateVO
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.prb_control import settings
from gui.prb_control.entities.base.unit.listener import IUnitListener
from gui.prb_control.entities.base.unit.listener import IStrongholdListener
from gui.prb_control.entities.stronghold.unit.ctx import SetReserveUnitCtx, UnsetReserveUnitCtx
from gui.prb_control.settings import CTRL_ENTITY_TYPE, FUNCTIONAL_FLAG
from gui.prb_control.items.stronghold_items import REQUISITION_TYPE
from gui.prb_control.formatters import messages
from gui.shared import events
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.ClanCache import g_clanCache
from gui.shared.utils.functions import getViewName
from gui.shared.utils.MethodsRules import MethodsRules
from gui.shared.view_helpers import UsersInfoHelper
from skeletons.gui.game_control import IBrowserController
from messenger.proto.events import g_messengerEvents
from gui.Scaleform.managers.Cursor import Cursor

class StrongholdBattleRoom(FortClanBattleRoomMeta, IUnitListener, IStrongholdListener, MethodsRules, UsersInfoHelper):
    browserCtrl = dependency.descriptor(IBrowserController)

    class TIMER_GLOW_COLORS(CONST_CONTAINER):
        NORMAL = int('BB6200', 16)
        ALERT = int('BB2B00', 16)

    def __init__(self):
        super(StrongholdBattleRoom, self).__init__()
        self.__minimap = None
        self.__isOpened = False
        self.__battleModeData = {}
        self.__proxy = None
        self.__changeModeBrowserId = 0
        self.__firstShowMainForm = False
        return

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.__setReadyStatus()
        self._setActionButtonState()
        data = self.__getStrongholdData()
        if data:
            self._updateConfigureButtonState(data.isFirstBattle(), data.getReadyButtonEnabled())

    def onUnitPlayerStateChanged(self, pInfo):
        self.__setMemberStatus(pInfo)
        if pInfo.isCurrentPlayer() or self.prbEntity.isCommander():
            self._setActionButtonState()
        self._updateRallyData()

    def onTimerAlert(self):
        g_fortSoundController.playBattleRoomTimerAlert()

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
        entity = self.prbEntity
        pInfo = entity.getPlayerInfo(dbID=dbID)
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            if vInfos and not vInfos[0].isEmpty():
                vInfo = vInfos[0]
                vehicleVO = makeVehicleVO(g_itemsCache.items.getItemByCD(vInfo.vehTypeCD), entity.getRosterSettings().getLevelsRange(), isCurrentPlayer=pInfo.isCurrentPlayer())
                slotCost = vInfo.vehLevel
            else:
                slotState = entity.getSlotState(slotIdx)
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
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.STRONGHOLD_SEND_INVITES_WINDOW_PY, ctx={'prbName': PREBATTLE_TYPE_NAMES[PREBATTLE_TYPE.FORT_BATTLE],
         'ctrlType': CTRL_ENTITY_TYPE.UNIT,
         'showClanOnly': False}), scope=EVENT_BUS_SCOPE.LOBBY)

    def toggleRoomStatus(self):
        self.requestToOpen(not self.__isOpened)

    def chooseVehicleRequest(self):
        wgshData = self.prbEntity.getStrongholdData()
        if wgshData is not None:
            minLvl, maxLvl = wgshData.getMinLevel(), wgshData.getMaxLevel()
            levelsRange = self.prbEntity.getRosterSettings().getLevelsRange(minLvl, maxLvl)
        else:
            levelsRange = self.prbEntity.getRosterSettings().getLevelsRange()
        self._chooseVehicleRequest(levelsRange)
        return

    @process
    def openConfigureWindow(self):
        url = getStrongholdUrl('changeModeUrl')
        title = i18n.makeString(TOOLTIPS.CYBERSPORT_MODECHANGEFROZEN_HEADER)
        windowSize = GUI_SETTINGS.lookup('StrongholdsPopupWebWindowSize')
        browserSize = (windowSize.get('width', 800), windowSize.get('height', 600))
        self.__changeModeBrowserId = yield self.browserCtrl.load(url=url, title=title, browserSize=browserSize, isModal=True, showCreateWaiting=True, handlers=createStrongholdsWebHandlers(True), showActionBtn=False)
        browser = self.browserCtrl.getBrowser(self.__changeModeBrowserId)
        if browser:
            browser.ignoreKeyEvents = True
        else:
            self.__changeModeBrowserId = 0

    def onAvailableReservesChanged(self, selectedReservesIdx, reserveOrder):
        self._updateReserves(selectedReservesIdx, reserveOrder)

    def onBattleSeriesStatusChanged(self, currentBattle, enemyClan, battleIdx, clan):
        self._updateMiniMapData(currentBattle, clan)
        self._updateBuildings(currentBattle, enemyClan, battleIdx)

    def onDirectionChanged(self, isSortie, direction, resourceMultiplier):
        self._updateTitle(isSortie, direction, resourceMultiplier)
        self.__checkBattleMode()

    def onSelectedReservesChanged(self, selectedReservesIdx, reserveOrder):
        self._updateReserves(selectedReservesIdx, reserveOrder)

    def onIndustrialResourceMultiplierChanged(self, isSortie, direction, resourceMultiplier):
        self._updateTitle(isSortie, direction, resourceMultiplier)

    def onBattleDurationChanged(self, currentBattle, enemyClan, battleIdx, clan):
        self._updateMiniMapData(currentBattle, clan)
        self._updateBuildings(currentBattle, enemyClan, battleIdx)

    def onEnemyClanChanged(self, currentBattle, enemyClan, battleIdx, clan):
        self._updateMiniMapData(currentBattle, clan)
        self._updateBuildings(currentBattle, enemyClan, battleIdx)
        self.__setReadyStatus()

    def onLevelChanged(self):
        self.__checkBattleMode()

    def onPlayersCountChanged(self, maxPlayerCount, maxLegCount):
        self._updateRallyData(maxPlayerCount)
        self._updateTableHeader(maxPlayerCount, maxLegCount)
        self.__checkBattleMode()

    def onMaxLegionariesCountChanged(self, maxPlayerCount, maxLegCount):
        self._updateTableHeader(maxPlayerCount, maxLegCount)

    def onPermissionsChanged(self, selectedReservesIdx, reserveOrder):
        self._updateReserves(selectedReservesIdx, reserveOrder)

    def onPublicStateChanged(self, isOpened):
        self._updateOpenRoomBattleState(isOpened)

    def onTypeChanged(self, isSortie, direction, resourceMultiplier):
        self._updateTitle(isSortie, direction, resourceMultiplier)
        self.__checkBattleMode()

    def onStrongholdDataChanged(self):
        self.invalidateStrongholdWaiting()
        self.__strongholdUpdate()

    def onUpdateAll(self):
        self.__strongholdUpdate()

    def setProxy(self, parent):
        self.__proxy = weakref.proxy(parent)
        self.invalidateStrongholdWaiting()

    def invalidateStrongholdWaiting(self):
        if self.__proxy:
            self.__proxy.showStrongholdWaiting(self.__getStrongholdData() is None)
        return

    def _populate(self):
        super(StrongholdBattleRoom, self)._populate()
        g_messengerEvents.users.onUserStatusUpdated += self.__onUserStatusUpdated
        g_messengerEvents.users.onUserActionReceived += self.__onUserDataChanged
        self.addListener(events.CSReserveSelectEvent.RESERVE_SELECTED, self.__onReserveSelectHandler)
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__onFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__strongholdUpdate()

    def _dispose(self):
        self.__proxy = None
        g_messengerEvents.users.onUserStatusUpdated -= self.__onUserStatusUpdated
        g_messengerEvents.users.onUserActionReceived -= self.__onUserDataChanged
        self.removeListener(events.StrongholdEvent.STRONGHOLD_ON_TIMER, self._onMatchmakingTimerChanged, scope=EVENT_BUS_SCOPE.FORT)
        self.removeListener(events.CSReserveSelectEvent.RESERVE_SELECTED, self.__onReserveSelectHandler)
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__onFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        super(StrongholdBattleRoom, self)._dispose()
        if self.__changeModeBrowserId:
            self.__destroyChangeModeWindow()
        return

    def _closeSendInvitesWindow(self):
        from gui.Scaleform.framework import ViewTypes
        self._destroyRelatedView(ViewTypes.WINDOW, FORTIFICATION_ALIASES.STRONGHOLD_SEND_INVITES_WINDOW_PY)

    def _rebuildCandidatesDP(self):
        if self._candidatesDP:
            self._candidatesDP.rebuild(self.prbEntity.getCandidates())

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(StrongholdBattleRoom, self)._onRegisterFlashComponent(viewPy, alias)
        if isinstance(viewPy, MinimapLobby):
            self.__minimap = viewPy

    def _updateRallyData(self, maxPlayerCount=MAX_PLAYER_COUNT_ALL):
        entity = self.prbEntity
        unitPermissions = entity.getPermissions()
        havePermition = unitPermissions.canChangeUnitState()
        canInvite = unitPermissions.canSendInvite()
        maxPlayerCount = MAX_PLAYER_COUNT_ALL
        dataSH = self.__getStrongholdData()
        if dataSH:
            maxPlayerCount = dataSH.getMaxPlayerCount()
        data = vo_converters.makeSortieVO(entity, havePermition, unitIdx=entity.getUnitIdx(), app=self.app, canInvite=canInvite, maxPlayerCount=maxPlayerCount)
        if self.__changeModeBrowserId and not havePermition:
            self.__destroyChangeModeWindow()
        try:
            for slot in data['slots']:
                if slot['selectedVehicle'] and not slot['isFreezed'] and not slot['isCommanderState']:
                    slot['selectedVehicle']['isReadyToFight'] = True

        except:
            LOG_CURRENT_EXCEPTION()

        self.as_updateRallyS(data)

    def _updateMembersData(self):
        entity = self.prbEntity
        self._setActionButtonState()
        data = self.__getStrongholdData()
        if data:
            maxPlayerCount = data.getMaxPlayerCount()
            maxLegCount = data.getMaxLegCount()
            self._updateTableHeader(maxPlayerCount, maxLegCount)
            self.as_setMembersS(*vo_converters.makeSlotsVOs(entity, entity.getUnitIdx(), app=self.app, maxPlayerCount=maxPlayerCount))

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

    def _updateReserves(self, selectedReservesIdx, reserveOrder):
        slots = []
        enabled = []
        for index, groupType in enumerate(reserveOrder):
            reserveVO, enable = self.__updateReserve(groupType, selectedReservesIdx, index)
            slots.append(reserveVO)
            enabled.append(enable)

        self.as_setReservesDataS(slots)
        self.as_setReservesEnabledS(enabled)

    def _updateBuildings(self, currentBattle, enemyClan, battleIdx):
        index = currentBattle.getIndex() if currentBattle else None
        attacker = currentBattle.attacker != enemyClan.id if currentBattle else None
        self.as_setDirectionS(vo_converters.makeDirectionVO(index, attacker, battleIdx), self.prbEntity.animationNotAvailable())
        return

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
            title = i18n.makeString(FORTIFICATIONS.FORT2TITLE_SORTIE)
        else:
            direction = vo_converters.getDirection(direction)
            title = i18n.makeString(FORTIFICATIONS.FORT2TITLE_STRONGHOLD) % {'direction': direction}
            if resourceMultiplier > 1:
                title += ' (x%s)' % resourceMultiplier
        self.fireEvent(events.RenameWindowEvent(events.RenameWindowEvent.RENAME_WINDOW, ctx={'data': title}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _updateConfigureButtonState(self, isFirstBattle, readyButtonEnabled):
        flags = self.prbEntity.getFlags()
        isEnabled = not flags.isInQueue() and not flags.isInArena() and readyButtonEnabled
        vo = vo_converters.makeConfigureButtonVO(isEnabled and isFirstBattle, True)
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
        level = fort_formatters.getTextLevel(maxLvl)
        if data['isSortie']:
            headerDescr = i18n.makeString(FORTIFICATIONS.FORT2INFO_SORTIE) % {'level': level}
            timetext = None
            if textid == FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_ENDOFBATTLESOON:
                timetext = time_utils.getTimeLeftFormat(data['dtime'])
            elif textid == FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLESOON:
                timetext = time_utils.getTimeLeftFormat(data['dtime'])
            elif textid == FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETOMORROW:
                timetext = BigWorld.wg_getShortTimeFormat(data['peripheryStartTimestamp'])
            elif textid == FORTIFICATIONS.SORTIE_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETODAY:
                timetext = BigWorld.wg_getShortTimeFormat(data['peripheryStartTimestamp'])
            wfbDescr = i18n.makeString(textid, nextDate=timetext)
        else:
            direction = vo_converters.getDirection(data['direction'])
            headerDescr = i18n.makeString(FORTIFICATIONS.FORT2INFO_STRONGHOLD) % {'direction': direction}
            if textid != FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLESOON:
                timetext = None
                if textid == FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETOMORROW:
                    timetext = BigWorld.wg_getShortTimeFormat(data['matchmakerNextTick'])
                elif textid == FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLETODAY:
                    timetext = BigWorld.wg_getShortTimeFormat(data['matchmakerNextTick'])
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
        self.as_setBattleRoomDataS(vo_converters.makeFortClanBattleRoomVO(mapId, headerDescr, playerClanName, enemyClanName, wfbDescr, enemyVisible, isBattleTimerVisible, data['isSortie']))
        return

    def __setMemberStatus(self, pInfo):
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            slotState = self.prbEntity.getSlotState(slotIdx)
            self.as_setMemberStatusS(slotIdx, vo_converters.getPlayerStatus(slotState, pInfo))

    def __onReserveSelectHandler(self, event):
        self._selectReserve(event.ctx)

    def __onFightButtonUpdated(self, event):
        self._setActionButtonState()

    def __getStrongholdData(self):
        return self.prbEntity.getStrongholdData()

    def __strongholdUpdate(self):
        allData = self.__getStrongholdData()
        if allData is None:
            return
        else:
            if not self.__firstShowMainForm:
                self.__firstShowMainForm = True
                self.as_setBattleRoomDataS(vo_converters.makeFortClanBattleRoomVO(0, '', '', '', '', False, False, allData.isSortie()))
                self.addListener(events.StrongholdEvent.STRONGHOLD_ON_TIMER, self._onMatchmakingTimerChanged, scope=EVENT_BUS_SCOPE.FORT)
            self._updateRallyData(allData.getMaxPlayerCount())
            self._updateOpenRoomBattleState(allData.getPublic())
            self._updateMiniMapData(allData.getCurrentBattle(), allData.getClan())
            self._updateTableHeader(allData.getMaxPlayerCount(), allData.getMaxLegCount())
            self._updateBuildings(allData.getCurrentBattle(), allData.getEnemyClan(), allData.getBattleIdx())
            self._updateReserves(allData.getSelectedReservesIdx(), allData.getReserveOrder())
            self._updateTitle(allData.isSortie(), allData.getDirection(), allData.getResourceMultiplier())
            self._updateConfigureButtonState(allData.isFirstBattle(), allData.getReadyButtonEnabled())
            self.__checkBattleMode()
            return

    def __updateReserve(self, groupType, selected, slotIndex):
        data = self.__getStrongholdData()
        if data is None:
            return
        else:
            current = None
            group = data.getUniqueReservesByGroupType(groupType)
            for reserve in group:
                if reserve.getId() in selected:
                    current = reserve
                    break

            unitPermissions = self.prbEntity.getPermissions()
            havePermition = unitPermissions.canChangeConsumables()
            isFirstBattle = data.isFirstBattle()
            isInBattle = self.prbEntity.getFlags().isInArena()
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
            disabledByRequisition = isRequsition and not isFirstBattle
            empty = len(group) == 0
            enabled = havePermition and not empty and not isInBattle and not disabledByRequisition
            tooltip, tooltiptype = vo_converters.makeReserveSlotTooltipVO(groupType, title, description, empty, notChosen, havePermition, isInBattle, disabledByRequisition)
            vo = vo_converters.makeReserveSlotVO(slotType, groupType, reserveId, level, slotIndex, tooltip, tooltiptype)
            return (vo, enabled)

    def __setReadyStatus(self):
        data = self.__getStrongholdData()
        enemyReady = False
        if data and data.getEnemyClan():
            enemyReady = data.getEnemyClan().getReadyStatus()
        self.as_updateReadyStatusS(self.prbEntity.getFlags().isInQueue(), enemyReady)

    def __onUserDataChanged(self, _, user):
        if self._candidatesDP:
            candidates = self.prbEntity.getCandidates()
            if user._databaseID in candidates:
                self._rebuildCandidatesDP()
                self._updateRallyData()

    def __onUserStatusUpdated(self, user):
        if self._candidatesDP:
            candidates = self.prbEntity.getCandidates()
            if user._databaseID in candidates:
                self._rebuildCandidatesDP()
                self._updateRallyData()

    def __checkBattleMode(self):
        data = self.prbEntity.getStrongholdData()
        if data and data.isFirstBattle():
            battleModeFields = (('type', 'STRONGHOLDS_MODE_CHANGED'),
             ('direction', 'STRONGHOLDS_DIRECTION_CHANGED'),
             ('max_level', 'STRONGHOLDS_MODE_CHANGED'),
             ('max_players_count', 'STRONGHOLDS_MODE_CHANGED'))
            if self.__battleModeData:
                for field, key in battleModeFields:
                    if self.__battleModeData.get(field) != getattr(data, field):
                        SystemMessages.pushI18nMessage(messages.getUnitWarningMessage(key), type=SystemMessages.SM_TYPE.Warning)
                        break

            for field, _ in battleModeFields:
                self.__battleModeData[field] = getattr(data, field)

    def __destroyChangeModeWindow(self):
        if self.browserCtrl.getBrowser(self.__changeModeBrowserId):
            app = g_appLoader.getApp()
            if app is not None and app.containerManager is not None:
                windowAlias = getViewName(VIEW_ALIAS.BROWSER_WINDOW_MODAL, self.__changeModeBrowserId)
                window = app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.UNIQUE_NAME: windowAlias})
                if window:
                    window.destroy()
        self.__changeModeBrowserId = 0
        return

    def __unitActive(self):
        entity = self.prbEntity
        flags = entity.getFunctionalFlags()
        entityActive = flags & FUNCTIONAL_FLAG.FORT2 > 0
        unitActive = flags & FUNCTIONAL_FLAG.UNIT > 0 and entityActive
        return unitActive
