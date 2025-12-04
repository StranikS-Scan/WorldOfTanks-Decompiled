# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/notification/decorators.py
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from new_year.skeletons.new_year import INewYearController
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_BUTTON_STATE

class NyMessageButtonDecorator(MessageDecorator, IGlobalListener):
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(NyMessageButtonDecorator, self).__init__(entityID, entity, settings, model)
        self.startGlobalListening()
        self._nyController.onStateChanged += self.__doUpdateButtons

    def clear(self):
        self.stopGlobalListening()
        self._nyController.onStateChanged -= self.__doUpdateButtons
        super(NyMessageButtonDecorator, self).clear()

    def onEnqueued(self, queueType, *args):
        self.__doUpdateButtons()

    def onDequeued(self, queueType, *args):
        self.__doUpdateButtons()

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.__doUpdateButtons()

    def _make(self, formatted=None, settings=None):
        self._updateEntityButtons()
        super(NyMessageButtonDecorator, self)._make(formatted, settings)

    def _updateEntityButtons(self):
        if self._entity is None:
            return
        else:
            buttonsLayout = self._entity.get('buttonsLayout')
            if not buttonsLayout:
                return
            buttonsStates = self._entity.get('buttonsStates')
            state, tooltip = self._getButtonState()
            buttonsStates['submit'] = state
            buttonsLayout[0]['tooltip'] = tooltip
            return

    def _getButtonState(self):
        state, tooltip = NOTIFICATION_BUTTON_STATE.DEFAULT, ''
        bodyId = None
        if self.prbEntity is not None and self.prbEntity.isInQueue():
            state = NOTIFICATION_BUTTON_STATE.VISIBLE
            bodyId = R.strings.system_messages.queue.isInQueue()
        elif not self._isButtonEnabled():
            state = NOTIFICATION_BUTTON_STATE.VISIBLE
            if self._nyController.isSuspended():
                bodyId = R.strings.ny.notification.suspend()
            elif self._nyController.isPostEvent():
                bodyId = R.strings.ny.notification.postEvent()
            elif self._nyController.isFinished():
                bodyId = R.strings.ny.notification.finish()
        if bodyId:
            tooltip = makeTooltip(body=backport.text(bodyId))
        return (state, tooltip)

    def _updateButtons(self):
        if self._model is not None:
            self._model.updateNotification(self.getType(), self._entityID, self._entity, False)
        return

    def _isButtonEnabled(self):
        return self._nyController.isEnabled()

    def __doUpdateButtons(self):
        self._updateEntityButtons()
        self._updateButtons()
