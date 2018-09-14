# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsSeasonAwardsWindow.py
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from helpers.i18n import makeString as _ms
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters import icons
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.meta.QuestsSeasonAwardsWindowMeta import QuestsSeasonAwardsWindowMeta
from gui.Scaleform.locale import TOOLTIPS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class QuestsSeasonAwardsWindow(QuestsSeasonAwardsWindowMeta):

    def __init__(self, ctx = None):
        super(QuestsSeasonAwardsWindow, self).__init__()
        raise 'questsType' in ctx or AssertionError
        self.__questsType = ctx['questsType']

    def onWindowClose(self):
        self.destroy()

    def showVehicleInfo(self, vehTypeCompDescr):
        shared_events.showVehicleInfo(vehTypeCompDescr)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(QuestsSeasonAwardsWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == QUESTS_ALIASES.QUESTS_CONTENT_TABS_PY_ALIAS:
            viewPy.onTabSelected += self.__onTabSelected
            viewPy.selectTab(self.__questsType)

    @property
    def _contentTabs(self):
        return self.components.get(QUESTS_ALIASES.QUESTS_CONTENT_TABS_PY_ALIAS)

    def _populate(self):
        super(QuestsSeasonAwardsWindow, self)._populate()
        self.__setData()

    def __onTabSelected(self, tabId):
        self.__questsType = tabId
        self.__setData()

    def __setData(self):
        tabID = self.__questsType
        awards = []
        cache = events_helpers.getPotapovQuestsCache(tabID)
        for tile in cache.getTiles().itervalues():
            extraAward = self.__packFemaleTankmanAward()
            basicAward = self.__packBasicAward(tile)
            userName = tile.getUserName()
            awards.append({'title': text_styles.highTitle(_ms(QUESTS.SEASONAWARDSWINDOW_TILEAWARDSTITLE, name=userName)),
             'background': RES_ICONS.MAPS_ICONS_QUESTS_AWARDS_BACKGROUND,
             'basicAward': basicAward,
             'extraAward': extraAward})

        self.as_setDataS({'windowTitle': _ms(QUESTS.SEASONAWARDSWINDOW_TITLE),
         'awards': awards})

    def __packBasicAward(self, tile):
        name = ''
        vehicle = tile.getVehicleBonus()
        if vehicle is not None:
            type = vehicle.typeUserName
            level = _ms('#menu:header/level/%s' % vehicle.level)
            vName = vehicle.shortUserName
            name = text_styles.main(_ms(QUESTS.SEASONAWARDSWINDOW_VEHICLENAME, name=text_styles.highTitle(vName), type=type, level=text_styles.middleTitle(level)))
        tokensCountText, tooltipLinkage = self.__getTokensInfo(tile)
        return {'iconPath': '../maps/icons/quests/awards/tile_%s_%s_award.png' % (tile.getSeasonID(), tile.getID()),
         'vehicleType': vehicle.type if vehicle is not None else '',
         'name': name,
         'buttonText': _ms(QUESTS.SEASONAWARDSWINDOW_VEHICLEAWARD_BUTTONABOUT_TEXT),
         'buttonTooltipId': TOOLTIPS.TOOLTIPS.QUESTS_VEHICLESEASONAWARD_ABOUTBTN,
         'vehicleId': vehicle.intCD if vehicle is not None else -1,
         'tokensCountText': tokensCountText,
         'tokensCountTooltip': tooltipLinkage}

    def __getTokensInfo(self, tile):
        text, tooltip = ('', None)
        if self.__questsType == QUESTS_ALIASES.SEASON_VIEW_TAB_RANDOM:
            tokensCount = tile.getTotalTokensCount()
            tokenIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_QUESTS_TOKEN16, 16, 16, -3, 0)
            text = text_styles.main(_ms(QUESTS.SEASONAWARDSWINDOW_TOKENSCOUNT, count=str(tokensCount), icon=tokenIcon))
            tooltip = TOOLTIPS_CONSTANTS.PRIVATE_QUESTS_TOKENS_AWARD
        return (text, tooltip)

    def __packFemaleTankmanAward(self):
        return {'iconPath': RES_ICONS.MAPS_ICONS_QUESTS_TANKMANFEMALEGRAY,
         'title': text_styles.middleTitle(_ms(QUESTS.SEASONAWARDSWINDOW_FEMALETANKMANAWARD_TITLE)),
         'description': text_styles.main(_ms(QUESTS.SEASONAWARDSWINDOW_FEMALETANKMANAWARD_DESCRIPTION)),
         'tooltip': TOOLTIPS_CONSTANTS.PRIVATE_QUESTS_FEMALE_TANKMAN_AWARD}

    def __packCommendationListsAward(self):
        return {'iconPath': RES_ICONS.MAPS_ICONS_QUESTS_TOKEN128,
         'title': text_styles.middleTitle(_ms(QUESTS.SEASONAWARDSWINDOW_COMMENDATIONLISTSAWARD_TITLE)),
         'description': text_styles.main(_ms(QUESTS.SEASONAWARDSWINDOW_COMMENDATIONLISTSAWARD_DESCRIPTION))}
