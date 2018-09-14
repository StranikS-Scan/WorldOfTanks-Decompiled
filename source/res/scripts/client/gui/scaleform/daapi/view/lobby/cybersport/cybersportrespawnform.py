# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportRespawnForm.py
import BigWorld
import functools
from shared_utils import CONST_CONTAINER, safeCancelCallback
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.clubs.club_helpers import MyClubListener
from gui.Scaleform.daapi.view.meta.CyberSportRespawnFormMeta import CyberSportRespawnFormMeta
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.prb_control import settings
from gui.shared import g_itemsCache
from gui import makeHtmlString
from gui.shared.utils.functions import getArenaShortName
from gui.shared.view_helpers import ClubEmblemsHelper
from helpers import time_utils
from helpers import int2roman

class CyberSportRespawnForm(CyberSportRespawnFormMeta, MyClubListener, ClubEmblemsHelper):
    WARNING_TIME = 10

    class TIME_TEMPLATES(CONST_CONTAINER):
        NORMAL = 'timeNormal'
        WARNING = 'timeWarning'

    class ENEMY_STATUSES(CONST_CONTAINER):
        NORMAL = 'normal'
        READY = 'ready'

    def __init__(self):
        super(CyberSportRespawnForm, self).__init__()
        self.__extra = self.unitFunctional.getExtra()
        self.__timerCallback = None
        self.__warningCallback = None
        return

    def onClubEmblem32x32Received(self, clubDbID, emblem):
        if emblem:
            self.as_setTeamEmblemS(self.getMemoryTexturePath(emblem))

    def onUnitFlagsChanged(self, flags, timeLeft):
        self._setActionButtonState()
        if flags.isChanged():
            self._updateMembersData()
            self.__updateTimer()
            self.__updateWarning()

    def onUnitVehicleChanged(self, dbID, vInfo):
        functional = self.unitFunctional
        pInfo = functional.getPlayerInfo(dbID=dbID)
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            if not vInfo.isEmpty():
                vehicleVO = makeVehicleVO(g_itemsCache.items.getItemByCD(vInfo.vehTypeCD), functional.getRosterSettings().getLevelsRange())
                slotCost = vInfo.vehLevel
            else:
                slotState = functional.getSlotState(slotIdx)
                vehicleVO = None
                if slotState.isClosed:
                    slotCost = settings.UNIT_CLOSED_SLOT_COST
                else:
                    slotCost = 0
            self.as_setMemberVehicleS(slotIdx, slotCost, vehicleVO)
            self.__updateTotal()
        if pInfo.isCurrentPlayer() or functional.getPlayerInfo().isCreator():
            self._setActionButtonState()
        return

    def onUnitMembersListChanged(self):
        self._updateMembersData()
        self._setActionButtonState()
        self.__updateTotal()

    def onUnitExtraChanged(self, extra):
        self.__extra = self.unitFunctional.getExtra()
        self.__updateHeader()
        self.__updateTimer()
        self.__updateWarning()

    def onClubUpdated(self, club):
        self.__updateHeader()

    def onUnitRejoin(self):
        super(CyberSportRespawnForm, self).onUnitRejoin()
        self._updateMembersData()
        self.__updateHeader()
        self.__updateTimer()
        self.__updateWarning()
        self.__updateTotal()

    def _populate(self):
        super(CyberSportRespawnForm, self)._populate()
        self.startMyClubListening()
        self.__updateHeader()
        self.__updateTimer()
        self.__updateWarning()
        self.__updateTotal()
        settings = self.unitFunctional.getRosterSettings()
        self._updateVehiclesLabel(int2roman(settings.getMinLevel()), int2roman(settings.getMaxLevel()))

    def _dispose(self):
        self.__cancelTimerCallback()
        self.__cancelWargningCallback()
        self.stopMyClubListening()
        super(CyberSportRespawnForm, self)._dispose()

    def _getVehicleSelectorDescription(self):
        return CYBERSPORT.WINDOW_VEHICLESELECTOR_INFO_RESPAWN

    def _setActionButtonState(self):
        functional = self.unitFunctional
        pInfo = functional.getPlayerInfo()
        isCreator = pInfo.isCreator()
        isEnabled, _ = functional.canPlayerDoAction()
        if isCreator:
            isReady = False
            stateString = '#cyberSport:respawn/fight/status/commander'
        else:
            isReady = True
            stateString = '#cyberSport:respawn/fight/status/private'
        actionBtnData = {'toolTipData': '#tooltips:cyberSport/respawn/fightBtn/body',
         'isEnabled': isEnabled,
         'label': '#cyberSport:respawn/fight/label',
         'isReady': isReady,
         'stateString': stateString}
        self.as_setActionButtonStateS(actionBtnData)

    def _updateRallyData(self):
        functional = self.unitFunctional
        if functional is not None:
            data = vo_converters.makeStaticFormationUnitVO(functional, unitIdx=functional.getUnitIdx(), app=self.app)
            self.as_updateRallyS(data)
        return

    def __updateHeader(self):
        self.as_setTeamNameS(self.__extra.clubName)
        club = self.getClub()
        if club is not None:
            self.requestClubEmblem32x32(club.getClubDbID(), club.getEmblem32x32())
        statusID = self.ENEMY_STATUSES.READY if self.__extra.isEnemyReady else self.ENEMY_STATUSES.NORMAL
        enemyStatusLabel = makeHtmlString('html_templates:lobby/cyberSport/respawn/enemyStatus', statusID)
        self.as_updateEnemyStatusS(statusID, enemyStatusLabel)
        self.as_setArenaTypeIdS(getArenaShortName(self.__extra.mapID), self.__extra.mapID)
        return

    def __updateTimer(self):
        timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.__extra.startTime))
        self.__cancelTimerCallback()
        self.__showTimer(timeLeft)

    def __showTimer(self, timeLeft):
        self.__timerCallback = None
        templateName = self.TIME_TEMPLATES.WARNING if timeLeft <= self.WARNING_TIME else self.TIME_TEMPLATES.NORMAL
        timeLeftMsg = makeHtmlString('html_templates:lobby/cyberSport/respawn', templateName, {'time': time_utils.getTimeLeftFormat(timeLeft)})
        self.as_timerUpdateS(timeLeftMsg)
        if timeLeft > 0:
            self.__timerCallback = BigWorld.callback(1, functools.partial(self.__showTimer, timeLeft - 1))
        return

    def __cancelTimerCallback(self):
        if self.__timerCallback is not None:
            safeCancelCallback(self.__timerCallback)
            self.__timerCallback = None
        return

    def __updateWarning(self):
        timeLeft = time_utils.getTimeDeltaFromNow(self.__extra.startTime)
        self.__cancelWargningCallback()
        self.__showWarning(timeLeft)

    def __showWarning(self, timeLeft):
        self.__warningCallback = None
        level = 'warning' if timeLeft <= self.WARNING_TIME else 'info'
        isInQueue = self.unitFunctional is not None and self.unitFunctional.getFlags().isInQueue()
        msgStatus = 'ready' if isInQueue else level
        status = makeHtmlString('html_templates:lobby/cyberSport/respawn/status', msgStatus)
        tooltip = '#tooltips:cyberSport/respawn/status/%s' % msgStatus
        self.as_statusUpdateS(status, level, tooltip)
        if timeLeft > self.WARNING_TIME:
            self.__warningCallback = BigWorld.callback(timeLeft - self.WARNING_TIME, functools.partial(self.__showWarning, self.WARNING_TIME))
        return

    def __cancelWargningCallback(self):
        if self.__warningCallback is not None:
            safeCancelCallback(self.__warningCallback)
            self.__warningCallback = None
        return

    def __updateTotal(self):
        functional = self.unitFunctional
        unitStats = functional.getStats()
        canDoAction, restriction = functional.validateLevels(stats=unitStats)
        self.as_setTotalLabelS(canDoAction, vo_converters.makeTotalLevelLabel(unitStats, restriction), unitStats.curTotalLevel)
