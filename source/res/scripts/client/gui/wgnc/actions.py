# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgnc/actions.py
import BigWorld
from adisp import adisp_process
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_WARNING, LOG_DEBUG
from gui.game_control.links import URLMacros
from gui.promo.promo_logger import PromoLogSourceType
from gui.shared.event_dispatcher import showStrongholds
from gui.shared.utils.decorators import ReprInjector
from gui.wgnc.custom_actions_keeper import CustomActionsKeeper
from gui.wgnc.events import g_wgncEvents
from gui.wgnc.settings import WGNC_GUI_TYPE
from gui.wgnc.common import WebHandlersContainer
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from helpers import dependency
from skeletons.gui.game_control import IBrowserController, IPromoController, IRankedBattlesController
from web.web_client_api.sound import HangarSoundWebApi
from web.web_client_api import webApiCollection

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

    def invoke(self, notID, actor=None):
        raise NotImplementedError


@ReprInjector.withParent(('_purge', 'purge'), ('_isInvoked', 'isInvoked'))
class Callback(_Action):
    __slots__ = ('_purge', '_isInvoked')

    def __init__(self, name, purge=True):
        super(Callback, self).__init__(name)
        self._purge = purge
        self._isInvoked = False

    def doPurge(self):
        return self._purge

    def invoke(self, notID, actor=None):
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
class OpenInternalBrowser(_OpenBrowser, WebHandlersContainer):
    __slots__ = ('_browserID', '_size', '_showRefresh', '_webHandlerName', '_isSolidBorder')
    browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self, name, url, size=None, showRefresh=True, webHandlerName=None, isSolidBorder=False):
        super(OpenInternalBrowser, self).__init__(name, url)
        self._browserID = None
        self._size = size
        self._showRefresh = showRefresh
        self._webHandlerName = webHandlerName
        self._isSolidBorder = isSolidBorder
        return

    def invoke(self, _, actor=None):
        if actor:
            title = actor.getTopic()
        else:
            title = None
        self._doInvoke(title)
        return

    def _getHandlers(self):
        predefinedHandlers = self.getWebHandler(self._webHandlerName) or []
        return predefinedHandlers + webApiCollection(HangarSoundWebApi)

    @adisp_process
    def _doInvoke(self, title):
        self._browserID = yield self.browserCtrl.load(self._url, browserID=self._browserID, title=title, browserSize=self._size, showActionBtn=self._showRefresh, handlers=self._getHandlers(), isSolidBorder=self._isSolidBorder)
        browser = self.browserCtrl.getBrowser(self._browserID)
        if browser is not None:
            browser.setIsAudioMutable(True)
        return


@ReprInjector.withParent()
class OpenPromoBrowser(OpenInternalBrowser):
    __slots__ = ()
    promoCtrl = dependency.descriptor(IPromoController)

    def _doInvoke(self, _):
        self.promoCtrl.showPromo(self._url, source=PromoLogSourceType.PRMP)


@ReprInjector.withParent()
class OpenStrongholdBrowser(OpenInternalBrowser):
    __slots__ = ()

    def _doInvoke(self, _):
        showStrongholds(self._url)


@ReprInjector.withParent()
class OpenRankedBrowser(OpenInternalBrowser):
    __slots__ = ()
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def _doInvoke(self, _):
        self.__rankedController.showRankedBattlePage(ctx={'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID})


@ReprInjector.withParent()
class OpenExternalBrowser(_OpenBrowser):

    @adisp_process
    def invoke(self, notID, actor=None):
        processedUrl = yield URLMacros().parse(self._url)
        try:
            BigWorld.wg_openWebBrowser(processedUrl)
        except (AttributeError, TypeError):
            LOG_CURRENT_EXCEPTION()


@ReprInjector.withParent()
class CustomAction(_Action):

    def __init__(self, action_name, **kwargs):
        super(CustomAction, self).__init__(action_name)
        self.actionID = kwargs.get('id') or kwargs.get('action_id', -1)
        self.kwargs = kwargs

    def invoke(self, notID, actor=None):
        actor, value = self.__getActor()
        if actor is not None:
            return CustomActionsKeeper.invoke(actor, **self.kwargs)
        else:
            LOG_ERROR("Can't find actor for ", str(value))
            return

    def __getActor(self):
        value = self.kwargs.get('value', None)
        if isinstance(value, dict):
            return (value.get('action_class', None), value)
        else:
            ac = self.kwargs.get('action_class', None)
            action = CustomActionsKeeper.getAction(ac or value) or (ac if value != ac else None)
            return (action, value)


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

    def invoke(self, notID, actor=None):
        g_wgncEvents.onItemShowByAction(notID, self._target)


@ReprInjector.withParent(('_text', 'text'))
class ReplaceButtons(_Action):
    __slots__ = ('_text',)

    def __init__(self, name, text):
        super(ReplaceButtons, self).__init__(name)
        self._text = text

    def getTextToReplace(self):
        return self._text

    def invoke(self, notID, actor=None):
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

    def invoke(self, notID, names, actor=None):
        result = False
        if not notID:
            LOG_ERROR('ID of notification is not defined', notID)
            return result
        for name in _getActions4String(names):
            if self.hasAction(name):
                action = self.__actions[name]
                action.invoke(notID, actor)
                result = True
            LOG_ERROR('Action is not found', name)

        return result
