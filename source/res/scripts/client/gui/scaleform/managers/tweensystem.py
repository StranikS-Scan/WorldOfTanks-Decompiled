# Embedded file name: scripts/client/gui/Scaleform/managers/TweenSystem.py
from gui.Scaleform.framework.entities.abstract.TweenManagerMeta import TweenManagerMeta
import BigWorld
import time
import math
import Math
from debug_utils import LOG_ERROR
import resource_helper
import ResMgr
TWEEN_CONSTRAINTS_FILE_PATH = 'gui/tween_constraints.xml'
ERROR_NOT_SUCH_FILE = 'Not such file '
REQUIRED_PARAMETERS = ['moveDuration',
 'fadeDuration',
 'shadowDuration',
 'blinkingDuration',
 'translationLength',
 'fadeAlphaMax',
 'fadeAlphaMin',
 'halfTurnDuration',
 'halfTurnDelay']

class TweenManager(TweenManagerMeta):
    THRESHOLD_VALUE_IN_CURRENT_FRAME = 15

    def __init__(self):
        super(TweenManager, self).__init__()
        self.__settings = {}
        self.__id = 0
        self.__animCallback = None
        self.__lastUpdateTime = None
        self.__tweens = []
        self.__playStack = []
        self.__callBackTime = 0.02
        self.__lastStartTime = 0
        self.__loadTweenConstraintsXML()
        return

    def _populate(self):
        super(TweenManager, self)._populate()
        self.as_setDataFromXmlS(self.__settings)

    def __loadTweenConstraintsXML(self):
        if ResMgr.isFile(TWEEN_CONSTRAINTS_FILE_PATH):
            ctx, section = resource_helper.getRoot(TWEEN_CONSTRAINTS_FILE_PATH)
            settings = {}
            for ctx, subSection in resource_helper.getIterator(ctx, section):
                item = resource_helper.readItem(ctx, subSection, name='setting')
                settings[item.name] = item.value

            self.__settings.update(settings)
            self.__checkRequiredValues(self.__settings)
        else:
            LOG_ERROR(ERROR_NOT_SUCH_FILE, TWEEN_CONSTRAINTS_FILE_PATH)

    def __checkRequiredValues(self, settings):
        for key in REQUIRED_PARAMETERS:
            if key not in settings:
                LOG_ERROR('In the ' + TWEEN_CONSTRAINTS_FILE_PATH + ' there is no required parameter ' + key)

    def __onTweenStarted(self, tween):
        if not self.isTweenInStack(tween):
            tweenData = tween.getDataForAnim()
            if tweenData[3][_AbstractTween.ALPHA] != 0:
                self.__playStack.insert(0, tweenData)
            else:
                self.__playStack.append(tweenData)
        if self.__animCallback is None:
            self.__animCallback = BigWorld.callback(self.__callBackTime, self.__updatePosition)
            self.__lastUpdateTime = time.time() * 1000
        if int(time.time() * 1000) - self.__lastStartTime <= TweenManager.THRESHOLD_VALUE_IN_CURRENT_FRAME:
            self.__lastUpdateTime = time.time() * 1000
        self.__lastStartTime = int(time.time() * 1000)
        return

    def isTweenInStack(self, tween):
        tweenIdx = tween.getTweenIdx()
        countTweens = len(self.__playStack)
        for index in range(countTweens):
            tweenData = self.__playStack[index]
            curTweenIdx = tweenData[6]
            if curTweenIdx == tweenIdx:
                return True

        return False

    def __clearPlayStackElement(self, element):
        index = len(element)
        while index > 0:
            element.pop()
            index -= 1

    def _dispose(self):
        if self.__animCallback is not None:
            BigWorld.cancelCallback(self.__animCallback)
            self.__animCallback = None
        index = len(self.__playStack)
        self.disposeAll()
        self.__tweens = None
        self.__playStack = None
        self.__propsInUse = None
        super(TweenManager, self)._dispose()
        return

    def createTween(self, tween):
        if tween.isOnCodeBased:
            tweenPY = _PythonTween(self.__id)
        else:
            tweenPY = _FlashTween(self.__id)
        self.__id += 1
        tweenPY.onTweenStart += self.__onTweenStarted
        tweenPY.setFlashObject(tween)
        self.__tweens.append(tweenPY)

    def pauseAllTween(self):
        for tween in self.__playStack:
            tween.setPaused(True)

    def playAllTween(self):
        for tween in self.__playStack:
            tween.setPaused(False)

    def disposeAll(self):
        index = len(self.__playStack)
        while index > 0:
            self.__clearPlayStackElement(self.__playStack[0])
            self.__playStack.pop(0)
            index -= 1

        for tween in self.__tweens:
            tween.onTweenStart -= self.__onTweenStarted
            tween.destroy()

        self.__tweens = []
        if self.__animCallback is not None:
            BigWorld.cancelCallback(self.__animCallback)
        self.__animCallback = None
        return

    def resetAllTweens(self):
        for tween in self.__playStack:
            tween.reset()

    def disposeTween(self, tweenOnDispose):
        tweenIdx = tweenOnDispose.getTweenIdx()
        countTweens = len(self.__tweens)
        tween = None
        for index in range(countTweens):
            tween = self.__tweens[index]
            curTweenIdx = tween.getTweenIdx()
            if curTweenIdx == tweenIdx:
                tween.onTweenStart -= self.__onTweenStarted
                del self.__tweens[index]
                break

        countTweens = len(self.__playStack)
        for index in range(countTweens):
            tweenData = self.__playStack[index]
            curTweenIdx = tweenData[6]
            if curTweenIdx == tweenIdx:
                self.__clearPlayStackElement(self.__playStack[index])
                del self.__playStack[index]
                break

        tween.destroy()
        return

    def checkAnimProps(self, startData, deltaData, ratio):
        result = {}
        for propsName in _AbstractTween.PROPS_IN_USE:
            if deltaData[propsName] != 0:
                result[propsName] = startData[propsName] + deltaData[propsName] * ratio

        if _AbstractTween.SCALE_X in result and _AbstractTween.SCALE_Y not in result:
            result[_AbstractTween.SCALE_Y] = startData[_AbstractTween.SCALE_Y]
        if _AbstractTween.SCALE_Y in result and _AbstractTween.SCALE_X not in result:
            result[_AbstractTween.SCALE_X] = startData[_AbstractTween.SCALE_X]
        if _AbstractTween.Y in result and _AbstractTween.X not in result:
            result[_AbstractTween.X] = startData[_AbstractTween.X]
        if _AbstractTween.X in result and _AbstractTween.Y not in result:
            result[_AbstractTween.Y] = startData[_AbstractTween.Y]
        return result

    def __updatePosition(self):
        locLastUpdateTime = self.__lastUpdateTime
        self.__lastUpdateTime = time.time() * 1000
        self.__animCallback = BigWorld.callback(self.__callBackTime, self.__updatePosition)
        tweenIdx = 0
        while tweenIdx < len(self.__playStack):
            tweenData = self.__playStack[tweenIdx]
            tween = tweenData[0]
            target = tweenData[1]
            startData = tweenData[2]
            deltaData = tweenData[3]
            delay = tweenData[4]
            duration = tweenData[5]
            if tween.isComplete:
                if tween.getLoop():
                    tween.resetAnim()
                    tween.setPaused(False)
                else:
                    self.__clearPlayStackElement(self.__playStack[tweenIdx])
                    del self.__playStack[tweenIdx]
                    if len(self.__playStack) == 0:
                        BigWorld.cancelCallback(self.__animCallback)
                        self.__animCallback = None
                tween.complete()
            elif tween.getPaused():
                self.__clearPlayStackElement(self.__playStack[tweenIdx])
                del self.__playStack[tweenIdx]
                if len(self.__playStack):
                    tweenIdx -= 1
                else:
                    BigWorld.cancelCallback(self.__animCallback)
                    self.__animCallback = None
            else:
                position = tween.position
                deltaTime = self.__lastUpdateTime - locLastUpdateTime
                position += deltaTime
                tween.position = position
                if position > 0:
                    ratio = position / duration
                    if ratio >= 1:
                        tween.isComplete = True
                        ratio = 1
                    tween.setPropToTargetDO(self.checkAnimProps(startData, deltaData, ratio), ratio)
                tweenIdx += 1

        return


from debug_utils import LOG_WARNING
import Event
from gui.Scaleform.framework.entities.abstract.AbstractTweenMeta import AbstractTweenMeta

class _AbstractTween(AbstractTweenMeta):
    PAUSED = 'paused'
    LOOP = 'loop'
    EASE = 'ease'
    ON_COMPLETE = 'onComplete'
    TARGET = 'target'
    DURATION = 'duration'
    DELAY = 'delay'
    SCALE_X = 'scaleX'
    SCALE_Y = 'scaleY'
    ALPHA = 'alpha'
    ROTATION = 'rotation'
    X = 'x'
    Y = 'y'
    NAN = 'nan'
    PROPS_IN_USE = {X: True,
     Y: True,
     ROTATION: True,
     SCALE_X: True,
     SCALE_Y: True,
     ALPHA: True}

    def __init__(self, idx):
        super(_AbstractTween, self).__init__()
        self.__tweenIdx = idx
        self.__target = None
        self.__duration = 0
        self.__delay = 0
        self.isComplete = True
        self.position = 0
        self.ease = None
        self.__loop = False
        self.__paused = True
        self.__animTargetProps = {}
        self.__propsFromNextAnim = {}
        self.__startTargetProps = {}
        self.__deltaTargetProps = {}
        self.__currentAngle = 0
        self.__isPostponedStarted = False
        self.onTweenStart = Event.Event()
        return

    def setPropToTargetDO(self, props, ratio):
        pass

    def _populate(self):
        super(_AbstractTween, self)._populate()

    def postponedCheckState(self):
        self.__isPostponedStarted = True
        if not self.__paused:
            self.onTweenStart(self)

    def _dispose(self):
        self.__animTargetProps = None
        self.__deltaTargetProps = None
        self.__startTargetProps = None
        self.__propsFromNextAnim = None
        self.__target = None
        self.__duration = None
        self.__delay = None
        self.__loop = None
        self.isComplete = None
        self.__paused = None
        self.position = None
        self.ease = None
        self.onTweenStart.clear()
        self.onTweenStart = None
        super(_AbstractTween, self)._dispose()
        return

    def getTweenIdx(self):
        return self.__tweenIdx

    def __applyQuickSet(self, quickSet):
        self.isComplete = False
        getPaused = getattr(quickSet, 'getPaused', None)
        getLoop = getattr(quickSet, 'getLoop', None)
        getDelay = getattr(quickSet, 'getGlobalDelay', None)
        if getPaused is not None:
            self.setPaused(getPaused())
        if getLoop is not None:
            self.setLoop(getLoop())
        if getDelay is not None:
            self.setDelay(getDelay())
        return

    def __createStartProps(self, target):
        matrix = target.displayMatrix
        info = target.getDisplayInfo()
        return {_AbstractTween.X: info.x,
         _AbstractTween.Y: info.y,
         _AbstractTween.SCALE_X: info.xScale / 100,
         _AbstractTween.SCALE_Y: info.yScale / 100,
         _AbstractTween.ALPHA: info.alpha,
         _AbstractTween.ROTATION: matrix.roll}

    def __creatDeltaData(self):
        deltaProps = {}
        for prop in _AbstractTween.PROPS_IN_USE.keys():
            if self.__animTargetProps.has_key(prop) and self.__animTargetProps[prop] is not None:
                deltaProps[prop] = self.__animTargetProps[prop] - self.__startTargetProps[prop]
            else:
                deltaProps[prop] = 0

        return deltaProps

    def __createAnimPropsFromObject(self, newProps):
        resultProps = {}
        for propName in _AbstractTween.PROPS_IN_USE.keys():
            propValue = getattr(newProps, propName, None)
            if propValue is not None and not str(propValue) == _AbstractTween.NAN:
                resultProps[propName] = propValue

        return resultProps

    def __setNewPropsOnAnimComplete(self):
        if self.isComplete:
            props = self.__propsFromNextAnim
            if _AbstractTween.DURATION in props:
                self.setDuration(props[_AbstractTween.DURATION])
            if _AbstractTween.DELAY in props:
                self.setDelay(props[_AbstractTween.DELAY])
                self.setPosition(-1 * self.__delay)
            if _AbstractTween.TARGET in props:
                self.setTarget(props[_AbstractTween.TARGET])
            for propsName in _AbstractTween.PROPS_IN_USE:
                if propsName in self.__propsFromNextAnim:
                    self.__animTargetProps[propsName] = self.__propsFromNextAnim[propsName]

            self.__deltaTargetProps = self.__creatDeltaData()
            self.__propsFromNextAnim = {}

    def initialiaze(self, props):
        self.__target = self.getTargetDisplayObjectS()
        props.setTweenIdx(self.__tweenIdx)
        if self.__target:
            self.__startTargetProps = self.__createStartProps(self.__target)
        duration = props.getDuration()
        if not duration == 0:
            self.setDuration(duration)
        self.__animTargetProps = self.__createAnimPropsFromObject(props)
        self.__deltaTargetProps = self.__creatDeltaData()
        self.__applyQuickSet(props)

    def getStartData(self):
        return self.__startTargetProps

    def getDeltaData(self):
        return self.__deltaTargetProps

    def getPaused(self):
        return self.__paused

    def setPaused(self, paused):
        if not self.__paused == paused:
            if not paused and self.__isPostponedStarted:
                self.onTweenStart(self)
            self.__paused = paused

    def getLoop(self):
        return self.__loop

    def setLoop(self, loop):
        self.__loop = loop

    def getDuration(self):
        return self.__duration

    def setDuration(self, duration):
        if duration == 0:
            LOG_WARNING('Duration will be more than 0')
            return
        if self.isComplete:
            self.__duration = duration
        else:
            self.__propsFromNextAnim[_AbstractTween.DURATION] = duration

    def getPosition(self):
        return self.position

    def setPosition(self, position):
        self.position = position

    def complete(self):
        self.onAnimCompleteS()

    def getDelay(self):
        return self.__delay

    def setDelay(self, delay):
        if self.isInStart():
            self.__delay = delay
            self.setPosition(-self.getDelay())
        else:
            self.__propsFromNextAnim[_AbstractTween.DELAY] = delay

    def getTarget(self):
        return self.__target

    def setTarget(self, target):
        if self.isInStart():
            self.__target = target
            self.__startTargetProps = self.__createStartProps(target)
            self.__deltaTargetProps = self.__creatDeltaData()
        else:
            self.__propsFromNextAnim[_AbstractTween.TARGET] = target

    def getIsComplete(self):
        return self.isComplete

    def getPosition(self):
        return self.position

    def setPosition(self, position):
        self.position = position

    def getEasy(self):
        return self.__easy

    def setEasy(self, easy):
        if self.isInStart():
            self.__easy = easy
        else:
            self.__propsFromNextAnim[_AbstractTween.EASE] = easy

    def getFinishX(self):
        return self.__animTargetProps[_AbstractTween.X]

    def setFinishX(self, valueX):
        if self.isInStart():
            self.__animTargetProps[_AbstractTween.X] = valueX
        else:
            self.__propsFromNextAnim[_AbstractTween.X] = valueX

    def getFinishY(self):
        return self.__animTargetProps[_AbstractTween.Y]

    def setFinishY(self, valueY):
        if self.isInStart():
            self.__animTargetProps[_AbstractTween.Y] = valueY
        else:
            self.__propsFromNextAnim[_AbstractTween.Y] = valueY

    def getFinishScaleX(self):
        return self.__animTargetProps[_AbstractTween.SCALE_Y]

    def setFinishScaleX(self, valueScaleX):
        if self.isInStart():
            self.__animTargetProps[_AbstractTween.SCALE_X] = valueScaleX
        else:
            self.__propsFromNextAnim[_AbstractTween.SCALE_X] = valueScaleX

    def getFinishScaleY(self):
        return self.__animTargetProps[_AbstractTween.SCALE_Y]

    def setFinishScaleY(self, valueScaleY):
        if self.isInStart():
            self.__animTargetProps[_AbstractTween.SCALE_Y] = valueScaleY
        else:
            self.__propsFromNextAnim[_AbstractTween.SCALE_Y] = valueScaleY

    def getFinishAlpha(self):
        return self.__animTargetProps[_AbstractTween.ALPHA]

    def setFinishAlpha(self, valueAlpha):
        if self.isInStart():
            self.__animTargetProps[_AbstractTween.ALPHA] = valueAlpha * 100
        else:
            self.__propsFromNextAnim[_AbstractTween.ALPHA] = valueAlpha * 100

    def getFinishRotation(self):
        return self.__animTargetProps[_AbstractTween.ROTATION] * 180 / math.pi

    def setFinishRotation(self, valueRotation):
        if self.isInStart():
            self.__animTargetProps[_AbstractTween.ROTATION] = valueRotation * math.pi / 180
            self.__creatDeltaData()
        else:
            self.__propsFromNextAnim[_AbstractTween.ROTATION] = valueRotation * math.pi / 180

    def resetAnim(self):
        self.setPosition(-self.getDelay())
        self.__setNewPropsOnAnimComplete()
        self.setPaused(True)
        self.isComplete = False

    def isInStart(self):
        if self.position == -self.getDelay():
            return True
        else:
            return False

    def getDataForAnim(self):
        resultData = [self,
         self.__target,
         self.getStartData(),
         self.getDeltaData(),
         self.getDelay(),
         self.getDuration(),
         self.__tweenIdx]
        return resultData


from gui.Scaleform.framework.entities.abstract.PythonTweenMeta import PythonTweenMeta

class _PythonTween(_AbstractTween, PythonTweenMeta):

    def __init__(self, idx):
        super(_PythonTween, self).__init__(idx)

    def setPropToTargetDO(self, data, ratio):
        target = self.getTarget()
        info = target.getDisplayInfo()
        self.resetMatrix(target)
        matrix = target.displayMatrix
        translation = matrix.translation
        if _AbstractTween.ALPHA in data:
            info.alpha = data[_AbstractTween.ALPHA]
            info.x = translation.x
            info.y = translation.y
            target.setDisplayInfo(info)
        matrixProps = set([_AbstractTween.X,
         _AbstractTween.Y,
         _AbstractTween.ROTATION,
         _AbstractTween.SCALE_X,
         _AbstractTween.SCALE_Y])
        if len(set(data.keys()).intersection(matrixProps)) > 0:
            if _AbstractTween.ROTATION in data:
                matrixRotation = Math.Matrix()
                matrixRotation.setRotateZ(-data[_AbstractTween.ROTATION] - matrix.roll)
                matrix.preMultiply(matrixRotation)
            if _AbstractTween.X in data:
                matrixTranslation = Math.Matrix()
                matrixTranslation.setTranslate((data[_AbstractTween.X] - translation.x, data[_AbstractTween.Y] - translation.y, 0))
                matrix.preMultiply(matrixTranslation)
            target.displayMatrix = matrix
            self.resetDisplayInfo(target)

    def resetMatrix(self, target):
        displayInfo = target.getDisplayInfo()
        matrixTranslation = Math.Matrix()
        matrix = target.displayMatrix
        translation = matrix.translation
        x = round(displayInfo.x, 1) - round(translation.x, 1)
        y = round(displayInfo.y, 1) - round(translation.y, 1)
        matrixTranslation.setTranslate((x, y, 1))
        matrix.postMultiply(matrixTranslation)
        target.displayMatrix = matrix

    def resetDisplayInfo(self, target):
        displayInfo = target.getDisplayInfo()
        translation = target.displayMatrix.translation
        displayInfo.x = translation.x
        displayInfo.y = translation.y
        target.setDisplayInfo(displayInfo)

    def complete(self):
        super(_PythonTween, self).complete()


from gui.Scaleform.framework.entities.abstract.FlashTweenMeta import FlashTweenMeta

class _FlashTween(_AbstractTween, FlashTweenMeta):

    def __init__(self, idx):
        super(_FlashTween, self).__init__(idx)

    def setPropToTargetDO(self, data, ratio):
        self.moveOnPositionS(round(ratio * 100))
