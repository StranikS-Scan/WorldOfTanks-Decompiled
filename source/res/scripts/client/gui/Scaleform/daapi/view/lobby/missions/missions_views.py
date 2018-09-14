# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/missions_views.py
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.CurrentVehicleMissionsViewMeta import CurrentVehicleMissionsViewMeta
from gui.Scaleform.daapi.view.meta.MissionsGroupedViewMeta import MissionsGroupedViewMeta
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import settings
from gui.server_events.events_dispatcher import showMissionsCategories
from gui.server_events.formatters import isMarathon
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms

class _GroupedMissionsView(MissionsGroupedViewMeta):
    """ Missions tab for quests combined in groups.
    """

    def clickActionBtn(self, actionID):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STORE, ctx={'tabId': STORE_CONSTANTS.STORE_ACTIONS}), scope=EVENT_BUS_SCOPE.LOBBY)

    def expand(self, id, value):
        settings.expandGroup(id, value)
        if self._questsDP is not None:
            for blockData in self._questsDP.collection:
                if blockData.get('blockId') == id:
                    blockData['isCollapsed'] = settings.isGroupMinimized(id)

        return

    def openTokenPopover(self, tokenId):
        super(_GroupedMissionsView, self).openTokenPopover(tokenId)


class MissionsMarathonsView(_GroupedMissionsView):
    """ Missions tab for quests combined in marathons.
    
    Marathon is a special group with a final prise.
    """

    def dummyClicked(self, eventType):
        if eventType == 'OpenCategoriesEvent':
            showMissionsCategories()
        else:
            super(MissionsMarathonsView, self).dummyClicked(eventType)

    @staticmethod
    def _getBackground():
        return RES_ICONS.MAPS_ICONS_MISSIONS_BACKGROUNDS_MARATHONS

    @staticmethod
    def _getDummy():
        return {'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON,
         'htmlText': text_styles.main(_ms(QUESTS.MISSIONS_NOTASKSMARATHON_DUMMY_TEXT)),
         'alignCenter': False,
         'btnVisible': True,
         'btnLabel': '',
         'btnTooltip': '',
         'btnEvent': 'OpenCategoriesEvent',
         'btnLinkage': BUTTON_LINKAGES.BUTTON_LINK}

    def _getViewQuestFilter(self):
        return lambda q: isMarathon(q.getGroupID())


class MissionsCategoriesView(_GroupedMissionsView):
    """ Missions tab for quests that don't fall within the marathon criteria.
    """

    @staticmethod
    def _getBackground():
        return RES_ICONS.MAPS_ICONS_MISSIONS_BACKGROUNDS_CATEGORIES

    def _getViewQuestFilter(self):
        return lambda q: not isMarathon(q.getGroupID())


class CurrentVehicleMissionsView(CurrentVehicleMissionsViewMeta):
    """ Missions tab for all quests from the other tabs that can be completed on the current vihicle.
    """

    def setBuilder(self, builder, filters):
        super(CurrentVehicleMissionsView, self).setBuilder(builder, filters)
        self._builder.onBlocksDataChanged += self.__onBlocksDataChanged

    @staticmethod
    def _getBackground():
        return RES_ICONS.MAPS_ICONS_MISSIONS_BACKGROUNDS_CURRENTVEHICLE

    def _dispose(self):
        self._builder.onBlocksDataChanged -= self.__onBlocksDataChanged
        super(CurrentVehicleMissionsView, self)._dispose()

    def __onBlocksDataChanged(self):
        self._builder.invalidateBlocks()
        self._filterMissions()
        self._onDataChangedNotify()
