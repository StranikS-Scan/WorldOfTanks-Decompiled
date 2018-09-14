# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/SwitchModePanel.py
from constants import ARENA_GUI_TYPE_LABEL
from gui.Scaleform.daapi.view.meta.SwitchModePanelMeta import SwitchModePanelMeta
from gui.Scaleform.genConsts.FALLOUT_ALIASES import FALLOUT_ALIASES
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.prb_getters import getArenaGUIType
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.game_control import IFalloutController

class SwitchModePanel(SwitchModePanelMeta):
    falloutCtrl = dependency.descriptor(IFalloutController)

    def _populate(self):
        super(SwitchModePanel, self)._populate()
        self.falloutCtrl.onSettingsChanged += self.__updateFalloutSettings
        self.falloutCtrl.onAutomatchChanged += self.__updateFalloutSettings
        self.__updateFalloutSettings()

    def _dispose(self):
        self.falloutCtrl.onSettingsChanged -= self.__updateFalloutSettings
        self.falloutCtrl.onAutomatchChanged -= self.__updateFalloutSettings
        super(SwitchModePanel, self)._dispose()

    def switchMode(self):
        g_eventBus.handleEvent(events.LoadViewEvent(FALLOUT_ALIASES.FALLOUT_BATTLE_SELECTOR_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def onSelectCheckBoxAutoSquad(self, isSelected):
        self.falloutCtrl.setAutomatch(isSelected)

    def __updateFalloutSettings(self):
        battleType = self.falloutCtrl.getBattleType()
        isVisible = self.falloutCtrl.canChangeBattleType() and self.falloutCtrl.isSelected()
        if isVisible:
            self.as_setDataS({'iconSource': '../maps/icons/battleTypes/64x64/%s.png' % ARENA_GUI_TYPE_LABEL.LABELS[getArenaGUIType(queueType=battleType)],
             'buttonLabel': FALLOUT.HANGARSWITCH_BTNLBL,
             'label': text_styles.middleTitle('#fallout:hangarSwitch/%d' % battleType),
             'autoSquadEnabled': self.falloutCtrl.isAutomatch(),
             'autoSquadLabel': FALLOUT.FALLOUTBATTLESELECTORWINDOW_AUTOSQUAD_LABEL,
             'autoSquadInfoTooltip': makeTooltip(TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_INFO_HEADER, TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_INFO_BODY, attention=TOOLTIPS.FALLOUTBATTLESELECTORWINDOW_INFO_ALERT),
             'autoSquadIsVisible': self.falloutCtrl.canAutomatch()})
        self.as_setVisibleS(isVisible)
