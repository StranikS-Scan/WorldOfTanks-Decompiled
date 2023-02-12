# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_secondary_entry_point.py
from gui.Scaleform.daapi.view.meta.SecondaryEntryPointMeta import SecondaryEntryPointMeta
from gui.impl.gen import R
from gui.impl import backport
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.BATTLE_PASS import BATTLE_PASS
from gui.impl.lobby.battle_pass.battle_pass_entry_point_view import BaseBattlePassEntryPointView
_R_TOOLTIPS = R.views.lobby.battle_pass.tooltips
_R_IMAGES = R.images.gui.maps.icons.library.hangarEntryPoints.battlePass
_TOOLTIPS = {_R_TOOLTIPS.BattlePassNotStartedTooltipView(): TOOLTIPS_CONSTANTS.BATTLE_PASS_NOT_STARTED,
 _R_TOOLTIPS.BattlePassCompletedTooltipView(): TOOLTIPS_CONSTANTS.BATTLE_PASS_COMPLETED,
 _R_TOOLTIPS.BattlePassInProgressTooltipView(): TOOLTIPS_CONSTANTS.BATTLE_PASS_IN_PROGRESS,
 _R_TOOLTIPS.BattlePassNoChapterTooltipView(): TOOLTIPS_CONSTANTS.BATTLE_PASS_NO_CHAPTER}

class BattlePassSecondaryEntryPointWidget(SecondaryEntryPointMeta, BaseBattlePassEntryPointView):
    __battlePass = dependency.descriptor(IBattlePassController)
    __slots__ = ('__arenaBonusType',)

    def __init__(self):
        super(BattlePassSecondaryEntryPointWidget, self).__init__()
        self.__arenaBonusType = None
        return

    def onClick(self):
        self._onClick()

    def update(self, currentArenaBonusType):
        self.__arenaBonusType = currentArenaBonusType
        self._updateData()

    def _populate(self):
        super(BattlePassSecondaryEntryPointWidget, self)._populate()
        super(BattlePassSecondaryEntryPointWidget, self)._subscribe()
        self._start()

    def _dispose(self):
        self._stop()
        super(BattlePassSecondaryEntryPointWidget, self)._unsubscribe()
        super(BattlePassSecondaryEntryPointWidget, self)._dispose()

    def _updateData(self, *_):
        super(BattlePassSecondaryEntryPointWidget, self)._updateData()
        if self.__arenaBonusType is None:
            return
        else:
            flagIcon = backport.image(_R_IMAGES.dyn('flag_chapter_{}'.format(self.chapterID), default=_R_IMAGES.flag_default)()) if self.chapterID > 0 else None
            gameModeIsEnabled = self.__battlePass.isGameModeEnabled(self.__arenaBonusType)
            isEnabled = gameModeIsEnabled and self.__battlePass.isActive() and self.__battlePass.isEnabled()
            data = {'flagIcon': flagIcon,
             'icon': self.__getIcon(),
             'altIcon': self.__getAltIcon(isEnabled),
             'extraIcon': self.__getExtraIcon(),
             'text': str(self.level + 1),
             'isEnabled': isEnabled,
             'isBought': self.isBought,
             'chapterID': self.chapterID,
             'points': self.freePoints if self.isCompleted else 0}
            self.__updateTooltipData(data, self.__arenaBonusType, gameModeIsEnabled)
            self.as_setDataS(data)
            if isEnabled:
                self.as_setCountS(self._getNotChosenRewardCount())
            return

    def _getCurrentArenaBonusType(self):
        return self.__arenaBonusType

    def __getIcon(self):
        if self.isBought or self.isCompleted:
            shieldTemplate = 'shield_blue{}{}'
            color = '_gold' if self.isBought else '_silver'
            postfix = ''
            if self.isCompleted and self.freePoints == 0 or not self.__battlePass.hasActiveChapter():
                postfix = '_closed'
            icon = _R_IMAGES.dyn(shieldTemplate.format(color, postfix))()
        else:
            icon = _R_IMAGES.shield_silver() if self.chapterID != 0 else _R_IMAGES.shield_silver_empty()
        return backport.image(icon)

    def __getAltIcon(self, isEnabled):
        if self.chapterID > 0:
            iconTemplate = 'icon_{}_chapter_{}'
            progressionType = 'gold' if self.isBought else 'silver'
            icon = _R_IMAGES.dyn(iconTemplate.format(progressionType, self.chapterID), default=_R_IMAGES.icon_default)()
        elif self.isCompleted:
            icon = _R_IMAGES.icon_completed_gold() if self.isBought else _R_IMAGES.icon_completed_silver()
        else:
            icon = _R_IMAGES.icon_chapter_empty()
        return backport.image(icon)

    def __getExtraIcon(self):
        return backport.image(_R_IMAGES.extra_flags_mini()) if self.hasExtra else None

    def __updateTooltipData(self, data, currentArenaBonusType, gameModeIsEnabled):
        if gameModeIsEnabled and self.__battlePass.isEnabled():
            tooltip = _TOOLTIPS.get(self._getTooltip(), '')
            tooltipType = TOOLTIPS_CONSTANTS.WULF
        elif not self.__battlePass.isEnabled():
            tooltip = BATTLE_PASS.TOOLTIPS_ENTRYPOINT_DISABLED
            tooltipType = TOOLTIPS_CONSTANTS.COMPLEX
        else:
            tooltip = backport.text(R.strings.battle_pass.tooltips.secondaryEntryPoint.disabled.num(currentArenaBonusType)())
            if tooltip:
                tooltipType = TOOLTIPS_CONSTANTS.SIMPLE
            else:
                tooltip = BATTLE_PASS.TOOLTIPS_ENTRYPOINT_DISABLED
                tooltipType = TOOLTIPS_CONSTANTS.COMPLEX
        data['tooltip'] = str(tooltip)
        data['tooltipType'] = tooltipType
