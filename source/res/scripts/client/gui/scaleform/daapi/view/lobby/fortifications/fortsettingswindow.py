# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortSettingsWindow.py
import BigWorld
from ConnectionManager import connectionManager
from FortifiedRegionBase import FORT_EVENT_TYPE, NOT_ACTIVATED
from adisp import process
from fortified_regions import g_cache as g_fortCache
from constants import FORT_BUILDING_TYPE
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties
from gui.shared import events
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
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
from gui.shared.fortifications.fort_helpers import adjustOffDayToLocal
from gui.shared.utils.functions import makeTooltip

class VIEW_ALIASES:
    DEFENCE_ACTIVATED = FORTIFICATION_ALIASES.FORT_SETTINGS_ACTIVATED_VIEW
    DEFENCE_NOT_ACTIVATED = FORTIFICATION_ALIASES.FORT_SETTINGS_NOTACTIVATED_VIEW


class FortSettingsWindow(View, AbstractWindowView, FortSettingsWindowMeta, AppRef, FortViewHelper):

    def __init__(self, ctx = None):
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
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_ALIAS), EVENT_BUS_SCOPE.LOBBY)

    def activateDefencePeriod(self):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_ALIAS), EVENT_BUS_SCOPE.LOBBY)

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
        _, inCooldown = fort.getPeripheryProcessing()
        timestamp, _, _ = fort.events.get(FORT_EVENT_TYPE.PERIPHERY_COOLDOWN, (0, 0, 0))
        buttonEnabled = not inCooldown
        buttonToolTip = self.__makePeripheryBtnToolTip(buttonEnabled, time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(timestamp)))
        descriptionTooltip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_PERIPHERYDESCRIPTION
        return {'peripheryTitle': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_PEREPHERYTITLE)),
         'peripheryName': self.app.utilsManager.textManager.getText(TextType.NEUTRAL_TEXT, str(servername)),
         'buttonEnabled': buttonEnabled,
         'buttonToolTip': buttonToolTip,
         'descriptionTooltip': descriptionTooltip}

    def __makePeripheryBtnToolTip(self, btnEnabled, timeLeft):
        ttHeader = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_PEREPHERYBTN_HEADER
        if btnEnabled:
            ttBody = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_PEREPHERYBTN_ENABLED_BODY
        else:
            ttBody = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_PEREPHERYBTN_DISABLED_BODY, period=time_utils.getTillTimeString(timeLeft, MENU.TIME_TIMEVALUE))
        return makeTooltip(ttHeader, ttBody)

    def __makeDefencePeriodData(self):
        alertMessage = ''
        blockBtnEnabled = True
        fort = self.fortCtrl.getFort()
        inProcess, inCooldown = fort.getDefenceHourProcessing()
        conditionPostfix = self.app.utilsManager.textManager.getText(TextType.NEUTRAL_TEXT, fort.getDefencePeriodStr())
        blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DEFENCEBTNENABLED
        descriptionTooltip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DEFENCEPERIODDESCRIPTION
        if inProcess:
            defenceHourChangeDay, nextDefenceHour, _ = fort.events[FORT_EVENT_TYPE.DEFENCE_HOUR_CHANGE]
            timestampStart = time_utils.getTimeTodayForUTC(nextDefenceHour)
            value = '%s - %s' % (BigWorld.wg_getShortTimeFormat(timestampStart), BigWorld.wg_getShortTimeFormat(timestampStart + time_utils.ONE_HOUR))
            msgString = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_INPROGRESS, value=value, date=BigWorld.wg_getShortDateFormat(defenceHourChangeDay))
            alertMessage = self.app.utilsManager.textManager.getText(TextType.ALERT_TEXT, msgString)
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DEFENCEBTNDISABLED
        elif inCooldown:
            msgString = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_RECENTLYSCHEDULED)
            alertMessage = self.app.utilsManager.textManager.getText(TextType.ALERT_TEXT, msgString)
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DEFENCEBTNDISABLED
        conditionPrefix = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.settingswindow_blockcondition('defencePeriodTime')))
        blockDescr = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.settingswindow_blockdescr('defencePeriodTime')))
        if alertMessage:
            alertMessage = self.app.utilsManager.textManager.getIcon(TextIcons.ALERT_ICON) + ' ' + alertMessage
        return {'blockBtnEnabled': blockBtnEnabled,
         'blockDescr': blockDescr,
         'blockCondition': conditionPrefix + ' ' + conditionPostfix,
         'alertMessage': alertMessage,
         'blockBtnToolTip': blockBtnToolTip,
         'descriptionTooltip': descriptionTooltip}

    def __makeOffDayData(self):
        alertMessage = ''
        blockBtnEnabled = True
        fort = self.fortCtrl.getFort()
        inProcess, inCooldown = fort.getOffDayProcessing()
        conditionPostfix = self.app.utilsManager.textManager.getText(TextType.NEUTRAL_TEXT, fort.getOffDayStr())
        blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_WEEKENDBTNENABLED
        descriptionTooltip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DAYOFFDESCRIPTION
        if inProcess:
            offDayChangeDate, nextOffDayUTC, _ = fort.events[FORT_EVENT_TYPE.OFF_DAY_CHANGE]
            nextOffDayLocal = adjustOffDayToLocal(nextOffDayUTC, self.fortCtrl.getFort().getLocalDefenceHour()[0])
            if nextOffDayLocal > NOT_ACTIVATED:
                value = i18n.makeString(MENU.datetime_weekdays_full(str(nextOffDayLocal + 1)))
            else:
                value = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_NOWEEKEND)
            msgString = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_INPROGRESS, value=value, date=BigWorld.wg_getLongDateFormat(offDayChangeDate))
            alertMessage = self.app.utilsManager.textManager.getText(TextType.ALERT_TEXT, msgString)
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_WEEKENDBTNDISABLED
        elif inCooldown:
            msgString = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_RECENTLYSCHEDULED)
            alertMessage = self.app.utilsManager.textManager.getText(TextType.ALERT_TEXT, msgString)
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_WEEKENDBTNDISABLED
        conditionPrefix = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.settingswindow_blockcondition('weekEnd')))
        blockDescr = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.settingswindow_blockdescr('weekEnd')))
        if alertMessage:
            alertMessage = self.app.utilsManager.textManager.getIcon(TextIcons.ALERT_ICON) + ' ' + alertMessage
        return {'blockBtnEnabled': blockBtnEnabled,
         'blockDescr': blockDescr,
         'blockCondition': conditionPrefix + ' ' + conditionPostfix,
         'alertMessage': alertMessage,
         'blockBtnToolTip': blockBtnToolTip,
         'descriptionTooltip': descriptionTooltip}

    def __makeVacationData(self):
        alertMessage = ''
        blockBtnEnabled = True
        dayAfterVacation = 0
        fort = self.fortCtrl.getFort()
        isVacationEnabled = fort.isVacationEnabled()
        inProcess, inCooldown = fort.getVacationProcessing()
        blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONBTNENABLED
        descriptionTooltip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONDESCRIPTION
        conditionPostfix = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_VACATIONNOTPLANNED))
        if inProcess:
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONBTNDISABLED
        elif inCooldown:
            blockBtnEnabled = False
            dayAfterVacation = fort.getDaysAfterVacation()
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONBTNDISABLEDNOTPLANNED
        if isVacationEnabled:
            textColor = TextType.NEUTRAL_TEXT if not fort.isOnVacation() else TextType.SUCCESS_TEXT
            conditionPostfix = self.app.utilsManager.textManager.getText(textColor, fort.getVacationDateStr())
        conditionPrefix = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.settingswindow_blockcondition('vacation')))
        blockDescr = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.settingswindow_blockdescr('vacation')))
        if alertMessage:
            alertMessage = self.app.utilsManager.textManager.getIcon(TextIcons.ALERT_ICON) + ' ' + alertMessage
        return {'blockBtnEnabled': blockBtnEnabled,
         'blockDescr': blockDescr,
         'blockCondition': conditionPrefix + ' ' + conditionPostfix,
         'alertMessage': alertMessage,
         'blockBtnToolTip': blockBtnToolTip,
         'dayAfterVacation': dayAfterVacation,
         'descriptionTooltip': descriptionTooltip}

    def __updateNotActivatedView(self):
        description = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_DESCRIPTION))
        conditionTitle = self.app.utilsManager.textManager.getText(TextType.MIDDLE_TITLE, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_CONDITIONTITLE))
        firstConditionIcon = self.app.utilsManager.textManager.getIcon(TextIcons.CHECKMARK_ICON)
        secondConditionIcon = self.app.utilsManager.textManager.getIcon(TextIcons.CHECKMARK_ICON)
        if not self.__checkBaseLevel():
            firstConditionIcon = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, '-')
        if not self.__checkPlayerCount():
            secondConditionIcon = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, '-')
        firstConditionMsg = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_BASELEVELCONDITION, level=fort_formatters.getTextLevel(g_fortCache.defenceConditions.minRegionLevel)))
        secondConditionMsg = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_PLAYERCOUNTCONDITION, membersCount=BigWorld.wg_getNiceNumberFormat(g_fortCache.defenceConditions.minClanMembers)))
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

    def onShutdownDowngrade(self):
        self.as_setCanDisableDefencePeriodS(not self.fortCtrl.getFort().isDefenceHourShutDown())

    def onDefenceHourShutdown(self):
        self.as_setCanDisableDefencePeriodS(not self.fortCtrl.getFort().isDefenceHourShutDown())

    def onDefenceHourChanged(self, hour):
        self.updateData()

    def onOffDayChanged(self, offDay):
        self.updateData()

    def onPeripheryChanged(self, peripheryID):
        self.updateData()

    def onVacationChanged(self, vacationStart, vacationEnd):
        self.updateData()

    def onSettingCooldown(self, eventTypeID):
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
        prefix = self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, prefix)
        if self._isFortFrozen():
            toolTip = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_STATUSSTRING_FREEZED)
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_ERRORICON_1
            imageSource = self.app._utilsMgr.getHtmlIconText(ImageUrlProperties(icon, 16, 16, -4, 0))
            currentStatus = self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_STATUSMSG_FREEZED))
            currentStatus = imageSource + ' ' + currentStatus
        elif self.__defencePeriod:
            toolTip = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_STATUSSTRING_ACTIVATED)
            currentStatus = self.app.utilsManager.textManager.concatStyles(((TextIcons.CHECKMARK_ICON,), (TextType.SUCCESS_TEXT, ' ' + i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_STATUSMSG_ACTIVATED))))
        elif self.__checkConditions():
            toolTip = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_STATUSSTRING_CANBEACTIVATED)
            currentStatus = self.app.utilsManager.textManager.concatStyles(((TextIcons.ALERT_ICON,), (TextType.ALERT_TEXT, ' ' + i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_STATUSMSG_NOTACTIVATED))))
        else:
            toolTip = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_STATUSSTRING_CANNOTBEACTIVATED)
            currentStatus = self.app.utilsManager.textManager.concatStyles(((TextIcons.NOT_AVAILABLE,), (TextType.STANDARD_TEXT, ' ' + i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_STATUSMSG_NOTAVAILABLE))))
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
        clanTag = self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, clanTagLocal)
        creationDateLocalize = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_CLANINFO_CREATIONDATE, creationDate=creationDate)
        creationDate = self.app.utilsManager.textManager.getText(TextType.NEUTRAL_TEXT, creationDateLocalize)
        buildingsCount = len(self.fortCtrl.getFort().getBuildingsCompleted())
        buildingsCount = self.app.utilsManager.textManager.getText(TextType.NEUTRAL_TEXT, buildingsCount)
        buildingsCountLocalize = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_CLANINFO_BUILDINGSCOUNT, buildingsCount=str(buildingsCount))
        buildingsCountLocalize = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, buildingsCountLocalize)
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
        if result:
            self.as_setCanDisableDefencePeriodS(True)
