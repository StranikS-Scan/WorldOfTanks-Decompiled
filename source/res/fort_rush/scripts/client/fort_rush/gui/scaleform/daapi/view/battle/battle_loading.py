# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/battle_loading.py
from __future__ import absolute_import
import random
from account_helpers.settings_core.options import BattleLoadingTipSetting
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading
_FORT_RUSH_TIP_ICONS = tuple((backport.image(R.images.fort_rush.gui.maps.icons.battle_loading.dyn('tip_{:02d}'.format(index))()) for index in range(1, 4)))
_FORT_RUSH_TIP_TEXT = ((R.strings.fort_rush.battleLoading.tips.tip01.title(), R.strings.fort_rush.battleLoading.tips.tip01.description()), (R.strings.fort_rush.battleLoading.tips.tip02.title(), R.strings.fort_rush.battleLoading.tips.tip02.description()), (R.strings.fort_rush.battleLoading.tips.tip03.title(), R.strings.fort_rush.battleLoading.tips.tip03.description()))

class FortRushBattleLoading(BattleLoading):

    def __init__(self):
        super(FortRushBattleLoading, self).__init__()
        self.__tipIndex = random.randrange(len(_FORT_RUSH_TIP_ICONS))
        self.__tipIcon = _FORT_RUSH_TIP_ICONS[self.__tipIndex]

    def _setTipsInfo(self):
        super(FortRushBattleLoading, self)._setTipsInfo()
        titleRes, descriptionRes = _FORT_RUSH_TIP_TEXT[self.__tipIndex]
        self.as_setTipTitleS(self._formatTipTitle(backport.text(titleRes)))
        self.as_setTipS(self._formatTipBody(backport.text(descriptionRes)))

    def _makeVisualTipVO(self, arenaDP, tip=None):
        vo = super(FortRushBattleLoading, self)._makeVisualTipVO(arenaDP, tip)
        settingID = BattleLoadingTipSetting.OPTIONS.VISUAL
        vo.update({'settingID': settingID,
         'tipIcon': self.__tipIcon,
         'showMinimap': False,
         'showTableBackground': False,
         'showTipsBackground': True})
        vo.update(self._getViewSettingByID(settingID))
        return vo
