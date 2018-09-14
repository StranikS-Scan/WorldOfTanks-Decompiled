# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/respawn_view.py
import BigWorld
import constants
from gui.battle_control.arena_info import getClientArena, hasResourcePoints
from gui.battle_control.avatar_getter import getPlayerVehicleID
from gui.shared.utils.plugins import IPlugin
import nations
from helpers import i18n, time_utils
from gui import makeHtmlString
from items.vehicles import VEHICLE_CLASS_TAGS
from shared_utils import findFirst
from gui.Scaleform.daapi.view.battle.meta.BattleRespawnViewMeta import BattleRespawnViewMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import g_sessionProvider
from gui.shared.formatters.text_styles import standard, main, statInfo
from gui.shared.gui_items.Vehicle import getIconPath
from gui.Scaleform.daapi.view.fallout_info_panel_helper import getHelpText
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
_FLAG_ICON_TEMPLATE = '../maps/icons/battle/respawn/optimize_flags_160x100/%s.png'
_VEHICLE_TYPE_TEMPLATE = '../maps/icons/vehicleTypes/%s.png'
_VEHICLE_TYPE_ELITE_TEMPLATE = '../maps/icons/vehicleTypes/elite/%s.png'
_VEHICLE_LEVEL_TEMPLATE = '../maps/icons/levels/tank_level_%d.png'
_CALLBACK_NAME = 'battle.onLoadRespawnView'
_MUST_TOP_ELEMENTS = ('fragCorrelationBar', 'battleTimer', 'debugPanel')

class _BattleRespawnView(BattleRespawnViewMeta):

    def __init__(self, proxy):
        super(_BattleRespawnView, self).__init__()
        self.__proxy = proxy
        self.__selectedVehicleID = None
        self.__igrVehicleFormat = makeHtmlString('html_templates:igr/premium-vehicle', 'name', {})
        return

    def start(self, vehsList):
        self._populate(self.__proxy.getMember('_level0.battleRespawnView').getInstance())
        slotsData = self.__getSlotsData(vehsList)
        generalData = self.__getGeneralData()
        arenaType = BigWorld.player().arena.arenaType
        helpText = getHelpText(arenaType)
        self.as_initializeS(generalData, slotsData, helpText)

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
            isElite = False
            result.append({'vehicleID': v.intCD,
             'vehicleName': self.__getVehicleName(v),
             'flagIcon': _FLAG_ICON_TEMPLATE % nations.NAMES[nationID],
             'vehicleIcon': getIconPath(v.type.name),
             'vehicleType': _VEHICLE_TYPE_ELITE_TEMPLATE % classTag if isElite else _VEHICLE_TYPE_TEMPLATE % classTag,
             'isElite': isElite,
             'vehicleLevel': _VEHICLE_LEVEL_TEMPLATE % v.type.level})

        return result

    def __getGeneralData(self):
        if hasResourcePoints():
            helpPanelMode = 'points'
        else:
            helpPanelMode = 'flags'
        return {'titleMsg': "<font face='$FieldFont' size='32' color='#F4EFE8'>%s</font><font size='4'><br><br></font>%s" % (i18n.makeString(INGAME_GUI.RESPAWNVIEW_TITLE), standard(i18n.makeString(INGAME_GUI.RESPAWNVIEW_ADDITIONALTIP))),
         'helpPanelMode': helpPanelMode}

    def __getSlotsStatesData(self, vehsList, cooldowns):
        result = []
        for v in vehsList:
            compactDescr = v.intCD
            cooldownTime = cooldowns.get(compactDescr, 0)
            cooldownStr = None
            cooldown = cooldownTime - BigWorld.serverTime()
            enabled = cooldown <= 0
            if not enabled:
                if cooldownTime > g_sessionProvider.getPeriodCtrl().getEndTime():
                    cooldownStr = i18n.makeString('#ingame_gui:respawnView/destroyedLbl')
                else:
                    cooldownStr = i18n.makeString('#ingame_gui:respawnView/cooldownLbl', time=time_utils.getTimeLeftFormat(cooldown))
            result.append({'vehicleID': compactDescr,
             'selected': compactDescr == self.__selectedVehicleID,
             'enabled': enabled,
             'cooldown': cooldownStr})

        return result

    def __getSelectedVehicle(self, vehsList):
        selectedVehicle = self.__getVehicleByID(self.__selectedVehicleID, vehsList)
        vName = self.__getVehicleName(selectedVehicle)
        return main(i18n.makeString(INGAME_GUI.RESPAWNVIEW_NEXTVEHICLENAME)) + statInfo(vName)

    def __getVehicleName(self, vehile):
        tags = vehile.type.tags
        isIGR = bool(VEHICLE_TAGS.PREMIUM_IGR in tags)
        vehicleName = vehile.type.shortUserString
        if isIGR:
            vehicleName = self.__igrVehicleFormat % {'vehicle': vehicleName}
        return vehicleName


class RespawnViewPlugin(IPlugin):

    def __init__(self, parentObj):
        super(RespawnViewPlugin, self).__init__(parentObj)
        self.__respawnView = None
        return

    def init(self):
        super(RespawnViewPlugin, self).init()
        self._parentObj.addExternalCallback(_CALLBACK_NAME, self.__onLoad)

    def fini(self):
        self._parentObj.removeExternalCallback(_CALLBACK_NAME)
        super(RespawnViewPlugin, self).fini()

    def start(self):
        super(RespawnViewPlugin, self).start()
        self._parentObj.movie.preinitializeRespawnView(_MUST_TOP_ELEMENTS)

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
