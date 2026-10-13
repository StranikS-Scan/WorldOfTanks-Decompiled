# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/crosshair/plugins.py
from __future__ import absolute_import
import typing
from future.utils import itervalues
from FortRushDamageResistanceComponent import FortRushDamageResistanceComponent
from aih_constants import SHOT_RESULT
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import ShotResultIndicatorPlugin
if typing.TYPE_CHECKING:
    from aih_constants import GunMarkerState
SHOT_RESULT_INDICATOR = 'shotResultIndicator'

def createPlugins():
    return {SHOT_RESULT_INDICATOR: _FortRushShotResultIndicatorPlugin}


class _FortRushShotResultIndicatorPlugin(ShotResultIndicatorPlugin):

    def _getShotResolverResult(self, gunMarker):
        collision = gunMarker.collData
        if collision and collision.entity:
            for dynCmp in itervalues(collision.entity.dynamicComponents):
                if isinstance(dynCmp, FortRushDamageResistanceComponent):
                    return SHOT_RESULT.NOT_PIERCED

        return super(_FortRushShotResultIndicatorPlugin, self)._getShotResolverResult(gunMarker=gunMarker)
