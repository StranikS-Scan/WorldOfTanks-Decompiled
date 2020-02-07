# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/session_stats/session_stats_settings.py
import Event
from account_helpers.settings_core.settings_constants import SESSION_STATS
from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_settings_controller import SessionStatsSettingsController, MAX_STATS
from gui.Scaleform.daapi.view.lobby.session_stats.shared import toIntegral
from gui.Scaleform.daapi.view.meta.SessionStatsSettingsMeta import SessionStatsSettingsMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
_EFFICIENCY_BLOCK = {SESSION_STATS.SHOW_WTR: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.wtr()),
                          'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.wtr()))},
 SESSION_STATS.SHOW_RATIO_DAMAGE: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.ratioDamage()),
                                   'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.ratioDamage()))},
 SESSION_STATS.SHOW_RATIO_KILL: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.ratioKill()),
                                 'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.ratioKill()))},
 SESSION_STATS.SHOW_WINS: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.wins()),
                           'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.wins()))},
 SESSION_STATS.SHOW_AVERAGE_DAMAGE: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.averageDamage()),
                                     'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.averageDamage()))},
 SESSION_STATS.SHOW_HELP_DAMAGE: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.helpDamage()),
                                  'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.helpDamage()))},
 SESSION_STATS.SHOW_BLOCKED_DAMAGE: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.blockedDamage()),
                                     'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.blockedDamage()))},
 SESSION_STATS.SHOW_AVERAGE_XP: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.averageXp()),
                                 'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.averageXp()))},
 SESSION_STATS.SHOW_WIN_RATE: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.winRate()),
                               'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.winRate()))},
 SESSION_STATS.SHOW_AVERAGE_VEHICLE_LEVEL: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.averageVehiclesLevel()),
                                            'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.averageVehiclesLevel()))},
 SESSION_STATS.SHOW_AVERAGE_FRAGS: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.averageFrags()),
                                    'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.averageFrags()))},
 SESSION_STATS.SHOW_SURVIVED_RATE: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.survivedRate()),
                                    'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.survivedRate()))},
 SESSION_STATS.SHOW_SPOTTED: {'label': backport.text(R.strings.session_stats.propertyInfo.prop.label.spotted()),
                              'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.propertyInfo.prop.descr.spotted()))}}
_COMMON_BLOCK = {SESSION_STATS.IS_NOT_NEEDED_RESET_STATS_EVERY_DAY: {'label': backport.text(R.strings.session_stats.settings.commonSettings.isNotNeededResetStatsEveryDay()),
                                                     'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.tooltip.settings.commonSettings.isNotNeededResetStatsEveryDay.body()))},
 SESSION_STATS.IS_NEEDED_SAVE_CURRENT_TAB: {'label': backport.text(R.strings.session_stats.settings.commonSettings.saveCurrentTab()),
                                            'tooltip': makeTooltip(body=backport.text(R.strings.session_stats.tooltip.settings.commonSettings.saveCurrentTab.body()))}}
_ECONOMIC_BLOCK_VIEW = {SESSION_STATS.ECONOMIC_BLOCK_VIEW_WITHOUT_SPENDING: {'label': backport.text(R.strings.session_stats.settings.economicBlock.withoutSpending())},
 SESSION_STATS.ECONOMIC_BLOCK_VIEW_WITH_SPENDING: {'label': backport.text(R.strings.session_stats.settings.economicBlock.withSpending())}}

class SessionStatsSettings(SessionStatsSettingsMeta):

    def __init__(self):
        super(SessionStatsSettings, self).__init__()
        self.__sessionStasSettings = SessionStatsSettingsController()
        self.__currentSettings = self.__sessionStasSettings.getSettings()
        self.onShowStats = Event.Event()
        self.__lastChangedIdentifier = None
        return

    def _populate(self):
        super(SessionStatsSettings, self)._populate()
        self.__setSettings()

    def onClickResetBtn(self):
        self.__currentSettings = self.__sessionStasSettings.getDefaultSettings()
        self.__setSettings()
        self.as_setControlsStateS(self.__getControlsData())

    def onClickApplyBtn(self):
        if not self.__currentSettings[SESSION_STATS.IS_NEEDED_SAVE_CURRENT_TAB]:
            self.__currentSettings[SESSION_STATS.CURRENT_TAB] = SESSION_STATS.BATTLES_TAB
        self.__sessionStasSettings.setSettings(self.__currentSettings)
        self.as_setControlsStateS(self.__getControlsData())
        self.onShowStats()

    def onClickBackBtn(self):
        self.onShowStats()

    def onSettingsInputChanged(self, identifier, value):
        self.__lastChangedIdentifier = identifier
        self.__currentSettings[identifier] = value
        self.__setBattleSettingsStatus()
        self.__setSettings()

    def __setSettings(self):
        data = {'header': self.__getHeader(),
         'common': self.__getCommonBlocks(),
         'economics': self.__getEconomicsBlock(),
         'battle': self.__getBattlesBlock()}
        self.as_setDataS(data)
        self.as_setControlsStateS(self.__getControlsData())
        self.__setBattleSettingsStatus()

    def __getHeader(self):
        enableResetBtn = self.__currentSettings != self.__sessionStasSettings.getDefaultSettings()
        return {'title': text_styles.promoSubTitle(backport.text(R.strings.session_stats.settings.header())),
         'resetBtnIcon': RES_ICONS.MAPS_ICONS_STATISTIC_ICON_BUTTON_REFRESH_093,
         'resetBtnTooltip': makeTooltip(header=backport.text(R.strings.session_stats.tooltip.settings.resetBtn.header()), body=backport.text(R.strings.session_stats.tooltip.settings.resetBtn.body())),
         'resetBtnEnabled': enableResetBtn}

    def __getCommonBlocks(self):
        settings = self.__currentSettings
        inputs = []
        for key in SESSION_STATS.getCommonBlock():
            inputs.append({'id': key,
             'label': _COMMON_BLOCK[key]['label'],
             'tooltip': _COMMON_BLOCK[key]['tooltip'],
             'selected': bool(settings[key])})

        return {'title': text_styles.highlightText(backport.text(R.strings.session_stats.settings.commonSettings.header())),
         'inputs': inputs}

    def __getEconomicsBlock(self):
        settings = self.__currentSettings
        inputs = []
        for key in SESSION_STATS.getEconomicBlockView():
            inputs.append({'id': str(key),
             'label': _ECONOMIC_BLOCK_VIEW[key]['label']})

        return {'title': text_styles.highlightText(backport.text(R.strings.session_stats.settings.economicBlock.header())),
         'selectedRadioIndex': settings[SESSION_STATS.ECONOMIC_BLOCK_VIEW],
         'id': SESSION_STATS.ECONOMIC_BLOCK_VIEW,
         'inputs': inputs}

    def __getBattlesBlock(self):
        settings = self.__currentSettings
        inputs = []
        for key in SESSION_STATS.getEfficiencyBlock():
            if key in SESSION_STATS.getImmutableEfficiencyBlockParameters():
                continue
            inputs.append({'id': key,
             'label': _EFFICIENCY_BLOCK[key]['label'],
             'tooltip': _EFFICIENCY_BLOCK[key]['tooltip'],
             'selected': bool(settings[key])})

        return {'title': text_styles.highlightText(backport.text(R.strings.session_stats.settings.efficiencyBlock.header())),
         'inputs': inputs}

    def __getControlsData(self):
        enableApplyBtn = self.__sessionStasSettings.validateSettings(self.__currentSettings)
        warning = {}
        if not enableApplyBtn:
            maxStats = MAX_STATS - len(SESSION_STATS.getImmutableEfficiencyBlockParameters())
            text = backport.text(R.strings.session_stats.settings.efficiencyBlock.error(), max=maxStats)
            warning['text'] = text_styles.alert(text)
            warning['icon'] = backport.image(R.images.gui.maps.icons.library.alertBigIcon())
        else:
            enableApplyBtn = self.__currentSettings != self.__sessionStasSettings.getSettings()
        return {'warning': warning,
         'states': [{'btnEnabled': enableApplyBtn,
                     'btnLabel': backport.text(R.strings.session_stats.settings.controls.applyBtn())}, {'btnEnabled': True,
                     'btnLabel': backport.text(R.strings.session_stats.settings.controls.backBtn())}]}

    def __setBattleSettingsStatus(self):
        if self.__sessionStasSettings.validateSettings(self.__currentSettings):
            textStyle = text_styles.neutral
            warningFlag = False
        else:
            textStyle = text_styles.error
            warningFlag = self.__lastChangedIdentifier in SESSION_STATS.getEfficiencyBlock()
        parameters = list(SESSION_STATS.getEfficiencyBlock())
        for parameter in SESSION_STATS.getImmutableEfficiencyBlockParameters():
            parameters.remove(parameter)

        maxSelectedItems = MAX_STATS - len(SESSION_STATS.getImmutableEfficiencyBlockParameters())
        numberSelectedItems = sum([ self.__currentSettings[key] for key in parameters ])
        self.as_setBattleSettingsStatusS(text_styles.main(backport.text(R.strings.session_stats.settings.efficiencyBlock.subheader(), selected=textStyle(toIntegral(numberSelectedItems)), max=text_styles.main(toIntegral(maxSelectedItems)))), warningFlag)
