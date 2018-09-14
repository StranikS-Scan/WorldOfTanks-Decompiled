# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/SwitchModePanel.py
from gui.Scaleform.daapi.view.meta.SwitchModePanelMeta import SwitchModePanelMeta
from gui.Scaleform.genConsts.FALLOUT_ALIASES import FALLOUT_ALIASES
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.game_control import getFalloutCtrl
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils.functions import makeTooltip

class SwitchModePanel(SwitchModePanelMeta):

    def __init__(self):
        super(SwitchModePanel, self).__init__()
        self.__falloutCtrl = None
        return

    def _populate(self):
        super(SwitchModePanel, self)._populate()
        self.__falloutCtrl = getFalloutCtrl()
        self.__falloutCtrl.onSettingsChanged += self.__updateFalloutSettings
        self.__falloutCtrl.onAutomatchChanged += self.__updateFalloutSettings
        self.__updateFalloutSettings()

    def _dispose(self):
        self.__falloutCtrl.onSettingsChanged -= self.__updateFalloutSettings
        self.__falloutCtrl.onAutomatchChanged -= self.__updateFalloutSettings
        self.__falloutCtrl = None
        super(SwitchModePanel, self)._dispose()
        return

    def switchMode(self):
        g_eventBus.handleEvent(events.LoadViewEvent(FALLOUT_ALIASES.FALLOUT_BATTLE_SELECTOR_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def onSelectCheckBoxAutoSquad(self, isSelected):
        self.__falloutCtrl.setAutomatch(isSelected)

    def __updateFalloutSettings(self):
        battleType = self.__falloutCtrl.getBattleType()
        isVisible = self.__falloutCtrl.canChangeBattleType() and self.__falloutCtrl.isSelected()
        if isVisible:
            self.as_setDataS({'iconSource': RES_ICONS.MAPS_ICONS_BATTLETYPES_64X64_FALLOUT,
             'buttonLabel': FALLOUT.HANGARSWITCH_BTNLBL,
             'label': text_styles.middleTitle('#fallout:hangarSwitch/%d' % battleType),
             'autoSquadEnabled': self.__falloutCtrl.isAutomatch(),
             'autoSquadLabel': FALLOUT.FALLOUTBATTLESELECTORWINDOW_AUTOSQUAD_LABEL,
             'autoSquadInfoTooltip': makeTooltip(TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_INFO_HEADER, TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_INFO_BODY, attention=TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_INFO_ALERT),
             'autoSquadIsVisible': self.__falloutCtrl.canAutomatch()})
        self.as_setVisibleS(isVisible)
