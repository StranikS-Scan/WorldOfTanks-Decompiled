# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/respawn_view.py
import BigWorld
from gui.battle_control.arena_info import hasResourcePoints, isFalloutMultiTeam, hasFlags
from gui.Scaleform.daapi.view.fallout_info_panel_helper import getCosts
from gui.shared.utils.plugins import IPlugin
import nations
from helpers import i18n, time_utils
from gui import makeHtmlString
from items.vehicles import VEHICLE_CLASS_TAGS
from shared_utils import findFirst
from gui.Scaleform.daapi.view.battle.meta.BattleRespawnViewMeta import BattleRespawnViewMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import g_sessionProvider
from gui.shared.formatters.text_styles import standard, main, statInfo, warning
from gui.shared.gui_items.Vehicle import getIconPath
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.Scaleform.locale.FALLOUT import FALLOUT
from helpers.i18n import makeString
_FLAG_ICON_TEMPLATE = '../maps/icons/battle/respawn/optimize_flags_160x100/%s.png'
_VEHICLE_TYPE_TEMPLATE = '../maps/icons/vehicleTypes/%s.png'
_VEHICLE_TYPE_ELITE_TEMPLATE = '../maps/icons/vehicleTypes/elite/%s.png'
_VEHICLE_LEVEL_TEMPLATE = '../maps/icons/levels/tank_level_%d.png'
_CALLBACK_NAME = 'battle.onLoadRespawnView'
_HTML_TEMPLATE_FALLOUT_INFO_KEY = 'html_templates:battle/falloutSingleInfo'
_HTML_TEMPLATE_GARAGE_KEY = 'html_templates:battle/garage'

class _BattleRespawnView(BattleRespawnViewMeta):

    def __init__(self, proxy):
        super(_BattleRespawnView, self).__init__()
        self.__proxy = proxy
        self.__selectedVehicleID = None
        self.__igrVehicleFormat = makeHtmlString('html_templates:igr/premium-vehicle', 'name', {})
        self.__disabled = False
        return

    def start(self, vehsList, isLimited):
        self._populate(self.__proxy.getMember('_level0.battleRespawnView').getInstance())
        slotsData = self.__getSlotsData(vehsList)
        generalData = self.__getGeneralData(isLimited)
        helpText = self.__getHelpText()
        self.as_initializeS(generalData, slotsData, helpText)

    def __getHelpText(self):
        arena = BigWorld.player().arena
        arenaType = arena.arenaType
        isSolo = len(list(g_sessionProvider.getArenaDP().getVehiclesIterator())) == 1
        plusStr = makeString(FALLOUT.INFOPANEL_SINGLEHELPTEXT_PLUS)
        isMultiteam = isFalloutMultiTeam()
        headerStr = makeHtmlString(_HTML_TEMPLATE_FALLOUT_INFO_KEY, 'header', makeString(FALLOUT.INFOPANEL_SECRETWIN_HEAD))
        additionalBlockTemplate = makeHtmlString(_HTML_TEMPLATE_FALLOUT_INFO_KEY, 'winPoints')
        costKill, costFlags, costDamage = getCosts(arenaType, isSolo, True)
        helpStr = ''
        if hasFlags(arenaType, arena.bonusType) and len(costFlags) > 0:
            costFlags = list(costFlags)[0]
            helpStr = self.__getAdditionalBlockStr(additionalBlockTemplate, FALLOUT.INFOPANEL_SINGLEHELPTEXT_WINPOINTS_FLAGCAPTURE, warning(plusStr + str(costFlags)))
            if isMultiteam and isSolo:
                helpStr = self.__getAdditionalBlockStr(additionalBlockTemplate, FALLOUT.INFOPANEL_SINGLEHELPTEXT_WINPOINTS_FLAGDESTROY, warning(plusStr + str(costFlags)))
        helpStr += self.__getAdditionalBlockStr(additionalBlockTemplate, FALLOUT.INFOPANEL_SINGLEHELPTEXT_WINPOINTS_KILL, warning(plusStr + str(costKill)))
        damageDealt, points = costDamage
        points = warning(plusStr + str(points))
        helpStr += additionalBlockTemplate % makeString(FALLOUT.INFOPANEL_SINGLEHELPTEXT_WINPOINTS_DAMAGE, points=points, damageDealt=damageDealt)
        return headerStr + helpStr

    def __getAdditionalBlockStr(self, template, localeKey, params):
        return template % makeString(localeKey, params)

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

    def showGasAttackInfo(self, vehsList, cooldowns):
        self.__disabled = True
        self.__selectedVehicleID = None
        slotsStatesData = self.__getSlotsStatesData(vehsList, cooldowns)
        self.as_updateRespawnViewS('', slotsStatesData)
        self.as_showGasAtackMode()
        return

    def py_vehicleSelected(self, vehicleID):
        g_sessionProvider.getRespawnsCtrl().chooseVehicleForRespawn(vehicleID)

    def onPostmortemBtnClickS(self):
        self.hide()

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
            premiumTags = frozenset((VEHICLE_TAGS.PREMIUM,))
            isPremium = bool(v.type.tags & premiumTags)
            result.append({'vehicleID': v.intCD,
             'vehicleName': self.__getVehicleName(v),
             'flagIcon': _FLAG_ICON_TEMPLATE % nations.NAMES[nationID],
             'vehicleIcon': getIconPath(v.type.name),
             'vehicleType': _VEHICLE_TYPE_TEMPLATE % classTag,
             'isElite': False,
             'isPremium': isPremium,
             'vehicleLevel': _VEHICLE_LEVEL_TEMPLATE % v.type.level})

        return result

    def __getGeneralData(self, isLimited):
        if hasResourcePoints():
            helpPanelMode = 'points'
        else:
            helpPanelMode = 'flags'
        respawnMessage = '#ingame_gui:respawnView/additionalTip'
        if isLimited:
            respawnMessage += 'Limited'
        return {'titleMsg': "<font face='$FieldFont' size='32' color='#F4EFE8'>%s</font><font size='4'><br><br></font>%s" % (i18n.makeString(INGAME_GUI.RESPAWNVIEW_TITLE), standard(i18n.makeString(respawnMessage))),
         'helpPanelMode': helpPanelMode,
         'topInfoStr': '',
         'respawnInfoStr': '',
         'isPostmortemViewBtnEnabled': False,
         'postmortemBtnLbl': FALLOUT.INFOPANEL_GARAGE_POSTMORTEMBTNLBL}

    def __getSlotsStatesData(self, vehsList, cooldowns):
        result = []
        for v in vehsList:
            compactDescr = v.intCD
            cooldownTime = cooldowns.get(compactDescr, 0)
            cooldownStr = None
            cooldown = cooldownTime - BigWorld.serverTime()
            enabled = cooldown <= 0 and not self.__disabled
            if not enabled:
                if self.__disabled:
                    cooldownStr = i18n.makeString('#ingame_gui:respawnView/disabledLbl')
                elif cooldownTime > g_sessionProvider.getPeriodCtrl().getEndTime():
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
        vehicleName = vehile.type.shortUserString if isIGR else vehile.type.userString
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
        self._parentObj.movie.falloutItems.as_preinitializeRespawnView()

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
