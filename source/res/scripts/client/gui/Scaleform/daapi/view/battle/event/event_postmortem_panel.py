# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_postmortem_panel.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PLAYER_CARD_ANIMATION_VISIBLE
from festivity.festival.player_card import PlayerCard
from festivity.festival.sounds import playSound
from gui.Scaleform.daapi.view.meta.EventPostmortemPanelMeta import EventPostmortemPanelMeta
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.festival import IFestivalController
EVENT_DOGTAG_MESSAGE_CODES = ('DEATH_FROM_INACTIVE_CREW_AT_SHOT', 'DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT', 'DEATH_FROM_SHOT', 'DEATH_FROM_DROWNING_ENEMY_SELF', 'DEATH_FROM_WORLD_COLLISION_ENEMY_SELF', 'DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF', 'DEATH_FROM_DEATH_ZONE_ENEMY_SELF', 'DEATH_FROM_RAMMING_ENEMY_SELF', 'DEATH_FROM_OVERTURN_ENEMY_SELF', 'DEATH_FROM_FIRE')

class EventPostmortemPanel(EventPostmortemPanelMeta):
    _festController = dependency.descriptor(IFestivalController)
    __slots__ = ('__isDogtagSet', '__needSetDogtag')

    def __init__(self):
        super(EventPostmortemPanel, self).__init__()
        self.__isDogtagSet = False
        self.__needSetDogtag = False

    def switchShowDogtagAnimation(self, value):
        AccountSettings.setSettings(PLAYER_CARD_ANIMATION_VISIBLE, value)

    def onDogtagRollover(self):
        playSound(backport.sound(R.sounds.ev_fest_arena_token_zoom_on()))

    def onDogtagRollout(self):
        playSound(backport.sound(R.sounds.ev_fest_arena_token_zoom_off()))

    def onDogtagStartAnim(self):
        playSound(backport.sound(R.sounds.ev_fest_arena_token_appear()))

    def onDogtagHideAnim(self):
        playSound(backport.sound(R.sounds.ev_fest_arena_token_disappear()))

    def _populate(self):
        self.addListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        super(EventPostmortemPanel, self)._populate()

    def _dispose(self):
        self.__invitations = None
        self.removeListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        super(EventPostmortemPanel, self)._dispose()
        return

    def _prepareMessage(self, code, killerVehID, device=None):
        if killerVehID is not None and code in EVENT_DOGTAG_MESSAGE_CODES:
            context = self.sessionProvider.getCtx()
            isSelf = context.isCurrentPlayer(killerVehID)
            if isSelf:
                return
            isNotTK = not context.isTeamKiller(killerVehID)
            if isNotTK:
                self.__needSetDogtag = True
        super(EventPostmortemPanel, self)._prepareMessage(code, killerVehID, device)
        return

    def _nickNameFormatter(self, nickName):
        return nickName.replace(' ', '&nbsp;')

    def _showOwnDeathInfo(self):
        super(EventPostmortemPanel, self)._showOwnDeathInfo()
        if not self.__needSetDogtag or self.__isDogtagSet:
            return
        else:
            deathInfo = self.getDeathInfo()
            if deathInfo is None:
                return
            killerVehID = deathInfo['killerVehicle']
            battleCtx = self.sessionProvider.getCtx()
            if killerVehID and not battleCtx.isCurrentPlayer(killerVehID):
                context = self.sessionProvider.getCtx()
                vInfoVO = battleCtx.getArenaDP().getVehicleInfo(killerVehID)
                if vInfoVO.playerCard is None:
                    return
                playerCard = PlayerCard(vInfoVO.playerCard)
                self._festController.setGlobalPlayerCard(playerCard)
                basisImg = backport.image(playerCard.getBasis().getIconResID())
                emblemImg = backport.image(playerCard.getEmblem().getIconResID())
                emblemSmallImg = backport.image(playerCard.getEmblem().getSmallIconResID())
                basisSmallImg = backport.image(playerCard.getBasis().getSmallIconResID())
                titleImg = backport.image(playerCard.getTitle().getIconResID())
                rankStr = backport.text(playerCard.getRank().getNameResID())
                nickStr = context.getPlayerFullName(killerVehID, showVehShortName=False, showClan=False)
                translateStr = backport.text(R.strings.festival.dogtag.translate(), backport.text(playerCard.getTitle().getNameResID()))
                basisBackImg = backport.image(playerCard.getBasis().getBasisResID())
                truncateEndingStr = backport.text(R.strings.festival.dogtag.truncated())
                animEnabledTooltip = TOOLTIPS.EVENTPOSTMORTEMPANEL_GODTAG_ANIMENABLED
                animDisabledTooltip = TOOLTIPS.EVENTPOSTMORTEMPANEL_GODTAG_ANIMDISABLED
                self.__isDogtagSet = True
                self.as_setDogtagInfoS(basisImg=basisImg, emblemImg=emblemImg, titleImg=titleImg, rankStr=rankStr, nickStr=nickStr, isAnimEnabled=AccountSettings.getSettings(PLAYER_CARD_ANIMATION_VISIBLE), basisSmallImg=basisSmallImg, emblemSmallImg=emblemSmallImg, translateStr=translateStr, basisBackImg=basisBackImg, truncateEndingStr=truncateEndingStr, animEnabledTooltip=animEnabledTooltip, animDisabledTooltip=animDisabledTooltip)
                self._festController.setGlobalPlayerCard(None)
            return

    def _getVehicleData(self, killerVehID):
        showVehicle, vehLvl, vehImg, vehClass, vehName = super(EventPostmortemPanel, self)._getVehicleData(killerVehID)
        context = self.sessionProvider.getCtx()
        if not context.isTeamKiller(killerVehID) and self.__needSetDogtag:
            showVehicle = True
        return (showVehicle,
         vehLvl,
         vehImg,
         vehClass,
         vehName)

    def __handleShowCursor(self, _):
        if self._isPlayerVehicle:
            self.as_toggleCtrlPressFlagS(True)

    def __handleHideCursor(self, _):
        if self._isPlayerVehicle:
            self.as_toggleCtrlPressFlagS(False)
