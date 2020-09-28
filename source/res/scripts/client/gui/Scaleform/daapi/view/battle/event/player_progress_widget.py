# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/player_progress_widget.py
from gui import GUI_SETTINGS
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.battle.wt_event.battle_progression_view import HuntersBattleProgressionView
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.Scaleform.daapi.view.meta.EventBossProgressWidgetMeta import EventBossProgressWidgetMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IBattleFieldController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from items.vehicles import VehicleDescr

class BossProgressWidget(EventBossProgressWidgetMeta, IBattleFieldController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BossProgressWidget, self).__init__()
        self.__maxHealth = 0

    def getControllerID(self):
        return BATTLE_CTRL_ID.GUI

    def startControl(self, battleCtx, arenaVisitor):
        self.__playerFormatter = battleCtx.createPlayerFullNameFormatter(showVehShortName=False)

    def stopControl(self):
        self.__playerFormatter = None
        return

    def invalidateVehiclesInfo(self, arenaDP):
        for vInfo in arenaDP.getVehiclesInfoIterator():
            if {'event_boss'} & vInfo.vehicleType.tags:
                self.__updateBossInfo(vInfo)

    def invalidateArenaInfo(self):
        arenaDP = self.__sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            if {'event_boss'} & vInfo.vehicleType.tags:
                self.__updateBossInfo(vInfo)

    def invalidateVehicleStatus(self, flags, vInfo, arenaDP):
        if {'event_boss'} & vInfo.vehicleType.tags:
            self.__updateBossInfo(vInfo)

    def addVehicleInfo(self, vInfo, _):
        if {'event_boss'} & vInfo.vehicleType.tags:
            self.__updateBossInfo(vInfo)

    def updateVehiclesInfo(self, updated, arenaDP):
        for _, vInfo in updated:
            if {'event_boss'} & vInfo.vehicleType.tags:
                self.__updateBossInfo(vInfo)

    def updateVehiclesStats(self, updated, arenaDP):
        arenaDP = self.__sessionProvider.getArenaDP()
        for _, vStatsVO in updated:
            vInfoVO = arenaDP.getVehicleInfo(vStatsVO.vehicleID)
            if {'event_boss'} & vInfoVO.vehicleType.tags:
                self.__updateBossInfo(vInfoVO)

    def invalidatePlayerStatus(self, flags, vInfoVO, arenaDP):
        if {'event_boss'} & vInfoVO.vehicleType.tags:
            self.__updateBossInfo(vInfoVO)

    def invalidateVehiclesStats(self, arenaDP):
        arenaDP = self.__sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            if {'event_boss'} & vInfo.vehicleType.tags:
                self.__updateBossInfo(vInfo)

    def _populate(self):
        super(BossProgressWidget, self)._populate()
        self.__sessionProvider.addArenaCtrl(self)
        self.__maxHealth = VehicleDescr(typeName='germany:G98_Waffentrager_E100_TL').maxHealth
        arenaInfoCtrl = self.__sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onBossHealthChanged += self.__onBossHealthChanged
        self.as_setHpRatioS(GUI_SETTINGS.eventSettings.bossHpRatio)
        self.invalidateVehiclesStats(self.__sessionProvider.getArenaDP())
        return

    def _dispose(self):
        self.__sessionProvider.removeArenaCtrl(self)
        arenaInfoCtrl = self.__sessionProvider.dynamic.arenaInfo
        if arenaInfoCtrl is not None:
            arenaInfoCtrl.onBossHealthChanged -= self.__onBossHealthChanged
        super(BossProgressWidget, self)._dispose()
        return

    def __onBossHealthChanged(self, value):
        self.as_updateHpS(max(0, value))

    def __updateBossInfo(self, vInfo):
        arenaDP = self.__sessionProvider.getArenaDP()
        arenaInfo = avatar_getter.getArenaInfo()
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        vStats = arenaDP.getVehicleStats(vInfo.vehicleID)
        frags = vStats.frags if vStats is not None else 0
        parts = self.__playerFormatter.format(vInfo)
        vo = {'playerName': parts.playerName,
         'playerFakeName': parts.playerFakeName,
         'playerFullName': parts.playerFullName,
         'clanAbbrev': vInfo.player.clanAbbrev,
         'hpCurrent': max(0, arenaInfo.bossHealth),
         'kills': frags,
         'isPlayer': vInfo.vehicleID == playerVehicleID,
         'hpMax': self.__maxHealth,
         'isSpecial': 'special_event_boss' in vInfo.vehicleType.tags,
         'region': parts.regionCode}
        self.as_setWidgetDataS(vo)
        return


class HuntersProgressWidget(InjectComponentAdaptor, IAbstractPeriodView):

    def _makeInjectView(self):
        return HuntersBattleProgressionView()
