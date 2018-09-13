# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortSettingsWindow.py
import BigWorld
from ConnectionManager import connectionManager
from FortifiedRegionBase import FORT_EVENT_TYPE, NOT_ACTIVATED
from adisp import process
from fortified_regions import g_cache as g_fortCache
from constants import FORT_BUILDING_TYPE
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties
from gui.shared import events
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text, fort_formatters
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortSettingsWindowMeta import FortSettingsWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.ClanCache import g_clanCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.fortifications.context import DefencePeriodCtx
from helpers import i18n, time_utils
from predefined_hosts import g_preDefinedHosts

class VIEW_ALIASES:
    DEFENCE_ACTIVATED = FORTIFICATION_ALIASES.FORT_SETTINGS_ACTIVATED_VIEW
    DEFENCE_NOT_ACTIVATED = FORTIFICATION_ALIASES.FORT_SETTINGS_NOTACTIVATED_VIEW


class FortSettingsWindow(View, AbstractWindowView, FortSettingsWindowMeta, AppRef, FortViewHelper):

    def __init__(self):
        super(FortSettingsWindow, self).__init__()
        self.__defencePeriod = False
        self.__isActivatedDisableProcess = False

    def updateData(self):
        fort = self.fortCtrl.getFort()
        inProcess, _ = fort.getDefenceHourProcessing()
        self.__defencePeriod = fort.isDefenceHourEnabled() or inProcess
        self.__isActivatedDisableProcess = fort.isDefenceHourShutDown()
        self.__updateClanInfo()
        self.__updateStatus()
        if self.__defencePeriod:
            self.__updateActivatedView()
        else:
            self.__updateNotActivatedView()
        self.as_setViewS(VIEW_ALIASES.DEFENCE_ACTIVATED if self.__defencePeriod else VIEW_ALIASES.DEFENCE_NOT_ACTIVATED)

    def cancelDisableDefencePeriod(self):
        self.__cancelDefenceHour()

    def disableDefencePeriod(self):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_EVENT), EVENT_BUS_SCOPE.LOBBY)

    def activateDefencePeriod(self):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_EVENT), EVENT_BUS_SCOPE.LOBBY)

    def __updateActivatedView(self):
        result = {'canDisableDefencePeriod': not self.__isActivatedDisableProcess,
         'perepheryContainerVO': self.__makePeripheryData(),
         'settingsBlockVOs': (self.__makeDefencePeriodData(), self.__makeOffDayData(), self.__makeVacationData())}
        self.as_setDataForActivatedS(result)

    def __makePeripheryData(self):
        fort = self.fortCtrl.getFort()
        optionsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
        servername = None
        for key, name, csisStatus, peripheryID in optionsList:
            if fort.peripheryID == peripheryID:
                servername = name

        if servername is None:
            servername = connectionManager.serverUserName
        return {'peripheryTitle': fort_text.getText(fort_text.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_PEREPHERYTITLE)),
         'peripheryName': fort_text.getText(fort_text.NEUTRAL_TEXT, str(servername))}

    def __makeDefencePeriodData(self):
        alertMessage = ''
        blockBtnEnabled = True
        fort = self.fortCtrl.getFort()
        inProcess, inCooldown = fort.getDefenceHourProcessing()
        conditionPostfix = fort_text.getText(fort_text.NEUTRAL_TEXT, fort.getDefencePeriodStr())
        blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DEFENCEBTNENABLED
        if inProcess:
            defenceHourChangeDay, nextDefenceHour, _ = fort.events[FORT_EVENT_TYPE.DEFENCE_HOUR_CHANGE]
            timestampStart = time_utils.getTimeTodayForUTC(nextDefenceHour)
            value = '%s - %s' % (BigWorld.wg_getShortTimeFormat(timestampStart), BigWorld.wg_getShortTimeFormat(timestampStart + time_utils.ONE_HOUR))
            msgString = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_INPROGRESS, value=value, date=BigWorld.wg_getLongDateFormat(defenceHourChangeDay))
            alertMessage = fort_text.getText(fort_text.ALERT_TEXT, msgString)
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DEFENCEBTNDISABLED
        elif inCooldown:
            msgString = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_RECENTLYSCHEDULED)
            alertMessage = fort_text.getText(fort_text.ALERT_TEXT, msgString)
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DEFENCEBTNDISABLED
        conditionPrefix = fort_text.getText(fort_text.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.settingswindow_blockcondition('defencePeriodTime')))
        blockDescr = fort_text.getText(fort_text.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.settingswindow_blockdescr('defencePeriodTime')))
        if alertMessage:
            alertMessage = fort_text.getIcon(fort_text.ALERT_ICON) + ' ' + alertMessage
        return {'blockBtnEnabled': blockBtnEnabled,
         'blockDescr': blockDescr,
         'blockCondition': conditionPrefix + ' ' + conditionPostfix,
         'alertMessage': alertMessage,
         'blockBtnToolTip': blockBtnToolTip}

    def __makeOffDayData(self):
        alertMessage = ''
        blockBtnEnabled = True
        fort = self.fortCtrl.getFort()
        inProcess, inCooldown = fort.getOffDayProcessing()
        conditionPostfix = fort_text.getText(fort_text.NEUTRAL_TEXT, fort.getOffDayStr())
        blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_WEEKENDBTNENABLED
        if inProcess:
            offDayChangeDate, nextOffDay, _ = fort.events[FORT_EVENT_TYPE.OFF_DAY_CHANGE]
            if nextOffDay > NOT_ACTIVATED:
                value = i18n.makeString(MENU.datetime_weekdays_full(str(nextOffDay + 1)))
            else:
                value = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_NOWEEKEND)
            msgString = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_INPROGRESS, value=value, date=BigWorld.wg_getLongDateFormat(offDayChangeDate))
            alertMessage = fort_text.getText(fort_text.ALERT_TEXT, msgString)
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_WEEKENDBTNDISABLED
        elif inCooldown:
            msgString = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_RECENTLYSCHEDULED)
            alertMessage = fort_text.getText(fort_text.ALERT_TEXT, msgString)
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_WEEKENDBTNDISABLED
        conditionPrefix = fort_text.getText(fort_text.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.settingswindow_blockcondition('weekEnd')))
        blockDescr = fort_text.getText(fort_text.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.settingswindow_blockdescr('weekEnd')))
        if alertMessage:
            alertMessage = fort_text.getIcon(fort_text.ALERT_ICON) + ' ' + alertMessage
        return {'blockBtnEnabled': blockBtnEnabled,
         'blockDescr': blockDescr,
         'blockCondition': conditionPrefix + ' ' + conditionPostfix,
         'alertMessage': alertMessage,
         'blockBtnToolTip': blockBtnToolTip}

    def __makeVacationData(self):
        alertMessage = ''
        blockBtnEnabled = True
        dayAfterVacation = 0
        fort = self.fortCtrl.getFort()
        isVacationEnabled = fort.isVacationEnabled()
        inProcess, inCooldown = fort.getVacationProcessing()
        blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONBTNENABLED
        conditionPostfix = fort_text.getText(fort_text.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_VACATIONNOTPLANNED))
        if inProcess:
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONBTNDISABLED
        elif inCooldown:
            blockBtnEnabled = False
            dayAfterVacation = fort.getDaysAfterVacation()
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONBTNDISABLEDNOTPLANNED
        if isVacationEnabled:
            textColor = fort_text.NEUTRAL_TEXT if not fort.isOnVacation() else fort_text.SUCCESS_TEXT
            conditionPostfix = fort_text.getText(textColor, fort.getVacationDateStr())
        conditionPrefix = fort_text.getText(fort_text.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.settingswindow_blockcondition('vacation')))
        blockDescr = fort_text.getText(fort_text.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.settingswindow_blockdescr('vacation')))
        if alertMessage:
            alertMessage = fort_text.getIcon(fort_text.ALERT_ICON) + ' ' + alertMessage
        return {'blockBtnEnabled': blockBtnEnabled,
         'blockDescr': blockDescr,
         'blockCondition': conditionPrefix + ' ' + conditionPostfix,
         'alertMessage': alertMessage,
         'blockBtnToolTip': blockBtnToolTip,
         'dayAfterVacation': dayAfterVacation}

    def __updateNotActivatedView(self):
        description = fort_text.getText(fort_text.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_DESCRIPTION))
        conditionTitle = fort_text.getText(fort_text.MIDDLE_TITLE, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_CONDITIONTITLE))
        firstConditionIcon = fort_text.getIcon(fort_text.CHECKMARK_ICON)
        secondConditionIcon = fort_text.getIcon(fort_text.CHECKMARK_ICON)
        if not self.__checkBaseLevel():
            firstConditionIcon = fort_text.getText(fort_text.STANDARD_TEXT, '-')
        if not self.__checkPlayerCount():
            secondConditionIcon = fort_text.getText(fort_text.STANDARD_TEXT, '-')
        firstConditionMsg = fort_text.getText(fort_text.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_BASELEVELCONDITION, level=fort_formatters.getTextLevel(g_fortCache.defenceConditions.minRegionLevel)))
        secondConditionMsg = fort_text.getText(fort_text.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_PLAYERCOUNTCONDITION, membersCount=BigWorld.wg_getNiceNumberFormat(g_fortCache.defenceConditions.minClanMembers)))
        fortCondition = firstConditionMsg
        secondCondition = secondConditionMsg
        result = {'description': description,
         'conditionTitle': conditionTitle,
         'firstCondition': fortCondition,
         'secondCondition': secondCondition,
         'isBtnEnabled': self.__checkConditions(),
         'btnToolTipData': self.__getButtonToolTip(),
         'firstStatus': firstConditionIcon,
         'secondStatus': secondConditionIcon}
        self.as_setDataForNotActivatedS(result)

    def onWindowClose(self):
        self.destroy()

    def onUpdated(self):
        self.updateData()

    def _populate(self):
        super(FortSettingsWindow, self)._populate()
        self.startFortListening()
        self.updateData()

    def _dispose(self):
        self.stopFortListening()
        super(FortSettingsWindow, self)._dispose()

    def __updateStatus(self):
        prefix = i18n.makeString(FORTIFICATIONS.SETTINGSDEFENCEHOURPOPOVER_DEFENCEHOURTITLE)
        prefix = fort_text.getText(fort_text.HIGH_TITLE, prefix)
        if self._isFortFrozen():
            toolTip = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_STATUSSTRING_FREEZED)
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_ERRORICON_1
            imageSource = self.app._utilsMgr.getHtmlIconText(ImageUrlProperties(icon, 16, 16, -4, 0))
            currentStatus = fort_text.getText(fort_text.ERROR_TEXT, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_STATUSMSG_FREEZED))
            currentStatus = imageSource + ' ' + currentStatus
        elif self.__defencePeriod:
            toolTip = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_STATUSSTRING_ACTIVATED)
            currentStatus = fort_text.concatStyles(((fort_text.CHECKMARK_ICON,), (fort_text.SUCCESS_TEXT, ' ' + i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_STATUSMSG_ACTIVATED))))
        elif self.__checkConditions():
            toolTip = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_STATUSSTRING_CANBEACTIVATED)
            currentStatus = fort_text.concatStyles(((fort_text.ALERT_ICON,), (fort_text.ALERT_TEXT, ' ' + i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_STATUSMSG_NOTACTIVATED))))
        else:
            toolTip = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_STATUSSTRING_CANNOTBEACTIVATED)
            currentStatus = fort_text.concatStyles(((fort_text.NOT_AVAILABLE,), (fort_text.STANDARD_TEXT, ' ' + i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_STATUSMSG_NOTAVAILABLE))))
        self.as_setMainStatusS(prefix, currentStatus, toolTip)

    def __checkConditions(self):
        baseLevel = self.__checkBaseLevel()
        playerCount = self.__checkPlayerCount()
        return baseLevel and playerCount

    def __checkBaseLevel(self):
        return self.fortCtrl.getFort().getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE).level >= g_fortCache.defenceConditions.minRegionLevel

    def __checkPlayerCount(self):
        return len(g_clanCache.clanMembers) >= g_fortCache.defenceConditions.minClanMembers

    def __updateClanInfo(self):
        self.__makeClanInfo()

    @process
    def __makeClanInfo(self):
        enemyClanDBID = g_clanCache.clanDBID
        tID = 'clanInfo%d' % enemyClanDBID
        self.__imageID = yield g_clanCache.getClanEmblemTextureID(enemyClanDBID, True, tID)
        creationDate = BigWorld.wg_getLongDateFormat(self.fortCtrl.getFort().getFortDossier().getGlobalStats().getCreationTime())
        clanTag = g_clanCache.clanTag
        clanTagLocal = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_CLANINFO_CLANTAG, clanTag=clanTag)
        clanTag = fort_text.getText(fort_text.HIGH_TITLE, clanTagLocal)
        creationDateLocalize = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_CLANINFO_CREATIONDATE, creationDate=creationDate)
        creationDate = fort_text.getText(fort_text.NEUTRAL_TEXT, creationDateLocalize)
        buildingsCount = len(self.fortCtrl.getFort().getBuildingsCompleted())
        buildingsCount = fort_text.getText(fort_text.NEUTRAL_TEXT, buildingsCount)
        buildingsCountLocalize = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_CLANINFO_BUILDINGSCOUNT, buildingsCount=str(buildingsCount))
        buildingsCountLocalize = fort_text.getText(fort_text.STANDARD_TEXT, buildingsCountLocalize)
        FortSettingsClanInfoVO = {'clanTag': clanTag,
         'clanIcon': self.__imageID,
         'creationDate': creationDate,
         'buildingCount': buildingsCountLocalize}
        self.as_setFortClanInfoS(FortSettingsClanInfoVO)

    def __getButtonToolTip(self):
        result = ''
        if not self.__checkConditions():
            result = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DISABLEBUTTON
        return result

    @process
    def __cancelDefenceHour(self):
        result = yield self.fortProvider.sendRequest(DefencePeriodCtx(False, waitingID='fort/settings'))
