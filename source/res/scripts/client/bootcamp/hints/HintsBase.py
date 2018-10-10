# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/hints/HintsBase.py


class HINT_COMMAND(object):
    SHOW = 0
    SHOW_COMPLETED = 1
    SHOW_COMPLETED_WITH_HINT = 2
    HIDE = 3


class HintBase(object):
    STATE_INACTIVE = 0
    STATE_DEFAULT = 1
    STATE_HINT = 2
    STATE_COMPLETE = 3

    def __init__(self, avatar, hintTypeId, timeout):
        super(HintBase, self).__init__()
        self._avatar = avatar
        self._timeStart = 0
        self._timeout = timeout
        self.__message = ''
        self.__voiceover = None
        self._state = HintBase.STATE_INACTIVE
        self.typeId = hintTypeId
        self.timeCompleted = 3.0
        self.cooldownAfter = 3.0
        return

    def start(self):
        pass

    def stop(self):
        pass

    def destroy(self):
        self._avatar = None
        return

    def update(self):
        return None

    def onAction(self, actionId, actionParams):
        pass

    @property
    def message(self):
        return self.__message

    @message.setter
    def message(self, message):
        self.__message = message

    @property
    def voiceover(self):
        return self.__voiceover

    @voiceover.setter
    def voiceover(self, voiceover):
        self.__voiceover = voiceover
