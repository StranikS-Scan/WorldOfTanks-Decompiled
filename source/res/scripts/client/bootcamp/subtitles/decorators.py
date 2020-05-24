# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/subtitles/decorators.py


def subtitleDecorator(function):

    def showSubtitle(self, *args, **kwargs):
        if getattr(self.__class__, 'content', False) and self.content and self.content['voiceovers']:
            data = self.content['voiceovers'].pop(0)
            if data['subtitle']:
                if getattr(self.__class__, 'tutorial', False) and self.tutorial is not None:
                    from tutorial.data.effects import HasTargetEffect, EFFECT_TYPE
                    effects = [HasTargetEffect(data['subtitle'], EFFECT_TYPE.SHOW_WINDOW, None)]
                    self.tutorial.storeEffectsInQueue(effects, benefit=True, isGlobal=True)
                    funcEffect = self.tutorial.getFirstElementOfTop()
                    funcEffect.triggerEffect()
                else:
                    from gui.shared.event_dispatcher import showSubtitleWindow
                    showSubtitleWindow(messageVO={'voiceovers': [data]})
            elif data['voiceover']:
                self.soundManager.playSound(data['voiceover'])
        return

    def onCall(self, *args, **kwargs):
        showSubtitle(self, *args, **kwargs)
        return function(self, *args, **kwargs)

    return onCall
