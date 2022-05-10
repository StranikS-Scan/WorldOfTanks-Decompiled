# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/impl/event_battle_page.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.battle.classic import ClassicPage
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES

class EventBattlePage(ClassicPage):

    def __init__(self, components=None, external=None, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        LOG_ERROR('INIT --- EventBattlePage')
        super(EventBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
