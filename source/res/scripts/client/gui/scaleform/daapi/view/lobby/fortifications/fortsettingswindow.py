# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortSettingsWindow.py
import BigWorld
from adisp import process
from constants import FORT_BUILDING_TYPE
from helpers import i18n, time_utils
from predefined_hosts import g_preDefinedHosts
from ConnectionManager import connectionManager
from fortified_regions import g_cache as g_fortCache
from FortifiedRegionBase import FORT_EVENT_TYPE, NOT_ACTIVATED
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortSettingsWindowMeta import FortSettingsWindowMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.shared.fortifications.settings import FORT_BATTLE_DIVISIONS
from gui.shared.fortifications.context import DefencePeriodCtx
from gui.shared.fortifications.fort_helpers import adjustOffDayToLocal
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.ClanCache import g_clanCache
from gui.shared.utils.functions import makeTooltip
from gui.shared.formatters import icons, text_styles

class VIEW_ALIASES:
    DEFENCE_ACTIVATED = FORTIFICATION_ALIASES.FORT_SETTINGS_ACTIVATED_VIEW
    DEFENCE_NOT_ACTIVATED = FORTIFICATION_ALIASES.FORT_SETTINGS_NOTACTIVATED_VIEW


class FortSettingsWindow(FortSettingsWindowMeta, FortViewHelper):

    def __init__(self, _ = None):
        super(FortSettingsWindow, self).__init__()
        self.__defencePeriod = False
        self.__isActivatedDisableProcess = False

    def updateData(self):
        fort = self.fortCtrl.getFort()
        inProcess, _ = fort.getDefenceHourProcessing()
        self.__defencePeriod = fort.isDefenceHourEnabled() or inProcess
        self.__isActivatedDisableProcess = fort.isDefenceHourShutDown()
        if self.__defencePeriod:
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
        self.destroy()

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
        if self._isFortFrozen():
            peripheryName = text_styles.standard(str(servername))
        else:
            peripheryName = text_styles.neutral(str(servername))
        return {'peripheryTitle': text_styles.main(i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_PEREPHERYTITLE)),
         'peripheryName': peripheryName,
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
        if self._isFortFrozen():
            conditionPostfix = text_styles.standard(fort.getDefencePeriodStr())
        else:
            conditionPostfix = text_styles.neutral(fort.getDefencePeriodStr())
        blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DEFENCEBTNENABLED
        descriptionTooltip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DEFENCEPERIODDESCRIPTION
        if inProcess:
            defenceHourChangeDay, nextDefenceHour, _ = fort.events[FORT_EVENT_TYPE.DEFENCE_HOUR_CHANGE]
            timestampStart = time_utils.getTimeTodayForUTC(nextDefenceHour)
            value = '%s - %s' % (BigWorld.wg_getShortTimeFormat(timestampStart), BigWorld.wg_getShortTimeFormat(timestampStart + time_utils.ONE_HOUR))
            msgString = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_INPROGRESS, value=value, date=BigWorld.wg_getShortDateFormat(defenceHourChangeDay))
            alertMessage = text_styles.alert(msgString)
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DEFENCEBTNDISABLED
        elif inCooldown:
            msgString = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_RECENTLYSCHEDULED)
            alertMessage = text_styles.alert(msgString)
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_DEFENCEBTNDISABLED
        conditionPrefix = text_styles.main(i18n.makeString(FORTIFICATIONS.settingswindow_blockcondition('defencePeriodTime')))
        blockDescr = text_styles.standard(i18n.makeString(FORTIFICATIONS.settingswindow_blockdescr('defencePeriodTime')))
        if alertMessage:
            alertMessage = icons.alert() + ' ' + alertMessage
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
        dayOff = fort.getOffDayStr()
        if self._isFortFrozen():
            conditionPostfix = text_styles.standard(dayOff)
        else:
            conditionPostfix = text_styles.neutral(dayOff)
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
            alertMessage = text_styles.alert(msgString)
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_WEEKENDBTNDISABLED
        elif inCooldown:
            msgString = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_RECENTLYSCHEDULED)
            alertMessage = text_styles.alert(msgString)
            blockBtnEnabled = False
            blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_WEEKENDBTNDISABLED
        conditionPrefix = text_styles.main(i18n.makeString(FORTIFICATIONS.settingswindow_blockcondition('weekEnd')))
        blockDescr = text_styles.standard(i18n.makeString(FORTIFICATIONS.settingswindow_blockdescr('weekEnd')))
        if alertMessage:
            alertMessage = icons.alert() + ' ' + alertMessage
        return {'blockBtnEnabled': blockBtnEnabled,
         'blockDescr': blockDescr,
         'blockCondition': conditionPrefix + ' ' + conditionPostfix,
         'alertMessage': alertMessage,
         'blockBtnToolTip': blockBtnToolTip,
         'descriptionTooltip': descriptionTooltip}

    def __makeVacationData(self):
        alertMessage = ''
        blockBtnEnabled = True
        daysBeforeVacation = -1
        fort = self.fortCtrl.getFort()
        isVacationEnabled = fort.isVacationEnabled()
        inProcess, inCooldown = fort.getVacationProcessing()
        _, vacationEnd = fort.getVacationDate()
        blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONBTNENABLED
        descriptionTooltip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONDESCRIPTION
        conditionPostfix = text_styles.standard(i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_BLOCKCONDITION_VACATIONNOTPLANNED))
        if inProcess or inCooldown:
            blockBtnEnabled = False
            cooldownEnd = vacationEnd + g_fortCache.vacationCooldownTime
            if fort.isOnVacation():
                blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONBTNDISABLEDNOTPLANNED
                daysBeforeVacation = time_utils.getTimeDeltaFromNow(cooldownEnd) / time_utils.ONE_DAY
            elif time_utils.getTimeDeltaFromNow(vacationEnd) != 0:
                blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONBTNDISABLED
            else:
                daysBeforeVacation = time_utils.getTimeDeltaFromNow(cooldownEnd) / time_utils.ONE_DAY
                if daysBeforeVacation == 0:
                    blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONBTNDSBLDLESSADAY
                    daysBeforeVacation = -1
                else:
                    blockBtnToolTip = TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_VACATIONBTNDISABLEDNOTPLANNED
        if isVacationEnabled:
            vacation = fort.getVacationDateTimeStr()
            if not self._isFortFrozen():
                if not fort.isOnVacation():
                    conditionPostfix = text_styles.neutral(vacation)
                else:
                    conditionPostfix = text_styles.success(vacation)
            else:
                conditionPostfix = text_styles.standard(vacation)
        conditionPrefix = text_styles.main(i18n.makeString(FORTIFICATIONS.settingswindow_blockcondition('vacation')))
        blockDescr = text_styles.standard(i18n.makeString(FORTIFICATIONS.settingswindow_blockdescr('vacation')))
        if alertMessage:
            alertMessage = icons.alert() + ' ' + alertMessage
        return {'blockBtnEnabled': blockBtnEnabled,
         'blockDescr': blockDescr,
         'blockCondition': conditionPrefix + ' ' + conditionPostfix,
         'alertMessage': alertMessage,
         'blockBtnToolTip': blockBtnToolTip,
         'daysBeforeVacation': daysBeforeVacation,
         'descriptionTooltip': descriptionTooltip}

    def __updateNotActivatedView(self):
        _ms = i18n.makeString
        titleText = text_styles.promoTitle(_ms(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_TITLE))
        description = text_styles.main(_ms(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_DESCRIPTION))
        conditionTitle = text_styles.middleTitle(_ms(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_CONDITIONTITLE))
        firstConditionIcon = icons.checkmark()
        secondConditionIcon = icons.checkmark()
        conditionsText = text_styles.middleTitle(_ms(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_CONDITIONS))
        fortConditionsText = text_styles.main(_ms(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_CONDITIONS_FORTLEVEL))
        defenceConditionsText = text_styles.main(_ms(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_CONDITIONS_DEFENCE))
        attackConditionsText = text_styles.main(_ms(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_CONDITIONS_ATTACK))
        firstConditionNotReady = ''
        secondConditionNotReady = ''
        if not self.__checkBaseLevel():
            firstConditionIcon = text_styles.standard('-')
            firstConditionNotReady = text_styles.error(_ms(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_ISNOTREADY))
        if not self.__checkPlayerCount():
            secondConditionIcon = text_styles.standard('-')
            secondConditionNotReady = text_styles.error(_ms(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_ISNOTREADY))
        firstConditionMsg = text_styles.main(_ms(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_BASELEVELCONDITION, level=fort_formatters.getTextLevel(g_fortCache.defenceConditions.minRegionLevel), isNotReady=firstConditionNotReady))
        secondConditionMsg = text_styles.main(_ms(FORTIFICATIONS.SETTINGSWINDOW_NOTACTIVATED_PLAYERCOUNTCONDITION, membersCount=BigWorld.wg_getNiceNumberFormat(g_fortCache.defenceConditions.minClanMembers), isNotReady=secondConditionNotReady))
        fortCondition = firstConditionMsg
        secondCondition = secondConditionMsg
        settingsBlockTop = self.__makeSettingsBlockVO(True)
        settingsBlockBottom = self.__makeSettingsBlockVO(False)
        result = {'titleText': titleText,
         'description': description,
         'conditionTitle': conditionTitle,
         'firstCondition': fortCondition,
         'secondCondition': secondCondition,
         'conditionsText': conditionsText,
         'fortConditionsText': fortConditionsText,
         'defenceConditionsText': defenceConditionsText,
         'attackConditionsText': attackConditionsText,
         'isBtnEnabled': self.__checkConditions(),
         'btnToolTipData': self.__getButtonToolTip(),
         'firstStatus': firstConditionIcon,
         'secondStatus': secondConditionIcon,
         'settingsBlockTop': settingsBlockTop,
         'settingsBlockBottom': settingsBlockBottom}
        self.as_setDataForNotActivatedS(result)

    def __makeSettingsBlockVO(self, isTopBlock):
        if isTopBlock:
            minFortLevel = FORT_BATTLE_DIVISIONS.CHAMPION.minFortLevel
            maxFortLevel = FORT_BATTLE_DIVISIONS.CHAMPION.maxFortLevel
            defenceTankIcon = attackTankIconTop = self.__makeTankIconVO(False, FORT_BATTLE_DIVISIONS.CHAMPION.maxCombatants, RES_ICONS.MAPS_ICONS_LIBRARY_USA_A12_T32, fort_formatters.getIconLevel(FORT_BATTLE_DIVISIONS.CHAMPION.iconLevel), FORT_BATTLE_DIVISIONS.CHAMPION.divisionID)
            attackTankIconBottom = self.__makeTankIconVO(True, FORT_BATTLE_DIVISIONS.ABSOLUTE.maxCombatants, RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_USSR_T62A, fort_formatters.getIconLevel(FORT_BATTLE_DIVISIONS.ABSOLUTE.iconLevel), FORT_BATTLE_DIVISIONS.ABSOLUTE.divisionID)
        else:
            minFortLevel = FORT_BATTLE_DIVISIONS.ABSOLUTE.minFortLevel
            maxFortLevel = FORT_BATTLE_DIVISIONS.ABSOLUTE.maxFortLevel
            defenceTankIcon = attackTankIconTop = self.__makeTankIconVO(False, FORT_BATTLE_DIVISIONS.ABSOLUTE.maxCombatants, RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_USSR_T62A, fort_formatters.getIconLevel(FORT_BATTLE_DIVISIONS.ABSOLUTE.iconLevel), FORT_BATTLE_DIVISIONS.ABSOLUTE.divisionID)
            attackTankIconBottom = self.__makeTankIconVO(True, FORT_BATTLE_DIVISIONS.CHAMPION.maxCombatants, RES_ICONS.MAPS_ICONS_LIBRARY_USA_A12_T32, fort_formatters.getIconLevel(FORT_BATTLE_DIVISIONS.CHAMPION.iconLevel), FORT_BATTLE_DIVISIONS.CHAMPION.divisionID)
        return {'startLvlSrc': fort_formatters.getIconLevel(minFortLevel),
         'endLvlSrc': fort_formatters.getIconLevel(maxFortLevel),
         'buildingIcon': FortViewHelper.getSmallIconSource(FORTIFICATION_ALIASES.FORT_BASE_BUILDING, maxFortLevel),
         'lvlDashTF': text_styles.stats('-'),
         'defenceTankIcon': defenceTankIcon,
         'attackTankIconTop': attackTankIconTop,
         'attackTankIconBottom': attackTankIconBottom}

    @staticmethod
    def __makeTankIconVO(showAlert, valueText, tankIconSource, lvlIconSource, divisionID):
        return {'showAlert': showAlert,
         'valueText': str(valueText),
         'tankIconSource': tankIconSource,
         'lvlIconSource': lvlIconSource,
         'divisionID': divisionID}

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        if reason == BUILDING_UPDATE_REASON.UPGRADED and buildingTypeID == FORT_BUILDING_TYPE.MILITARY_BASE:
            if self.fortCtrl.getFort().getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE).level == FORT_BATTLE_DIVISIONS.CHAMPION.minFortLevel:
                self.updateData()

    def onClanMembersListChanged(self):
        self.updateData()

    def onWindowClose(self):
        self.destroy()

    def onShutdownDowngrade(self):
        self.as_setCanDisableDefencePeriodS(not self.fortCtrl.getFort().isDefenceHourShutDown())

    def onDefenceHourShutdown(self):
        self.as_setCanDisableDefencePeriodS(not self.fortCtrl.getFort().isDefenceHourShutDown())

    def onDefenceHourChanged(self, hour):
        self.updateData()

    def onDefenceHourActivated(self, hour, initiatorDBID):
        if not self.__defencePeriod:
            self.destroy()
        else:
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
        prefix = text_styles.highTitle(prefix)
        if self._isFortFrozen():
            toolTip = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_STATUSSTRING_FREEZED)
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_ERRORICON_1
            imageSource = icons.makeImageTag(icon, 16, 16, -4, 0)
            currentStatus = text_styles.error(i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_STATUSMSG_FREEZED))
            currentStatus = imageSource + ' ' + currentStatus
        elif self.__defencePeriod:
            toolTip = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_STATUSSTRING_ACTIVATED)
            currentStatus = ''.join((icons.checkmark(), text_styles.success(' ' + i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_STATUSMSG_ACTIVATED))))
        elif self.__checkConditions():
            toolTip = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_STATUSSTRING_CANBEACTIVATED)
            currentStatus = ''.join((icons.alert(), text_styles.alert(' ' + i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_STATUSMSG_NOTACTIVATED))))
        else:
            toolTip = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTSETTINGSWINDOW_STATUSSTRING_CANNOTBEACTIVATED)
            currentStatus = ''.join((icons.notAvailable(), text_styles.standard(' ' + i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_STATUSMSG_NOTAVAILABLE))))
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
        clanTag = text_styles.highTitle(clanTagLocal)
        creationDateLocalize = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_CLANINFO_CREATIONDATE, creationDate=creationDate)
        creationDate = text_styles.neutral(creationDateLocalize)
        buildingsCount = len(self.fortCtrl.getFort().getBuildingsCompleted())
        buildingsCount = text_styles.neutral(buildingsCount)
        buildingsCountLocalize = i18n.makeString(FORTIFICATIONS.SETTINGSWINDOW_CLANINFO_BUILDINGSCOUNT, buildingsCount=str(buildingsCount))
        buildingsCountLocalize = text_styles.standard(buildingsCountLocalize)
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
