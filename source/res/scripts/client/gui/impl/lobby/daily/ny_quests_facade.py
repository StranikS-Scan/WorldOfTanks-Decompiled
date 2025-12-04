# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/ny_quests_facade.py
from gui.impl.gen import R
from gui.impl.lobby.daily import NYTabs
from gui.impl.lobby.daily.ny_quests_subview import NyQuestsSubView
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from helpers import dependency
NY_LAYOUT_ID = R.views.lobby.daily.NyQuestsView()

class NYQuestsFacade(object):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__nySubView', '__tabs', '__tabsToSubview', '__battleTypes')

    def __init__(self, parentView, *args, **kwargs):
        self.__nySubView = NyQuestsSubView(parentView, NY_LAYOUT_ID)
        self.__tabsToSubview = {NYTabs.DAILY: (self.__nySubView, NY_LAYOUT_ID)}
        self.__tabs = None
        self.__battleTypes = None
        return

    def finalize(self):
        self.__tabs.clear()
        self.__tabsToSubview.clear()

    def getTabs(self):
        return self.__tabs

    def getSubviews(self):
        return self.__tabsToSubview
