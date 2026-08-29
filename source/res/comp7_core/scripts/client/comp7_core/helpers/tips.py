# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/helpers/tips.py
from __future__ import absolute_import
import typing
from helpers import dependency
from helpers.tips import TipsCriteria, readTips
from skeletons.gui.battle_session import IBattleSessionProvider
from comp7_core_constants import SubMode
_COMP7_NIGHT_MAPS_TIPS_PATTERN = '^(comp7NightMaps\\d+$)'
_comp7NightMapsTips = readTips(_COMP7_NIGHT_MAPS_TIPS_PATTERN)

class Comp7BaseTipsCriteria(TipsCriteria):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _getTargetList(self):
        extraData = self._sessionProvider.arenaVisitor.getArenaExtraData()
        subMode = extraData.get('subMode', SubMode.REGULAR)
        subModeTips = self._getSubModeTips()
        if subMode not in subModeTips:
            subMode = SubMode.REGULAR
        return subModeTips.get(subMode)

    def _getSubModeTips(self):
        return {SubMode.REGULAR: self._getRegularTips(),
         SubMode.NIGHT_MAPS: _comp7NightMapsTips}

    @staticmethod
    def _getRegularTips():
        return []
