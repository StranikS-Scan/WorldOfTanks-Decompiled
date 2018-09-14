# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/indicators.py
from debug_utils import LOG_DEBUG
from gui import DEPTH_OF_Aim
from gui.battle_control.hit_direction_ctrl import IHitIndicator
from gui.Scaleform.Flash import Flash
_DAMAGE_INDICATOR_SWF = 'DamageIndicator.swf'
_DAMAGE_INDICATOR_COMPONENT = 'WGHitIndicatorFlash'
_DAMAGE_INDICATOR_MC_NAME = 'hit_{0}'
_DAMAGE_INDICATOR_SWF_SIZE = (680, 680)
_DAMAGE_INDICATOR_TOTAL_FRAMES = 90
_DAMAGE_INDICATOR_FRAME_RATE = 24
_DAMAGE_INDICATOR_ANIMATION_DURATION = _DAMAGE_INDICATOR_TOTAL_FRAMES / float(_DAMAGE_INDICATOR_FRAME_RATE)

class _DamageIndicator(Flash, IHitIndicator):

    def __init__(self, hitsCount):
        names = tuple(map(lambda i: _DAMAGE_INDICATOR_MC_NAME.format(i), xrange(hitsCount)))
        Flash.__init__(self, _DAMAGE_INDICATOR_SWF, _DAMAGE_INDICATOR_COMPONENT, (names,))
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_Aim
        self.movie.backgroundAlpha = 0.0
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.active(True)

    def __del__(self):
        LOG_DEBUG('DamageIndicator is deleted')

    def destroy(self):
        self.close()

    def getDuration(self):
        return _DAMAGE_INDICATOR_ANIMATION_DURATION

    def setOffset(self, offset):
        self.component.position.x = offset[0]
        self.component.position.y = offset[1]

    def setVisible(self, flag):
        self.component.visible = flag

    def showHitDirection(self, idx, gYaw, timeLeft, isDamage):
        name = _DAMAGE_INDICATOR_MC_NAME.format(idx)
        self.component.setGlobalYaw(name, gYaw)
        self.component.invoke(name, ('show', [isDamage, timeLeft * _DAMAGE_INDICATOR_FRAME_RATE]))

    def hideHitDirection(self, idx):
        self.component.invoke(_DAMAGE_INDICATOR_MC_NAME.format(idx), ('hide',))


class IndicatorsCollection(object):

    def createDamageIndicator(self, hitsCount):
        return _DamageIndicator(hitsCount)
