# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_secondary_entry_point.py
from gui.Scaleform.daapi.view.meta.SecondaryEntryPointMeta import SecondaryEntryPointMeta
from gui.impl.gen import R
from gui.impl import backport
from gui.shared.utils.functions import makeComplexTooltipByResource
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IBattlePassController
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.battle_pass.battle_pass_entry_point_view import BaseBattlePassEntryPointView
from gui.battle_pass.battle_pass_helpers import getIsBpPointsShopEntryPointActive
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
            isPointsVisible = self.isCompleted and getIsBpPointsShopEntryPointActive()
            data = {'flagIcon': flagIcon,
             'icon': self.__getIcon(),
             'altIcon': self.__getAltIcon(isEnabled),
             'extraIcon': self.__getExtraIcon(),
             'text': str(self.level + 1),
             'isEnabled': isEnabled,
             'isBought': self.isBought,
             'isPaused': self.isPaused,
             'chapterID': self.chapterID,
             'points': self.freePoints if isPointsVisible else 0}
            self.__updateTooltipData(data, self.__arenaBonusType, gameModeIsEnabled)
            self.as_setDataS(data)
            if not self.__battlePass.isDisabled():
                self.as_setCountS(self._getNotChosenRewardCount())
            return

    def _getCurrentArenaBonusType(self):
        return self.__arenaBonusType

    def __getChapterID(self):
        availableChapter = first(self.__battlePass.getChapterIDs())
        return availableChapter if self.__battlePass.isSingleChapter() else self.chapterID

    def __getIcon(self):
        isCompleted = self.isCompleted
        isBought = self.isBought
        isMarathonChapter = self.__battlePass.isMarathonChapter(self.chapterID)
        chapterID = self.__getChapterID()
        shieldTemplate = 'shield{}{}{}'
        customShieldTemplate = 'c_{}_shield{}{}{}'
        plateColor = '_normal'
        borderColor = '_gold' if isBought else '_silver'
        postfix = '' if self.__battlePass.hasActiveChapter() or isCompleted and self.freePoints > 0 else '_closed'
        if isMarathonChapter:
            plateColor = '_marathon'
        elif isBought or isCompleted:
            plateColor = '_blue'
        customIcon = _R_IMAGES.dyn(customShieldTemplate.format(chapterID, plateColor, borderColor, postfix), default=_R_IMAGES.dyn(shieldTemplate.format(plateColor, borderColor, postfix)))()
        return backport.image(customIcon)

    def __getAltIcon(self, isEnabled):
        progressionType = 'gold' if self.isBought else 'silver'
        customIcon = None
        if self.chapterID > 0:
            iconTemplate = 'icon_{}_chapter_{}'
            icon = _R_IMAGES.dyn(iconTemplate.format(progressionType, self.chapterID), default=_R_IMAGES.icon_default)()
        elif self.isCompleted:
            chapterID = self.__getChapterID()
            customIconTemplate = 'c_{}_icon_completed_{}'
            iconTemplate = 'icon_completed_{}'
            icon = _R_IMAGES.dyn(iconTemplate.format(progressionType))()
            customIcon = _R_IMAGES.dyn(customIconTemplate.format(chapterID, progressionType), default=_R_IMAGES.dyn(iconTemplate.format(progressionType)))()
        else:
            icon = _R_IMAGES.icon_chapter_empty()
        return backport.image(customIcon) if customIcon else backport.image(icon)

    def __getExtraIcon(self):
        if self.hasMarathon:
            return backport.image(_R_IMAGES.extra_flags_mini())
        else:
            return backport.image(_R_IMAGES.resource_decor()) if self.isResourceAvailable else None

    def __updateTooltipData(self, data, currentArenaBonusType, gameModeIsEnabled):
        if gameModeIsEnabled and self.__battlePass.isEnabled():
            tooltip = _TOOLTIPS.get(self._getTooltip(), '')
            tooltipType = TOOLTIPS_CONSTANTS.WULF
        elif not self.__battlePass.isEnabled():
            tooltip = makeComplexTooltipByResource(R.strings.battle_pass.tooltips.entryPoint.disabled)
            tooltipType = TOOLTIPS_CONSTANTS.COMPLEX
        else:
            tooltip = backport.text(R.strings.battle_pass.tooltips.secondaryEntryPoint.disabled.num(currentArenaBonusType)())
            if tooltip:
                tooltipType = TOOLTIPS_CONSTANTS.SIMPLE
            else:
                tooltip = makeComplexTooltipByResource(R.strings.battle_pass.tooltips.entryPoint.disabled)
                tooltipType = TOOLTIPS_CONSTANTS.COMPLEX
        data['tooltip'] = tooltip
        data['tooltipType'] = tooltipType
