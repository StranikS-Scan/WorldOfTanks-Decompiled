# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/HintLink.py


class HintLink(object):

    def __init__(self, hintTypeId, timeCompleted, cooldownAfter, message, startDelay, duration, innerCooldown, completeDuration, voiceover):
        self.hintTypeId = hintTypeId
        self.timeCompleted = timeCompleted
        self.cooldownAfter = cooldownAfter
        self.message = message
        self.voiceover = voiceover
        self.timeStartDelay = startDelay
        self.timeDuration = duration
        self.timeInnerCooldown = innerCooldown
        self.timeCompleteDuration = completeDuration
        self.hintObject = None
        return

    def show(self):
        if self.hintObject is not None:
            self.hintObject.show()
        return

    def hide(self):
        if self.hintObject is not None:
            self.hintObject.hide()
        return

    def complete(self):
        if self.hintObject is not None:
            self.hintObject.complete()
        return

    def disable(self):
        if self.hintObject is not None:
            self.hintObject.disable()
        return

    isVisible = property(lambda self: self.hintObject.isVisible() if self.hintObject is not None else False)
    isActive = property(lambda self: self.hintObject.isActive() if self.hintObject is not None else False)
    isNotShown = property(lambda self: self.hintObject.isNotShown() if self.hintObject is not None else False)
    isComplete = property(lambda self: self.hintObject.isComplete() if self.hintObject is not None else False)
    isDisabled = property(lambda self: self.hintObject.isDisabled() if self.hintObject is not None else False)
