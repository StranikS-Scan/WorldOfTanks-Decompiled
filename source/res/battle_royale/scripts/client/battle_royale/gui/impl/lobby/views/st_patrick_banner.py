# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/st_patrick_banner.py
from __future__ import absolute_import
from battle_royale.gui.impl.lobby.views.event_banner import BattleRoyaleEventBanner
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

@dependency.replace_none_kwargs(battleRoyaleController=IBattleRoyaleController)
def isStPatrickEntryPointAvailable(battleRoyaleController=None):
    return battleRoyaleController.isActive() and battleRoyaleController.isStPatrick()


class StPatrickEventBanner(BattleRoyaleEventBanner):
    NAME = 'StPatrickEntryPoint'

    @property
    def borderColor(self):
        pass

    @property
    def introDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.StPatrickEntryPoint.intro.description())

    @property
    def inProgressDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.StPatrickEntryPoint.inProgress.description())

    def _onUpdate(self, *_):
        if isStPatrickEntryPointAvailable():
            EventBannersContainer().onBannerUpdate(self)
        else:
            self.__eventsService.updateEntries()
