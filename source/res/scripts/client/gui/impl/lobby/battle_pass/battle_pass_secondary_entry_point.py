# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_secondary_entry_point.py
from gui.Scaleform.daapi.view.meta.SecondaryEntryPointMeta import SecondaryEntryPointMeta
from gui.impl.gen import R
from gui.impl import backport
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.BATTLE_PASS_2020 import BATTLE_PASS_2020
from gui.impl.lobby.battle_pass.battle_pass_entry_point_view import BaseBattlePassEntryPointView
_TOOLTIPS = {R.views.lobby.battle_pass.tooltips.BattlePassNotStartedTooltipView(): TOOLTIPS_CONSTANTS.BATTLE_PASS_NOT_STARTED,
 R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView(): TOOLTIPS_CONSTANTS.BATTLE_PASS_COMPLETED,
 R.views.lobby.battle_pass.tooltips.BattlePass3dStyleNotChosenTooltip(): TOOLTIPS_CONSTANTS.BATTLE_PASS_3D_NOT_CHOOSEN,
 R.views.lobby.battle_pass.tooltips.BattlePassInProgressTooltipView(): TOOLTIPS_CONSTANTS.BATTLE_PASS_IN_PROGRESS}

class BattlePassSecondaryEntryPointWidget(SecondaryEntryPointMeta, BaseBattlePassEntryPointView):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __slots__ = ('__arenaBonusType',)

    def __init__(self):
        super(BattlePassSecondaryEntryPointWidget, self).__init__()
        self.__arenaBonusType = None
        return

    def onClick(self):
        self._onClick()

    def update(self, currentArenaBonusType):
        self._updateData()
        currentLevel = ''
        if not self._isCompleted():
            currentLevel = min(self._widgetLevel + 1, self._battlePassController.getMaxLevel())
        self.__arenaBonusType = currentArenaBonusType
        flagIcon = backport.image(R.images.gui.maps.icons.library.hangarEntryPoints.dyn('chapter_{}'.format(self._widgetChapter), R.images.gui.maps.icons.library.hangarEntryPoints.chapter_1)())
        gameModeIsEnabled = self.__battlePassController.isGameModeEnabled(currentArenaBonusType)
        isEnabled = gameModeIsEnabled and self.__battlePassController.isActive() and self.__battlePassController.isEnabled()
        data = {'flagIcon': flagIcon,
         'icon': self.__getIcon(),
         'altIcon': self.__getAltIcon(isEnabled),
         'text': str(currentLevel),
         'isEnabled': isEnabled,
         'isBought': self._isBought(),
         'is3DStyleChosen': self._is3DStyleChosen()}
        self.__updateTooltipData(data, currentArenaBonusType, gameModeIsEnabled)
        self.as_setDataS(data)
        if isEnabled:
            self.as_setCountS(self._getNotChosenRewardCountWith3d())

    def __getIcon(self):
        hangarEntryPoints = R.images.gui.maps.icons.library.hangarEntryPoints
        if self._isBought() or self._isCompleted():
            icon = hangarEntryPoints.bp_entry_icon_purple_gold() if self._isCompleted() else hangarEntryPoints.bp_entry_icon_grey_gold()
        else:
            icon = hangarEntryPoints.bp_entry_icon_brown_silver()
        return backport.image(icon)

    def __getAltIcon(self, isEnabled):
        altIcon = ''
        if not self._is3DStyleChosen() and isEnabled:
            altIcon = backport.image(R.images.gui.maps.icons.library.hangarEntryPoints.c_3dStyles())
        elif self._isCompleted():
            altIcon = backport.image(R.images.gui.maps.icons.library.hangarEntryPoints.completedGold())
        return altIcon

    def __updateTooltipData(self, data, currentArenaBonusType, gameModeIsEnabled):
        if gameModeIsEnabled and self.__battlePassController.isEnabled():
            tooltip = _TOOLTIPS.get(self._getTooltip(), '')
            tooltipType = TOOLTIPS_CONSTANTS.WULF
        elif not self.__battlePassController.isEnabled():
            tooltip = BATTLE_PASS_2020.TOOLTIPS_ENTRYPOINT_DISABLED
            tooltipType = TOOLTIPS_CONSTANTS.COMPLEX
        else:
            tooltip = backport.text(R.strings.battle_pass_2020.tooltips.secondaryEntryPoint.disabled.num(currentArenaBonusType)())
            if tooltip:
                tooltipType = TOOLTIPS_CONSTANTS.SIMPLE
            else:
                tooltip = BATTLE_PASS_2020.TOOLTIPS_ENTRYPOINT_DISABLED
                tooltipType = TOOLTIPS_CONSTANTS.COMPLEX
        data['tooltip'] = str(tooltip)
        data['tooltipType'] = tooltipType

    def __battlePassSettingsChanged(self, *args):
        if self.__arenaBonusType:
            self.update(self.__arenaBonusType)
