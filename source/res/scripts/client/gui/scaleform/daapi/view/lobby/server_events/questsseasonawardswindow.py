# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsSeasonAwardsWindow.py
from helpers.i18n import makeString as _ms
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items import Vehicle
from gui.server_events import g_eventsCache
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.meta.QuestsSeasonAwardsWindowMeta import QuestsSeasonAwardsWindowMeta
from gui.Scaleform.locale import TOOLTIPS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.QUESTS_SEASON_AWARDS_TYPES import QUESTS_SEASON_AWARDS_TYPES

class QuestsSeasonAwardsWindow(QuestsSeasonAwardsWindowMeta):

    def __init__(self, ctx = None):
        super(QuestsSeasonAwardsWindow, self).__init__()
        raise 'seasonID' in ctx or AssertionError
        self.__seasonID = ctx['seasonID']

    def onWindowClose(self):
        self.destroy()

    def showVehicleInfo(self, vehTypeCompDescr):
        shared_events.showVehicleInfo(vehTypeCompDescr)

    def _populate(self):
        super(QuestsSeasonAwardsWindow, self)._populate()
        basicAwards = []
        season = g_eventsCache.potapov.getSeasons()[self.__seasonID]
        for tile in season.getTiles().itervalues():
            vehicle = tile.getVehicleBonus()
            if vehicle is not None:
                basicAwards.append(self.__packVehicleAward(vehicle))

        self.as_setDataS({'windowTitle': _ms(QUESTS.SEASONAWARDSWINDOW_TITLE),
         'basicAwardsTitle': text_styles.highTitle(_ms(QUESTS.SEASONAWARDSWINDOW_BASICAWARDS_TITLE)),
         'extraAwardsTitle': text_styles.highTitle(_ms(QUESTS.SEASONAWARDSWINDOW_EXTRAAWARDS_TITLE)),
         'basicAwards': basicAwards,
         'extraAwards': [self.__packFemaleTankmanAward(), self.__packCommendationListsAward()]})
        return

    def __packVehicleAward(self, vehicle):
        return {'type': QUESTS_SEASON_AWARDS_TYPES.VEHICLE,
         'iconPath': vehicle.iconUnique,
         'levelIconPath': Vehicle.getLevelBigIconPath(vehicle.level),
         'vehicleType': vehicle.type,
         'name': text_styles.middleTitle(vehicle.shortUserName),
         'buttonText': _ms(QUESTS.SEASONAWARDSWINDOW_VEHICLEAWARD_BUTTONABOUT_TEXT),
         'buttonTooltipId': TOOLTIPS.TOOLTIPS.QUESTS_VEHICLESEASONAWARD_ABOUTBTN,
         'vehicleId': vehicle.intCD,
         'nation': vehicle.nationName}

    def __packFemaleTankmanAward(self):
        return {'type': QUESTS_SEASON_AWARDS_TYPES.FEMALE_TANKMAN,
         'iconPath': RES_ICONS.MAPS_ICONS_QUESTS_TANKMANFEMALEGRAY,
         'title': text_styles.middleTitle(_ms(QUESTS.SEASONAWARDSWINDOW_FEMALETANKMANAWARD_TITLE)),
         'description': text_styles.main(_ms(QUESTS.SEASONAWARDSWINDOW_FEMALETANKMANAWARD_DESCRIPTION))}

    def __packCommendationListsAward(self):
        return {'type': QUESTS_SEASON_AWARDS_TYPES.COMMENDATION_LISTS,
         'iconPath': RES_ICONS.MAPS_ICONS_QUESTS_TOKEN128,
         'title': text_styles.middleTitle(_ms(QUESTS.SEASONAWARDSWINDOW_COMMENDATIONLISTSAWARD_TITLE)),
         'description': text_styles.main(_ms(QUESTS.SEASONAWARDSWINDOW_COMMENDATIONLISTSAWARD_DESCRIPTION))}
