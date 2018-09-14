# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/logitech/hangar_screen.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.logitech.LogitechMonitorMeta import LogitechMonitorMonoScreenMeta, LogitechMonitorHangarColoredScreenMeta
from gui.game_control import getFalloutCtrl
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.prb_helpers import GlobalListener
from gui.shared import g_itemsCache
from helpers import i18n
from items.vehicles import getVehicleType

class LogitechMonitorHangarMonoScreen(LogitechMonitorMonoScreenMeta, GlobalListener):

    def _onLoaded(self):
        g_currentVehicle.onChanged += self.__onVehicleChange
        if g_currentVehicle.item:
            self.__updateText()
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        falloutCtrl = getFalloutCtrl()
        if falloutCtrl is not None:
            falloutCtrl.onSettingsChanged += self.__onFalloutSettingsChanged
        self.startGlobalListening()
        return

    def _onUnloaded(self):
        self.stopGlobalListening()
        g_currentVehicle.onChanged -= self.__onVehicleChange
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        falloutCtrl = getFalloutCtrl()
        if falloutCtrl is not None:
            falloutCtrl.onSettingsChanged -= self.__onFalloutSettingsChanged
        return

    def onUnitPlayerStateChanged(self, pInfo):
        self.__onVehicleChange()

    def __onVehicleClientStateChanged(self, vehicles):
        self.__onVehicleChange()

    def __onFalloutSettingsChanged(self):
        self.__onVehicleChange()

    def __onVehicleChange(self):
        self.__updateText()

    def __updateText(self):
        self.as_setText(g_currentVehicle.item.userName + '\r\n' + i18n.makeString(g_currentVehicle.getHangarMessage()[1]))


_TOTAL_BLOCKS = (('common', (('a15x15', 'battlesCount'),
   ('a15x15', 'wins'),
   ('a15x15', 'losses'),
   ('a15x15', 'survivedBattles'))), ('battleeffect', (('a15x15', 'frags'),
   ('max15x15', 'maxFrags'),
   ('', 'effectiveShots'),
   ('a15x15', 'damageDealt'))), ('credits', (('a15x15', 'xp'), ('', 'avgExperience'), ('max15x15', 'maxXP'))))

def _getDossierTotalBlocksSummary(dossier):
    data = []
    for blockType, fields in _TOTAL_BLOCKS:
        for field in fields:
            blockName, fieldType = field
            data.append('#menu:profile/stats/items/' + fieldType)
            data.append(__getData(blockName, fieldType, dossier))
            data.append(__getDataExtra(blockType, blockName, fieldType, dossier))

    return data


def __getData(blockName, fieldType, dossier):
    if fieldType == 'effectiveShots':
        if dossier['a15x15']['shots'] != 0:
            return '%d%%' % round(float(dossier['a15x15']['directHits']) / dossier['a15x15']['shots'] * 100)
        return '0%'
    if fieldType == 'avgExperience':
        if dossier['a15x15']['battlesCount'] != 0:
            return BigWorld.wg_getIntegralFormat(round(float(dossier['a15x15']['xp']) / dossier['a15x15']['battlesCount']))
        return BigWorld.wg_getIntegralFormat(0)
    return BigWorld.wg_getIntegralFormat(dossier[blockName][fieldType])


def __getDataExtra(blockType, blockName, fieldType, dossier):
    extra = ''
    if blockType == 'common':
        if fieldType != 'battlesCount' and dossier['a15x15']['battlesCount'] != 0:
            extra = '(%d%%)' % round(float(dossier[blockName][fieldType]) / dossier['a15x15']['battlesCount'] * 100)
    if fieldType == 'maxFrags' and dossier['max15x15']['maxFrags'] != 0:
        extra = getVehicleType(dossier['max15x15']['maxFragsVehicle']).shortUserString
    if fieldType == 'maxXP' and dossier['max15x15']['maxXP'] != 0:
        extra = getVehicleType(dossier['max15x15']['maxXPVehicle']).shortUserString
    return extra


class LogitechMonitorHangarColoredScreen(LogitechMonitorHangarColoredScreenMeta):

    def _onLoaded(self):
        dossier = g_itemsCache.items.getAccountDossier()
        if dossier is not None:
            dossierDescr = dossier.getDossierDescr()
            statsData = _getDossierTotalBlocksSummary(dossierDescr)
            self.as_setStatsData(statsData)
        else:
            LOG_WARNING("Logitech: Can't get dossier. Hangar screen won't be updated")
        return
