# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/portal_full_stats.py
from battle_royale.gui.Scaleform.daapi.view.battle.full_stats import FullStatsComponent
import BigWorld
from gui.impl import backport
from gui.impl.gen import R
from PortalBattleStateComponent import PortalBattleStateComponent

class PortalFullStatsComponent(FullStatsComponent):

    def _populate(self):
        super(PortalFullStatsComponent, self)._populate()
        PortalBattleStateComponent.onCampInfoUpdated += self.__onCampInfoUpdated

    def _dispose(self):
        super(PortalFullStatsComponent, self)._dispose()
        PortalBattleStateComponent.onCampInfoUpdated -= self.__onCampInfoUpdated

    def _initPanel(self):
        campsCount = 4
        capturedCamps = 0
        data = {'header': {'title': backport.text(R.strings.portal_event.battle.tab.title()),
                    'subTitle': backport.text(R.strings.portal_event.battle.tab.subTitle()),
                    'description': backport.text(R.strings.portal_event.battle.tab.description())},
         'campsCount': campsCount,
         'capturedCamps': capturedCamps,
         'minimapItems': self.__getMinimapItems()}
        self.as_setDataS(data)

    def __onCampInfoUpdated(self, *args, **kwargs):
        campsCount = self.__battleState.getCampsCount()
        capturedCamps = self.__battleState.getCapturedCampsCount()
        self.as_updateScoreS(campsCount, capturedCamps, '')

    def __getMinimapItems(self):
        return [self.__getMinimapItem('portal_lgd', backport.text(R.strings.portal_event.battle.tab.minimapItemText.portal()), 'add'),
         self.__getMinimapItem('guard_lgd', backport.text(R.strings.portal_event.battle.tab.minimapItemText.guard()), 'add'),
         self.__getMinimapItem('camp_lgd', backport.text(R.strings.portal_event.battle.tab.minimapItemText.camp()), 'add'),
         self.__getMinimapItem('lane_lgd', backport.text(R.strings.portal_event.battle.tab.minimapItemText.lane()), 'add'),
         self.__getMinimapItem('teleport_lgd', backport.text(R.strings.portal_event.battle.tab.minimapItemText.teleport())),
         self.__getMinimapItem('tp_hub_lgd', backport.text(R.strings.portal_event.battle.tab.minimapItemText.tp_hub())),
         self.__getMinimapItem('base_lgd', backport.text(R.strings.portal_event.battle.tab.minimapItemText.base()))]

    def __getMinimapItem(self, icon, description, blendMode='normal'):
        return {'icon': icon,
         'description': description,
         'blendMode': blendMode}

    def __getScoreBlock(self, icon, count, descr, squads=''):
        return {'icon': icon,
         'count': count,
         'description': descr,
         'squads': squads}

    @property
    def __battleState(self):
        return BigWorld.player().arena.arenaInfo.portalBattleStateComponent
