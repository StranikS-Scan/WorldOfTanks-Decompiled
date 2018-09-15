# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_first_entry_award_view.py
from operator import attrgetter
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.PersonalMissionFirstEntryAwardViewMeta import PersonalMissionFirstEntryAwardViewMeta
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.settings import BADGES_ICONS, getBadgeIconPath
from gui.server_events.finders import getQuestsByTokenAndBonus, pmTokenDetector, badgeBonusFinder
from gui.server_events.personal_missions_navigation import PersonalMissionsNavigation
from gui.server_events.pm_constants import SOUNDS, FIRST_ENTRY_STATE, PERSONAL_MISSIONS_SOUND_SPACE
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from helpers.i18n import makeString
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore

def _wrapBadgeAward(title, badgeID, imageSize):
    return {'title': title,
     'icon': getBadgeIconPath(imageSize, badgeID),
     'tooltip': {'isSpecial': True,
                 'specialAlias': TOOLTIPS_CONSTANTS.BADGE,
                 'specialArgs': [badgeID]}}


class PersonalMissionFirstEntryAwardView(LobbySubView, PersonalMissionsNavigation, PersonalMissionFirstEntryAwardViewMeta):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SOUND_SPACE
    __BADGE_ICON_SIZES = dict(enumerate((BADGES_ICONS.X220,
     BADGES_ICONS.X110,
     BADGES_ICONS.X110,
     BADGES_ICONS.X110,
     BADGES_ICONS.X80), start=1))

    def bigBtnClicked(self):
        settingsCore = dependency.instance(ISettingsCore)
        settingsCore.serverSettings.setPersonalMissionsFirstEntryState(FIRST_ENTRY_STATE.AWARDS_WAS_SHOWN)
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS), scope=EVENT_BUS_SCOPE.LOBBY)

    def onEscapePress(self):
        self.closeView()

    def closeView(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(PersonalMissionFirstEntryAwardView, self)._populate()
        operations = self._eventsCache.personalMissions.getOperations()
        awards = self.__getAwards(operations)
        if len(awards) == 1:
            titleLabel = makeString(PERSONAL_MISSIONS.PERSONALMISSIONAWARDVIEW_TITLE_ONE, vehicleName=first(awards)['title'])
        elif len(awards) > len(operations):
            titleLabel = PERSONAL_MISSIONS.PERSONALMISSIONAWARDVIEW_TITLE_PERFECT
        else:
            titleLabel = PERSONAL_MISSIONS.PERSONALMISSIONAWARDVIEW_TITLE
        self.as_setInitDataS({'bgSource': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_INFOSCREENBG,
         'titleLabel': titleLabel,
         'subtitleLabel': PERSONAL_MISSIONS.PERSONALMISSIONAWARDVIEW_SUBTITLE,
         'bigBtnLabel': PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_ACKNOWLEDGEBTN})
        self.as_updateS({'awardsLinkage': PERSONAL_MISSIONS_ALIASES.BADGES_CMP_LINKAGES[len(awards) - 1],
         'awards': awards})
        self.soundManager.playSound(SOUNDS.FIRST_RUN_AWARD_APPEARANCE)

    def __getAwards(self, operations):
        badgesToShow = {}
        badgeQuests = getQuestsByTokenAndBonus(self._eventsCache.getHiddenQuests(), tokenFinder=pmTokenDetector(len(operations)), bonusFinder=badgeBonusFinder())
        for quest in badgeQuests.itervalues():
            for bonus in quest.getBonuses('dossier'):
                for badge in bonus.getBadges():
                    if badge.isAchieved:
                        group = badge.group
                        if group not in badgesToShow or badgesToShow[group].getBadgeClass() < badge.getBadgeClass():
                            badgesToShow[group] = badge

        result = []
        badgesCount = len(badgesToShow)
        if badgesCount > 0:
            sortedBadges = sorted(badgesToShow.values(), key=attrgetter('group'))
            if badgesCount > len(operations):
                result.append(_wrapBadgeAward('', sortedBadges.pop(0).badgeID, BADGES_ICONS.X220))
            imageSize = self.__BADGE_ICON_SIZES[badgesCount]
            for opIdx, badge in enumerate(sortedBadges, start=1):
                vehicleName = operations[opIdx].getVehicleBonus().userName
                result.append(_wrapBadgeAward(vehicleName, badge.badgeID, imageSize))

        return result
