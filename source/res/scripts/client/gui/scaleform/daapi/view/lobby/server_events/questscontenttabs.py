# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsContentTabs.py
from gui.Scaleform.daapi.view.meta.QuestsContentTabsMeta import QuestsContentTabsMeta
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.server_events.caches import PQ_TABS
from Event import Event
VIEW_TABS_ORDER = [QUESTS_ALIASES.SEASON_VIEW_TAB_RANDOM, QUESTS_ALIASES.SEASON_VIEW_TAB_FALLOUT]
VIEW_TABS_LABELS = {QUESTS_ALIASES.SEASON_VIEW_TAB_RANDOM: QUESTS.PERSONAL_SEASONS_TAB_RANDOM,
 QUESTS_ALIASES.SEASON_VIEW_TAB_FALLOUT: QUESTS.PERSONAL_SEASONS_TAB_FALLOUT}

class QuestsContentTabs(QuestsContentTabsMeta):

    def __init__(self):
        super(QuestsContentTabs, self).__init__()
        self.onTabSelected = Event()

    def onSelectTab(self, tabId):
        self.onTabSelected(tabId)

    def selectTab(self, tabID):
        self.as_selectTabS(PQ_TABS.index(tabID))

    def _populate(self):
        super(QuestsContentTabs, self)._populate()
        self.as_setTabsS({'tabs': self.__packViewTabs()})

    def __packViewTabs(self):
        tabs = []
        for idx in PQ_TABS:
            tabs.append(self.__packViewTabDataItem(VIEW_TABS_LABELS[idx], idx))

        return tabs

    def __packViewTabDataItem(self, label, id):
        return {'label': label,
         'id': id}
