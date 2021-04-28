# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/attention_effect_player.py
import BigWorld

class AttentionEffectPlayer(object):
    __slots__ = ('__viewRef', '__callbackID', '__delayTime', '__isPlaying')

    def __init__(self, viewRef):
        super(AttentionEffectPlayer, self).__init__()
        self.__viewRef = viewRef
        self.__callbackID = None
        self.__delayTime = self._setDelayTime()
        self.__isPlaying = False
        return

    def setVisible(self, visible):
        if visible:
            if self.__callbackID is not None or self.__isPlaying:
                self.__stopEffect()
            self.__startTimer()
        else:
            self.__stopEffect()
        return

    def destroy(self):
        self.__viewRef = None
        self.__disposeTimer()
        return

    def _setDelayTime(self):
        raise NotImplementedError

    def __startTimer(self):
        self.__callbackID = BigWorld.callback(self.__delayTime, self.__onDelayFinished)

    def __disposeTimer(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __stopAnimation(self):
        if self.__isPlaying:
            self.__viewRef.hideNotificationAnim()
            self.__isPlaying = False

    def __stopEffect(self):
        self.__disposeTimer()
        self.__stopAnimation()

    def __onDelayFinished(self):
        self.__callbackID = None
        self.__isPlaying = True
        self.__viewRef.showNotificationAnim()
        return
