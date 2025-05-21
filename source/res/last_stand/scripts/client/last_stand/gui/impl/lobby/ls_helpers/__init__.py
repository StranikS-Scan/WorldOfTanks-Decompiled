# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/ls_helpers/__init__.py
from functools import wraps
from BWUtil import AsyncReturn
from last_stand.skeletons.ls_controller import ILSController
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from wg_async import wg_await, wg_async, forwardAsFuture

@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def isQuestCompleted(questID, eventsCache=None):
    quest = eventsCache.getAllQuests().get(questID)
    return quest.isCompleted() if quest else False


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getQuestDescription(questID, eventsCache=None):
    quest = eventsCache.getAllQuests().get(questID)
    return quest.getDescription() if quest else ''


@dependency.replace_none_kwargs(lsCtrl=ILSController)
def isCustomizationHangarDisabled(lsCtrl=None):
    return lsCtrl.isEventHangar()


class UseHeaderNavigationImpossible(object):
    __slots__ = ('_hide', '_show', '_confirmationHelper')

    def __init__(self, confirmationHelper, show=True, hide=True):
        super(UseHeaderNavigationImpossible, self).__init__()
        self._hide = hide
        self._show = show
        self._confirmationHelper = confirmationHelper

    def __call__(self, func):

        @wraps(func)
        @wg_async
        def wrapper(*args, **kwargs):

            @wg_async
            def confirmation():
                raise AsyncReturn(False)

            if self._show:
                self._confirmationHelper.start(confirmation)
            yield wg_await(forwardAsFuture(func(*args, **kwargs)))
            if self._hide:
                self._confirmationHelper.stop()

        return wrapper
