# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/hangar/event_shop_entry_point.py
from gui.Scaleform.daapi.view.meta.EventShopEntryPointMeta import EventShopEntryPointMeta
from gui.impl.gen import R
from gui.impl import backport
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from halloween.skeletons.gui.game_event_controller import IHalloweenProgressController
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.server_events import IEventsCache
from halloween.gui.shared.event_dispatcher import showHalloweenShop

class EventShopEntryPoint(EventShopEntryPointMeta, IGlobalListener):
    _eventsCache = dependency.descriptor(IEventsCache)
    _eventController = dependency.descriptor(IEventBattlesController)
    _hwController = dependency.descriptor(IHalloweenProgressController)

    def onClick(self):
        showHalloweenShop()

    def _populate(self):
        super(EventShopEntryPoint, self)._populate()
        self.startGlobalListening()
        self._eventsCache.onSyncCompleted += self.__onSyncCompleted
        self._hwController.onChangeActivePhase += self.__onChangeActivePhase
        self._hwController.onQuestsUpdated += self.__onQuestUpdated
        self.__update()

    def _dispose(self):
        self.stopGlobalListening()
        self._eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self._hwController.onChangeActivePhase -= self.__onChangeActivePhase
        self._hwController.onQuestsUpdated -= self.__onQuestUpdated
        super(EventShopEntryPoint, self)._dispose()

    def __onSyncCompleted(self):
        self.__update()

    def __onChangeActivePhase(self, _):
        self.__update()

    def __onQuestUpdated(self):
        self.__update()

    def __update(self):
        phase = self._hwController.phasesHalloween.getActivePhase()
        if not phase:
            return
        data = phase.getAbilityInfo(dailyQuest=False)
        if not data:
            return
        equipment, _, _ = data
        self.as_setDataS({'kettleType': equipment.descriptor.iconName,
         'title': backport.text(R.strings.hw_lobby.eventShop.entryPoint.title()),
         'tooltip': makeTooltip(backport.text(R.strings.hw_tooltips.eventShop.entryPoint.header()), backport.text(R.strings.hw_tooltips.eventShop.entryPoint.body()))})
