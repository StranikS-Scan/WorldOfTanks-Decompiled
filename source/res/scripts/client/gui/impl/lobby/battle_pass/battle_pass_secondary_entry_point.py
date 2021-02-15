# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_secondary_entry_point.py
from gui.Scaleform.daapi.view.meta.SecondaryEntryPointMeta import SecondaryEntryPointMeta
from gui.impl.gen import R
from gui.impl import backport
from gui.server_events.events_dispatcher import showMissionsBattlePassCommonProgression
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from gui.battle_pass.battle_pass_helpers import getCurrentLevel
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS

class BattlePassSecondaryEntryPointWidget(SecondaryEntryPointMeta):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __slots__ = ('__arenaBonusType',)

    def __init__(self):
        super(BattlePassSecondaryEntryPointWidget, self).__init__()
        self.__arenaBonusType = None
        return

    def _populate(self):
        super(BattlePassSecondaryEntryPointWidget, self)._populate()
        self.__battlePassController.onBattlePassSettingsChange += self.__battlePassSettingsChanged

    def _dispose(self):
        self.__battlePassController.onBattlePassSettingsChange -= self.__battlePassSettingsChanged
        super(BattlePassSecondaryEntryPointWidget, self)._dispose()

    def onClick(self):
        showMissionsBattlePassCommonProgression()

    def update(self, currentArenaBonusType):
        self.__arenaBonusType = currentArenaBonusType
        bgIcon = backport.image(R.images.gui.maps.icons.library.hangarEntryPoints.bp_entry_bg_green())
        icon = backport.image(R.images.gui.maps.icons.library.hangarEntryPoints.bp_entry_icon_brown_silver())
        isEnabled = self.__battlePassController.isGameModeEnabled(currentArenaBonusType)
        data = {'bgIcon': bgIcon,
         'icon': icon,
         'text': str(getCurrentLevel()),
         'isEnabled': isEnabled}
        self.__updateTooltipData(data, currentArenaBonusType)
        self.as_setDataS(data)

    def __updateTooltipData(self, data, currentArenaBonusType):
        if data['isEnabled']:
            tooltip = TOOLTIPS_CONSTANTS.BATTLE_PASS_IN_PROGRESS
            tooltipType = TOOLTIPS_CONSTANTS.WULF
        else:
            tooltip = backport.text(R.strings.battle_pass_2020.tooltips.secondaryEntryPoint.disabled.num(currentArenaBonusType)())
            tooltipType = TOOLTIPS_CONSTANTS.SIMPLE
        data['tooltip'] = tooltip
        data['tooltipType'] = tooltipType

    def __battlePassSettingsChanged(self, *args):
        if self.__arenaBonusType:
            self.update(self.__arenaBonusType)
