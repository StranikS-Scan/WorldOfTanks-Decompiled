# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/respawn.py
import math
import BigWorld
import logging
import SoundGroups
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters.time_formatters import getBattleTimerString
from helpers.CallbackDelayer import CallbackDelayer
from historical_battles.gui.Scaleform.daapi.view.meta.HBRespawnMeta import HBRespawnMeta
from historical_battles.gui.Scaleform.genConsts.HB_VEHICLE_CARD_STATE import HB_VEHICLE_CARD_STATE
from historical_battles.gui.Scaleform.genConsts.HB_FRONT_NAME import HB_FRONT_NAME
from historical_battles.gui.sounds.sound_constants import HBRespawnEvent
from items import vehicles
from tutorial.control.game_vars import getVehicleByIntCD
from gui.shared.gui_items.Vehicle import getIconResourceName, getNationLessName, getUserName
from gui.shared.utils.functions import replaceHyphenToUnderscore
from HBGoalComponent import HBGoalComponent
from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE
_logger = logging.getLogger(__name__)

class HistoricalBattlesRespawn(HBRespawnMeta, CallbackDelayer):
    _R_IMG_DIVISION = R.images.historical_battles.gui.maps.icons.division
    _R_IMG_VEHICLE = R.images.gui.maps.shop.vehicles.c_600x450
    _R_IMG_VEHICLE_TYPES = R.images.gui.maps.icons.vehicleTypes.big
    _UPDATE_INTERVAL = 1
    _BONUS_TYPE_TO_FRONT_NAME = {ARENA_BONUS_TYPE.HB_OFFENCE: HB_FRONT_NAME.OFFENCE,
     ARENA_BONUS_TYPE.HB_DEFENCE: HB_FRONT_NAME.DEFENCE}

    def __init__(self):
        HBRespawnMeta.__init__(self)
        CallbackDelayer.__init__(self)
        self.__goalFinishTime = None
        return

    def _populate(self):
        super(HistoricalBattlesRespawn, self)._populate()
        HBGoalComponent.onGoalsUpdated += self.__onGoalsUpdated

    def _dispose(self):
        self.__goalFinishTime = None
        CallbackDelayer.destroy(self)
        HBGoalComponent.onGoalsUpdated -= self.__onGoalsUpdated
        super(HistoricalBattlesRespawn, self)._dispose()
        return

    def __onGoalsUpdated(self, goalsInfo):
        if not goalsInfo:
            return
        self.__goalFinishTime = goalsInfo[-1]['finishTime']

    def __timerUpdate(self):
        if not self.__goalFinishTime:
            return
        timeLeft = math.ceil(self.__goalFinishTime - BigWorld.serverTime())
        self.as_updateGoalTimeS(backport.text(R.strings.hb_battle.respawn.goalTimer(), time=getBattleTimerString(timeLeft)))
        self.delayCallback(self._UPDATE_INTERVAL, self.__timerUpdate)

    def show(self):
        tankSet = BigWorld.player().HBAvatarRespawnComponent.tankSet
        tankSetMask = BigWorld.player().HBAvatarRespawnComponent.tankSetMask
        divisionID = BigWorld.player().HBAvatarRespawnComponent.divisionID
        bonusType = BigWorld.player().arena.bonusType
        frontName = self._BONUS_TYPE_TO_FRONT_NAME.get(bonusType, '')
        divisionName = R.strings.hb_lobby.dyn('division_{}'.format(divisionID)).name
        divisionEbmlem = self._R_IMG_DIVISION.c_110x110.dyn('c_{}'.format(divisionID))
        arenaType = BigWorld.player().arena.arenaType
        division = {'name': backport.text(divisionName()).upper(),
         'emblemSrc': backport.image(divisionEbmlem())}
        vehicleCards = []
        isAvailableCount = 0
        cardState = HB_VEHICLE_CARD_STATE.PICKED
        for isAvailable, (maskID, vehCD) in zip(tankSetMask, enumerate(tankSet)):
            vehType = vehicles.getVehicleType(vehCD)
            vehicleTypeSrc = R.images.gui.maps.icons.vehicleTypes.white.c_36x36.dyn(replaceHyphenToUnderscore(vehType.classTag))
            vehicle = getVehicleByIntCD(vehCD)
            vehicleSrc = self._R_IMG_VEHICLE.dyn(getIconResourceName(getNationLessName(vehicle.name)))
            if isAvailable:
                isAvailableCount += 1
            vehicleCards.append({'vehicleId': maskID,
             'vehicleSrc': backport.image(vehicleSrc()),
             'vehicleTypeSrc': backport.image(vehicleTypeSrc()),
             'vehicleName': getUserName(vehicles.getVehicleType(vehCD)),
             'emblemSrc': backport.image(divisionEbmlem()),
             'state': cardState if isAvailable else HB_VEHICLE_CARD_STATE.DEAD,
             'frontName': frontName})
            if cardState == HB_VEHICLE_CARD_STATE.PICKED and isAvailable:
                cardState = HB_VEHICLE_CARD_STATE.DEFAULT
                self.onPickVehicle(maskID)

        data = {'division': division,
         'vehicleCards': vehicleCards,
         'mapName': arenaType.geometryName}
        self.as_setDataS(data)
        self.as_setTimerDataS({'time': BigWorld.player().HBAvatarRespawnComponent.respawnTime - BigWorld.serverTime(),
         'title': backport.text(R.strings.hb_battle.respawn.timer.title.chooseVehicle()),
         'label': backport.text(R.strings.hb_battle.respawn.timer.label.chooseVehicle())})
        self.as_setVisibilityS(True, isAvailableCount != len(vehicleCards))
        self.__timerUpdate()

    def hide(self):
        self.as_setVisibilityS(False)
        self.stopCallback(self.__timerUpdate)

    def onPickVehicle(self, id):
        avatarComponent = BigWorld.player().HBAvatarRespawnComponent
        vehTypeCD = avatarComponent.tankSet[id]
        avatarComponent.selectVehicle(vehTypeCD)

    def onSelectVehicle(self):
        SoundGroups.g_instance.playSound2D(HBRespawnEvent.TANK_SELECTION)
        BigWorld.player().HBAvatarRespawnComponent.confirmVehicleSelection()
