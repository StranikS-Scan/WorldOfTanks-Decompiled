# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/stats_exchange/__init__.py
from typing import TYPE_CHECKING
import BigWorld
import aih_constants
from RTSShared import RTSOrder
from AvatarInputHandler import aih_global_binding
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import FragsCollectableStats
from gui.Scaleform.daapi.view.battle.commander.stats_exchange import supply, broker
from gui.Scaleform.daapi.view.meta.RTSBattleStatisticDataControllerMeta import RTSBattleStatisticDataControllerMeta
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.battle_control.controllers.commander.rts_commander_ctrl import getPrioritizedCondition
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
import shared_utils
if TYPE_CHECKING:
    from gui.battle_control.controllers.commander.interfaces import ICommand

class RTSStatisticsDataController(RTSBattleStatisticDataControllerMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def invalidateArenaInfo(self):
        super(RTSStatisticsDataController, self).invalidateArenaInfo()
        self.updateCommanderDataList()

    def invalidateSupplyData(self, arenaDP):
        exchange = self._exchangeBroker.getRTSSupplyExchange()
        exchange.update(arenaDP)
        data = exchange.get()
        if data:
            self.as_setRTSSupplyDataS(data)

    def invalidateVehiclesInfo(self, arenaDP):
        super(RTSStatisticsDataController, self).invalidateVehiclesInfo(arenaDP)
        self.invalidateSupplyData(arenaDP)
        for vInfo in arenaDP.getVehiclesInfoIterator():
            self.__onArenaVehicleUpdated(vInfo.vehicleID)

    def invalidateVehiclesStats(self, arenaDP):
        super(RTSStatisticsDataController, self).invalidateVehiclesStats(arenaDP)
        self.invalidateSupplyData(arenaDP)

    def addVehicleInfo(self, vo, arenaDP):
        super(RTSStatisticsDataController, self).addVehicleInfo(vo, arenaDP)
        self.invalidateSupplyData(arenaDP)
        self.__onArenaVehicleUpdated(vo.vehicleID)

    def updateVehiclesInfo(self, updated, arenaDP):
        super(RTSStatisticsDataController, self).updateVehiclesInfo(updated, arenaDP)
        self.invalidateSupplyData(arenaDP)

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        super(RTSStatisticsDataController, self).invalidateVehicleStatus(flags, vo, arenaDP)
        self.invalidateSupplyData(arenaDP)

    def updateVehiclesStats(self, updated, arenaDP):
        super(RTSStatisticsDataController, self).updateVehiclesStats(updated, arenaDP)
        self.invalidateSupplyData(arenaDP)

    def invalidateVehicleReloading(self, vehicleID):
        vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vehicleID)
        if vehicle is None:
            return
        else:
            self.__onVehicleReloading(vehicleID, vehicle.reloadingState)
            return

    def updateCommanderDataList(self):
        self.__updateCommanderData(tuple(self._battleCtx.getArenaDP().getVehiclesInfoIterator()))

    def updateCommanderDataVehicle(self, vInfo):
        self.__updateCommanderData((vInfo,))

    def getExchangeContext(self):
        return self._exchangeBroker.getExchangeCtx()

    def _createExchangeBroker(self, exchangeCtx):
        return broker.createExchangeBroker(exchangeCtx)

    def _createExchangeCollector(self):
        return FragsCollectableStats()

    def _populate(self):
        super(RTSStatisticsDataController, self)._populate()
        rtsCommander = self.__sessionProvider.dynamic.rtsCommander
        rtsCommander.vehicles.onOrderChanged += self.__onUpdateOrder
        rtsCommander.vehicles.onCommandComplete += self.__onCommandComplete
        rtsCommander.vehicles.onVehicleGroupChanged += self.__onVehicleGroupChanged
        rtsCommander.vehicles.onSelectionChanged += self.__onSelectionChanged
        rtsCommander.vehicles.onFocusVehicleChanged += self.__onFocusVehicleChanged
        rtsCommander.vehicles.onVehicleSpeaking += self.__onVehicleSpeaking
        rtsCommander.vehicles.onVehiclesInDragBoxChanged += self.__onVehiclesInDragBoxChanged
        rtsCommander.vehicles.onVehicleReloading += self.__onVehicleReloading
        rtsCommander.vehicles.onVehicleUpdated += self.__onVehicleUpdated
        rtsCommander.vehicles.onVehicleShellsUpdated += self.__onVehicleShellsUpdated
        rtsCommander.vehicles.onVehicleDisabledStateChanged += self.__onVehicleDisabledStateChanged
        rtsCommander.vehicles.onVehicleDeviceDamaged += self.__onVehicleDeviceDamaged
        rtsCommander.vehicles.onVehicleDeviceRepaired += self.__onVehicleDeviceRepaired
        rtsCommander.vehicles.onVehicleConditionUpdated += self.__onVehicleConditionUpdated
        vehicleChangeCtrl = self.__sessionProvider.dynamic.vehicleChange
        if vehicleChangeCtrl is not None:
            vehicleChangeCtrl.onStartVehicleControl += self.__onStartVehicleControl
            vehicleChangeCtrl.onStopVehicleControl += self.__onStopVehicleControl
        aih_global_binding.subscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self.__onControlModeChanged)
        self.as_setRTSPlayerCommanderS(BigWorld.player().isCommander())
        if self._battleCtx is not None:
            self.updateCommanderDataList()
        for vehicleID in rtsCommander.vehicles.keys(lambda v: v.isControllable):
            self.invalidateVehicleReloading(vehicleID)

        return

    def _dispose(self):
        sessionProvider = self.__sessionProvider
        rtsCommander = sessionProvider.dynamic.rtsCommander
        if rtsCommander is not None:
            rtsCommander.vehicles.onOrderChanged -= self.__onUpdateOrder
            rtsCommander.vehicles.onCommandComplete -= self.__onCommandComplete
            rtsCommander.vehicles.onVehicleGroupChanged -= self.__onVehicleGroupChanged
            rtsCommander.vehicles.onSelectionChanged -= self.__onSelectionChanged
            rtsCommander.vehicles.onFocusVehicleChanged -= self.__onFocusVehicleChanged
            rtsCommander.vehicles.onVehicleSpeaking -= self.__onVehicleSpeaking
            rtsCommander.vehicles.onVehiclesInDragBoxChanged -= self.__onVehiclesInDragBoxChanged
            rtsCommander.vehicles.onVehicleReloading -= self.__onVehicleReloading
            rtsCommander.vehicles.onVehicleUpdated -= self.__onVehicleUpdated
            rtsCommander.vehicles.onVehicleShellsUpdated -= self.__onVehicleShellsUpdated
            rtsCommander.vehicles.onVehicleDisabledStateChanged -= self.__onVehicleDisabledStateChanged
            rtsCommander.vehicles.onVehicleDeviceDamaged -= self.__onVehicleDeviceDamaged
            rtsCommander.vehicles.onVehicleDeviceRepaired -= self.__onVehicleDeviceRepaired
            rtsCommander.vehicles.onVehicleConditionUpdated -= self.__onVehicleConditionUpdated
        vehicleChangeCtrl = sessionProvider.dynamic.vehicleChange
        if vehicleChangeCtrl is not None:
            vehicleChangeCtrl.onStartVehicleControl -= self.__onStartVehicleControl
            vehicleChangeCtrl.onStopVehicleControl -= self.__onStopVehicleControl
        aih_global_binding.unsubscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self.__onControlModeChanged)
        super(RTSStatisticsDataController, self)._dispose()
        return

    def __onArenaVehicleUpdated(self, vehicleID):
        vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vehicleID)
        if vehicle is not None:
            self.__onVehicleUpdated(vehicle)
        return

    def __onVehicleUpdated(self, vehicle):
        self.__onVehicleGroupChanged(vehicle.id, vehicle.groupID)
        self.invalidateVehicleReloading(vehicle.id)
        self.__onVehicleDisabledStateChanged(vehicle.id, not vehicle.isEnabled)

    def __onVehicleGroupChanged(self, vehicleID, commanderGroup):
        self.as_setRTSVehicleGroupS(vehicleID, commanderGroup)

    def __onVehicleSpeaking(self, vehicleID, value):
        self.as_setRTSSpeakingVehicleS(vehicleID, value)

    def __onVehiclesInDragBoxChanged(self, vehicleIDs, value):
        self.as_setRTSVehiclesInFocusS(vehicleIDs, value)

    def __onSelectionChanged(self, selectedVehiclesIDs):
        self.as_setRTSSelectedVehiclesS(selectedVehiclesIDs)

    def __onFocusVehicleChanged(self, focusVehicleID, isInFocus):
        self.as_setRTSVehicleInFocusS(focusVehicleID if isInFocus else 0)

    def __onVehicleReloading(self, vehicleID, reloadingState):
        updateTime, timeLeft, baseTime = reloadingState
        self.as_setRTSReloadingS(vehicleID, updateTime, timeLeft, baseTime)

    def __onVehicleShellsUpdated(self, vehicleID, maxCount, currentCount, isAutoload, isDualGun):
        self.as_setRTSClipDataS(vehicleID, maxCount, currentCount, isAutoload, isDualGun)

    def __onVehicleDisabledStateChanged(self, vehicleID, isDisabled):
        self.as_setRTSVehicleDisabledS(vehicleID, isDisabled)

    def __onVehicleDeviceDamaged(self, vehicleID, damagedDevice):
        self.as_setDeviceDamagedS(vehicleID, damagedDevice)

    def __onVehicleDeviceRepaired(self, vehicleID, damagedDevice):
        self.as_setDeviceRepairedS(vehicleID, damagedDevice)

    def __updateCommanderData(self, vInfos):
        arena = BigWorld.player().arena
        commanderData = arena.commanderData
        otherCommanderData = arena.otherCommanderData
        exchangeBroker = self._exchangeBroker
        infoExchange = exchangeBroker.getRTSCommanderInfoExchange()
        dataExchange = exchangeBroker.getRTSCommanderDataExchange()
        attachedVehicleID = self.__getAttachedVehicleID()
        arenaDP = self._battleCtx.getArenaDP()
        for vInfo in vInfos:
            isEnemy, overrides = self._getTeamOverrides(vInfo, arenaDP)
            dataContainer = otherCommanderData if isEnemy else commanderData
            with dataExchange.getCollectedComponent(isEnemy) as item:
                vehicleID = vInfo.vehicleID
                item.setVehicleID(vehicleID)
                item.addVehicleCommanderData(dataContainer.get(vehicleID), attachedVehicleID == vehicleID)
            if vInfo.isCommander():
                with infoExchange.getCollectedComponent(isEnemy) as item:
                    item.addVehicleInfo(vInfo, overrides)

        self.__setCommanderInfo(infoExchange)
        self.__setCommanderData(dataExchange)

    def __setCommanderData(self, exchange):
        self.as_setRTSCommanderDataS(exchange.get())

    def __setCommanderInfo(self, exchange):
        self.as_setRTSCommanderInfoS(exchange.get())

    def __onUpdateOrder(self, vehID, order, **_):
        if order:
            self.as_setRTSOrderS(vehID, order.value, True)

    def __onCommandComplete(self, command, _):
        order = command.order
        if order not in (RTSOrder.CAPTURE_THE_BASE, RTSOrder.DEFEND_THE_BASE):
            self.as_setRTSOrderS(command.entity.id, order.value, False)

    def __onStartVehicleControl(self, vehID):
        self.as_setRTSOrderS(vehID, -1, False)
        self.updateCommanderDataList()

    def __onStopVehicleControl(self, _):
        self.updateCommanderDataList()

    def __onControlModeChanged(self, mode):
        self.updateCommanderDataList()
        self.as_setRTSCommanderModeS(mode in aih_constants.CTRL_MODE_NAME.COMMANDER_MODES)

        def voSearchCondition(v):
            return not (v.isObserver() or v.isSupply() or v.isCommander()) and arenaDP.isAllyTeam(v.team)

        arenaDP = self._battleCtx.getArenaDP()
        if mode in [aih_constants.CTRL_MODE_NAME.ARCADE, aih_constants.CTRL_MODE_NAME.COMMANDER] and arenaDP:
            vo = shared_utils.findFirst(voSearchCondition, arenaDP.getVehiclesInfoIterator())
            self.updateVehiclesInfo([(INVALIDATE_OP.SORTING, arenaDP.getVehicleInfo(vo.vehicleID))], arenaDP)

    def __onVehicleConditionUpdated(self, vehicleID, conditions):
        condition = getPrioritizedCondition(vehicleID, conditions)
        self.as_setRTSVehicleConditionS(vehicleID, condition)

    @staticmethod
    def __getAttachedVehicleID():
        attachedVehicle = BigWorld.player().getVehicleAttached()
        return None if attachedVehicle is None else attachedVehicle.id
