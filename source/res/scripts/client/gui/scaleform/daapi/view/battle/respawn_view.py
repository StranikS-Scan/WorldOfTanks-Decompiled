# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/respawn_view.py
import BigWorld
from gui.battle_control.arena_info import getClientArena
from gui.shared.utils.plugins import IPlugin
import nations
from helpers import i18n, time_utils
from items.vehicles import VEHICLE_CLASS_TAGS
from gui.Scaleform.daapi.view.battle.meta.BattleRespawnViewMeta import BattleRespawnViewMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import g_sessionProvider
from gui.shared.formatters.text_styles import standard, main, statInfo
from gui.shared.gui_items.Vehicle import getIconPath
from gui.shared.utils import findFirst
from gui.shared.view_helpers.FalloutInfoPanelHelper import getHelpText

class _BattleRespawnView(BattleRespawnViewMeta):
    __FLAG_ICON_TEMPLATE = '../maps/icons/battle/respawn/optimize_flags_160x100/%s.png'
    __VEHICLE_TYPE_TEMPLATE = '../maps/icons/battle/respawn/vehicleType/%s.png'

    def __init__(self, proxy):
        super(_BattleRespawnView, self).__init__()
        self.__proxy = proxy
        self.__selectedVehicleID = None
        return

    def start(self, vehsList):
        self._populate(self.__proxy.getMember('_level0.battleRespawnView').getInstance())
        generalData = self.__getGeneralData()
        slotsData = self.__getSlotsData(vehsList)
        arena = getClientArena()
        helpText = [''] * 4
        if arena is not None:
            helpText = getHelpText(arena.arenaType)
        self.as_initializeS(generalData, slotsData, helpText)
        return

    def destroy(self):
        self.__proxy = None
        self._dispose()
        return

    def show(self, selectedID, vehsList, cooldowns):
        self.__selectedVehicleID = selectedID
        self.__showRespawnView(vehsList, cooldowns)

    def hide(self):
        self.__selectedVehicleID = None
        self.__hideRespawnView()
        return

    def setSelectedVehicle(self, vehicleID, vehsList, cooldowns):
        self.__selectedVehicleID = vehicleID
        vehicleName = self.__getSelectedVehicle(vehsList)
        slotsStatesData = self.__getSlotsStatesData(vehsList, cooldowns)
        self.as_updateRespawnViewS(vehicleName, slotsStatesData)

    def updateTimer(self, timeLeft, vehsList, cooldowns):
        mainTimer = time_utils.getTimeLeftFormat(timeLeft)
        slots = self.__getSlotsStatesData(vehsList, cooldowns)
        self.as_respawnViewUpdateTimerS(mainTimer, slots)

    def py_vehicleSelected(self, vehicleID):
        g_sessionProvider.getRespawnsCtrl().chooseVehicleForRespawn(vehicleID)

    def __showRespawnView(self, vehsList, cooldowns):
        vehicleName = self.__getSelectedVehicle(vehsList)
        slotsStatesData = self.__getSlotsStatesData(vehsList, cooldowns)
        self.as_showRespawnViewS(vehicleName, slotsStatesData)

    def __hideRespawnView(self):
        self.as_hideRespawnViewS()

    def __getVehicleByID(self, intCD, vehicles):
        return findFirst(lambda v: v.intCD == intCD, vehicles)

    def __getSlotsData(self, vehsList):
        result = []
        for v in vehsList:
            nationID, _ = v.type.id
            classTag = tuple(VEHICLE_CLASS_TAGS & v.type.tags)[0]
            result.append({'vehicleID': v.intCD,
             'vehicleName': v.type.userString,
             'flagIcon': self.__FLAG_ICON_TEMPLATE % nations.NAMES[nationID],
             'vehicleIcon': getIconPath(v.type.name),
             'vehicleType': self.__VEHICLE_TYPE_TEMPLATE % classTag})

        return result

    def __getGeneralData(self):
        return {'titleMsg': "<font face='$FieldFont' size='32' color='#F4EFE8'>%s</font><font size='4'><br><br></font>%s" % (i18n.makeString(INGAME_GUI.RESPAWNVIEW_TITLE), standard(i18n.makeString(INGAME_GUI.RESPAWNVIEW_ADDITIONALTIP)))}

    def __getSlotsStatesData(self, vehsList, cooldowns):
        result = []
        for v in vehsList:
            compactDescr = v.intCD
            cooldownTime = cooldowns.get(compactDescr, 0)
            cooldown = cooldownTime - BigWorld.serverTime()
            enabled = cooldown <= 0
            cooldownStr = i18n.makeString(INGAME_GUI.RESPAWNVIEW_COOLDOWNLBL) + time_utils.getTimeLeftFormat(cooldown) if not enabled else None
            result.append({'vehicleID': compactDescr,
             'selected': compactDescr == self.__selectedVehicleID,
             'enabled': enabled,
             'cooldown': cooldownStr})

        return result

    def __getSelectedVehicle(self, vehsList):
        selectedVehicle = self.__getVehicleByID(self.__selectedVehicleID, vehsList)
        return main(i18n.makeString(INGAME_GUI.RESPAWNVIEW_NEXTVEHICLENAME)) + statInfo(selectedVehicle.type.userString)


class RespawnViewPlugin(IPlugin):
    __CALLBACK_NAME = 'battle.onLoadRespawnView'
    __MUST_TOP_ELEMENTS = ['fragCorrelationBar', 'battleTimer', 'debugPanel']

    def __init__(self, parentObj):
        super(RespawnViewPlugin, self).__init__(parentObj)
        self.__respawnView = None
        return

    def init(self):
        super(RespawnViewPlugin, self).init()
        self._parentObj.addExternalCallback(self.__CALLBACK_NAME, self.__onLoad)

    def fini(self):
        self._parentObj.removeExternalCallback(self.__CALLBACK_NAME)
        self.__MUST_TOP_ELEMENTS = None
        super(RespawnViewPlugin, self).fini()
        return

    def start(self):
        super(RespawnViewPlugin, self).start()
        self._parentObj.movie.preinitializeRespawnView(self.__MUST_TOP_ELEMENTS)

    def stop(self):
        g_sessionProvider.getRespawnsCtrl().stop()
        if self.__respawnView is not None:
            self.__respawnView.destroy()
            self.__respawnView = None
        super(RespawnViewPlugin, self).stop()
        return

    def __onLoad(self, _):
        self.__respawnView = _BattleRespawnView(self._parentObj)
        g_sessionProvider.getRespawnsCtrl().start(self.__respawnView, self._parentObj)
