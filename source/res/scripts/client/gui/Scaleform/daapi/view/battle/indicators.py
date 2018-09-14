# Python bytecode 2.7 (decompiled from Python 2.7)
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
_DIRECT_INDICATOR_SWF = 'DirectionIndicator.swf'
_DIRECT_INDICATOR_COMPONENT = 'WGDirectionIndicatorFlash'
_DIRECT_INDICATOR_MC_NAME = 'directionalIndicatorMc'
_DIRECT_INDICATOR_SWF_SIZE = (680, 680)
_DIRECT_INDICATOR_MESSAGE_SWF = 'DirectionIndicatorMessage.swf'

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


class IDirectionIndicator(object):

    def track(self, position):
        pass

    def setShape(self, shape):
        pass

    def setDistance(self, distance):
        pass

    def setPosition(self, position):
        pass

    def remove(self):
        pass


class _DirectionIndicator(Flash, IDirectionIndicator):

    def __init__(self, swf):
        super(_DirectionIndicator, self).__init__(swf, _DIRECT_INDICATOR_COMPONENT, (_DIRECT_INDICATOR_MC_NAME,))
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_Aim
        self.movie.backgroundAlpha = 0.0
        self.movie.scaleMode = 'NoScale'
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.flashSize = _DIRECT_INDICATOR_SWF_SIZE
        self.__isVisible = True
        self.component.relativeRadius = 0.5
        self._dObject = getattr(self.movie, _DIRECT_INDICATOR_MC_NAME, None)
        return

    def __del__(self):
        LOG_DEBUG('DirectionIndicator deleted')

    def setShape(self, shape):
        if self._dObject:
            self._dObject.setShape(shape)

    def setDistance(self, distance):
        if self._dObject:
            self._dObject.setDistance(distance)

    def setPosition(self, position):
        self.component.position3D = position

    def track(self, position):
        self.active(True)
        self.component.visible = True
        self.component.position3D = position

    def remove(self):
        self._dObject = None
        self.close()
        return

    @classmethod
    def _getSWF(cls):
        return _DIRECT_INDICATOR_SWF

    def setVisibility(self, isVisible):
        if not self.__isVisible == isVisible:
            self.__isVisible = isVisible
            self.component.visible = isVisible


class _DirectionIndicatorMessage(_DirectionIndicator):

    def setMessage(self, message):
        if self._dObject:
            self._dObject.setMessage(message)


def createDirectIndicator():
    return _DirectionIndicator(_DIRECT_INDICATOR_SWF)


def createDirectIndicatorMessage():
    return _DirectionIndicatorMessage(_DIRECT_INDICATOR_MESSAGE_SWF)
