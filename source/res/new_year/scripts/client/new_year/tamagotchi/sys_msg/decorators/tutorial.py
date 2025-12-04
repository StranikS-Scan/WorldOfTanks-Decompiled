# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/tamagotchi/sys_msg/decorators/tutorial.py
from helpers import dependency
from helpers.events_handler import EventsHandler
from new_year.skeletons.new_year import ITamagotchiDataProvider
from notification.decorators import MessageDecorator

class NyTutorialMsgDecorator(MessageDecorator, EventsHandler):
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(NyTutorialMsgDecorator, self).__init__(entityID, entity, settings, model)
        self._subscribe()

    def clear(self):
        self._unsubscribe()
        super(NyTutorialMsgDecorator, self).clear()

    def _getEvents(self):
        return ((self._dataProvider.onViewVisibilityChanged, self.__removeNotification), (self._dataProvider.onOnboardingChanged, self.__removeNotification))

    def __removeNotification(self, isVisible):
        if not isVisible:
            self._model.removeNotification(self.getType(), self._entityID)
