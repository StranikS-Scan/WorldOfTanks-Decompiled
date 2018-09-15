# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/free_sheet_popover.py
import operator
from gui.Scaleform.daapi.view.meta.FreeSheetPopoverMeta import FreeSheetPopoverMeta
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import events_helpers, events_dispatcher
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.server_events import IEventsCache

class FreeSheetPopover(FreeSheetPopoverMeta):
    __eventsCache = dependency.descriptor(IEventsCache)
    __ANIMATION_DELAY = 200

    def __init__(self, ctx=None):
        super(FreeSheetPopover, self).__init__(ctx)
        if ctx is not None and ctx.get('data') is not None:
            self.__playAnimation = ctx.get('data').showAnimation
        else:
            self.__playAnimation = False
        return

    def onTaskClick(self, questID):
        events_dispatcher.showPersonalMission(int(questID))
        self.destroy()

    def _populate(self):
        super(FreeSheetPopover, self)._populate()
        self.__eventsCache.onSyncCompleted += self.__update
        self.__update()

    def _dispose(self):
        self.__eventsCache.onSyncCompleted -= self.__update
        super(FreeSheetPopover, self)._dispose()

    def __update(self):
        freeSheetsQuests = []
        pawnedSheets = 0
        for oID, o in sorted(events_helpers.getPersonalMissionsCache().getOperations().iteritems(), key=operator.itemgetter(0)):
            if o.isUnlocked():
                operationName = _ms(PERSONAL_MISSIONS.OPERATIONTITLE_TITLE, title=o.getShortUserName())
                idx = 1
                for vehicleType in VEHICLE_TYPES_ORDER:
                    _, quests = o.getChainByVehicleType(vehicleType)
                    for quest in sorted(quests.itervalues(), key=lambda q: q.getID()):
                        if quest.areTokensPawned():
                            freeSheetsQuests.append({'taskId': str(quest.getID()),
                             'taskText': text_styles.standard(operationName),
                             'descrText': text_styles.main(quest.getUserName()),
                             'animDelay': self.__ANIMATION_DELAY * idx if self.__playAnimation else -1})
                            idx += 1
                            pawnedSheets += quest.getPawnCost()

        freeSheets = events_helpers.getPersonalMissionsCache().getFreeTokensCount()
        if pawnedSheets == 0:
            pawnedSheetsDescrText = PERSONAL_MISSIONS.FREESHEETPOPOVER_PAWNEDSHEETSINFO_DESCR_NOONE
        else:
            pawnedSheetsDescrText = PERSONAL_MISSIONS.FREESHEETPOPOVER_PAWNEDSHEETSINFO_DESCR
        self.as_setDataS({'titleText': text_styles.highTitle(PERSONAL_MISSIONS.FREESHEETPOPOVER_TITLE),
         'freeSheetsInfo': {'imgSource': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_FREE_SHEET_SMALL,
                            'titleText': text_styles.middleTitle(_ms(PERSONAL_MISSIONS.FREESHEETPOPOVER_FREESHEETSINFO_TITLE, count=freeSheets)),
                            'descrText': text_styles.standard(PERSONAL_MISSIONS.FREESHEETPOPOVER_FREESHEETSINFO_DESCR)},
         'pawnedSheetsInfo': {'imgSource': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_PAWNED_SHEET,
                              'titleText': text_styles.middleTitle(_ms(PERSONAL_MISSIONS.FREESHEETPOPOVER_PAWNEDSHEETSINFO_TITLE, count=pawnedSheets)),
                              'descrText': text_styles.standard(pawnedSheetsDescrText)},
         'hasPawnedSheets': pawnedSheets > 0})
        if pawnedSheets > 0:
            self.as_setListDataProviderS(freeSheetsQuests)
