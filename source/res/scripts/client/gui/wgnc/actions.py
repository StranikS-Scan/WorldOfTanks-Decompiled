# Embedded file name: scripts/client/gui/wgnc/actions.py
import BigWorld
from adisp import process
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_WARNING, LOG_DEBUG
from gui.game_control import getBrowserCtrl
from gui.shared.utils.decorators import ReprInjector
from gui.wgnc.events import g_wgncEvents
from gui.wgnc.settings import WGNC_GUI_TYPE

@ReprInjector.simple(('_name', 'name'))

class _Action(object):
    __slots__ = ('_name',)

    def __init__(self, name):
        super(_Action, self).__init__()
        self._name = name

    def getName(self):
        return self._name

    def validate(self, itemsHolder):
        return True

    def invoke(self, notID, actor = None):
        raise NotImplementedError


@ReprInjector.withParent(('_purge', 'purge'), ('_isInvoked', 'isInvoked'))

class Callback(_Action):
    __slots__ = ('_purge', '_isInvoked')

    def __init__(self, name, purge = True):
        super(Callback, self).__init__(name)
        self._purge = purge
        self._isInvoked = False

    def doPurge(self):
        return self._purge

    def invoke(self, notID, actor = None):
        if self._purge and self._isInvoked:
            LOG_DEBUG('Callback with purge=true has been invoked, it is skipped', self._name)
            return
        self._isInvoked = True
        try:
            BigWorld.player().sendNotificationReply(notID, self._purge, self._name)
        except (AttributeError, TypeError):
            LOG_CURRENT_EXCEPTION()


@ReprInjector.withParent(('_url', 'url'))

class _OpenBrowser(_Action):
    __slots__ = ('_url',)

    def __init__(self, name, url):
        super(_OpenBrowser, self).__init__(name)
        self._url = url

    def getURL(self):
        return self._url


@ReprInjector.withParent()

class OpenInternalBrowser(_OpenBrowser):
    __slots__ = ('_browserID',)

    def __init__(self, name, url):
        super(OpenInternalBrowser, self).__init__(name, url)
        self._browserID = None
        return

    def invoke(self, notID, actor = None):
        ctrl = getBrowserCtrl()
        if ctrl:
            if actor:
                title = actor.getTopic()
            else:
                title = None
            self.__doInvoke(ctrl, title)
        else:
            LOG_ERROR('Browser controller is not found')
        return

    @process
    def __doInvoke(self, ctrl, title):
        self._browserID = yield ctrl.load(self._url, browserID=self._browserID, title=title)


@ReprInjector.withParent()

class OpenExternalBrowser(_OpenBrowser):

    def invoke(self, notID, actor = None):
        try:
            BigWorld.wg_openWebBrowser(self._url)
        except (AttributeError, TypeError):
            LOG_CURRENT_EXCEPTION()


@ReprInjector.withParent(('_target', 'target'))

class OpenWindow(_Action):
    __slots__ = ('_target',)

    def __init__(self, name, target):
        super(OpenWindow, self).__init__(name)
        self._target = target

    def validate(self, itemsHolder):
        return itemsHolder.getItemByName(self._target) is not None

    def getTarget(self):
        return self._target

    def invoke(self, notID, actor = None):
        g_wgncEvents.onItemShowByAction(notID, self._target)


@ReprInjector.withParent(('_text', 'text'))

class ReplaceButtons(_Action):
    __slots__ = ('_text',)

    def __init__(self, name, text):
        super(ReplaceButtons, self).__init__(name)
        self._text = text

    def getTextToReplace(self):
        return self._text

    def invoke(self, notID, actor = None):
        if not actor:
            LOG_ERROR('GUI item is not found', self)
            return
        if actor.getType() != WGNC_GUI_TYPE.POP_UP:
            LOG_WARNING('Hiding buttons is allowed in pup up only', actor, self)
            return
        actor.hideButtons()
        actor.setNote(self._text)
        g_wgncEvents.onItemUpdatedByAction(notID, actor)


def _getActions4String(value):
    seq = value.split(',')
    for name in seq:
        yield name.strip()


@ReprInjector.simple(('__actions', 'actions'))

class ActionsHolder(object):
    __slots__ = ('__actions',)

    def __init__(self, items):
        super(ActionsHolder, self).__init__()
        self.__actions = {item.getName():item for item in items}

    def clear(self):
        self.__actions.clear()

    def hasAction(self, name):
        return name in self.__actions

    def hasAllActions(self, names):
        for name in _getActions4String(names):
            if not self.hasAction(name):
                return False

        return True

    def getAction(self, name):
        action = None
        if self.hasAction(name):
            action = self.__actions[name]
        return action

    def validate(self, itemsHolder):
        exclude = set()
        for name, action in self.__actions.iteritems():
            if not action.validate(itemsHolder):
                LOG_WARNING('Action is invalid', action)
                exclude.add(name)

        for name in exclude:
            self.__actions.pop(name, None)

        return

    def invoke(self, notID, names, actor = None):
        result = False
        if not notID:
            LOG_ERROR('ID of notification is not defined', notID)
            return result
        for name in _getActions4String(names):
            if self.hasAction(name):
                action = self.__actions[name]
                action.invoke(notID, actor)
                result = True
            else:
                LOG_ERROR('Action is not found', name)

        return result
