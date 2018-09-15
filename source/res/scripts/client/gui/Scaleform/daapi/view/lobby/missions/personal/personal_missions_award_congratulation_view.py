# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_award_congratulation_view.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.meta.PersonalMissionAwardCongratulationViewMeta import PersonalMissionAwardCongratulationViewMeta
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.settings import getPersonalMissionVehicleAwardImage, ICONS_SIZES, getBadgeIconPath
from gui.server_events.personal_missions_navigation import PersonalMissionsNavigation
from gui.server_events.pm_constants import SOUNDS, PERSONAL_MISSIONS_SOUND_SPACE
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers.i18n import makeString as _ms

class PersonalMissionAwardCongratulationView(PersonalMissionsNavigation, PersonalMissionAwardCongratulationViewMeta):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SOUND_SPACE

    def __init__(self, ctx=None):
        super(PersonalMissionAwardCongratulationView, self).__init__(ctx)
        self.__operationID = ctx['operationID']
        self.__quests = ctx['quests']

    def bigBtnClicked(self):
        self.closeView()

    def onEscapePress(self):
        self.closeView()

    def closeView(self):
        self.destroy()

    def _populate(self):
        super(PersonalMissionAwardCongratulationView, self)._populate()
        self.as_setInitDataS({'bgSource': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_INFOSCREENBG,
         'titleLabel': PERSONAL_MISSIONS.AWARDCONGRATULATIONVIEW_TITLE,
         'subtitleLabel': self.__getSubtitleLabel(),
         'bigBtnLabel': PERSONAL_MISSIONS.AWARDCONGRATULATIONVIEW_BUTTON_LABEL})
        self.__update()
        self.soundManager.playSound(SOUNDS.TANK_AWARD_WINDOW)
        self.soundManager.setRTPC(SOUNDS.RTCP_OVERLAY, SOUNDS.MAX_MISSIONS_ZOOM)

    def _destroy(self):
        self.soundManager.setRTPC(SOUNDS.RTCP_OVERLAY, SOUNDS.MIN_MISSIONS_ZOOM)
        super(PersonalMissionAwardCongratulationView, self)._destroy()

    def _invalidate(self, ctx=None):
        self.__quests.update(ctx['quests'])
        self.__update()

    def __update(self):
        mainAwards, awards = self.__getAwards()
        self.as_updateS({'mainAwardsLinkage': PERSONAL_MISSIONS_ALIASES.OPERATION_MAIN_AWARD_LINKAGE,
         'awardsLinkage': PERSONAL_MISSIONS_ALIASES.BADGES_CMP_LINKAGES[len(awards) - 1],
         'mainAwards': mainAwards,
         'awards': awards})

    def __getSubtitleLabel(self):
        operation = self._eventsCache.personalMissions.getOperations()[self.__operationID]
        return text_styles.superPromoTitle(_ms(PERSONAL_MISSIONS.AWARDCONGRATULATIONVIEW_SUBTITLE, title=operation.getShortUserName()))

    def __getAwards(self):
        vehicleBonuses = []
        badgesBonuses = []
        hasTankCamo = False
        hasNationCamo = False
        mainAwards = []
        addAwards = []
        for q in self.__quests.itervalues():
            for b in q.getBonuses('vehicles'):
                for vehicle, _ in b.getVehicles():
                    vehicleBonuses.append(vehicle)

            for b in q.getBonuses('dossier'):
                for badge in b.getBadges():
                    badgesBonuses.append(badge)

            if q.getBonuses('customizations'):
                hasTankCamo = True
            for b in q.getBonuses('tokens'):
                for token in b.getTokens():
                    if token.endswith(':camouflage'):
                        hasNationCamo = True

        for vehicle in vehicleBonuses:
            LOG_DEBUG('## vehicle, vehicle.name, result', vehicle, vehicle.name, vehicle.name.split(':')[-1])
            mainAwards.append({'title': '',
             'icon': getPersonalMissionVehicleAwardImage(ICONS_SIZES.X550, vehicle.name.split(':')[-1]),
             'tooltip': {'isSpecial': True,
                         'specialAlias': TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
                         'specialArgs': [vehicle.intCD]}})

        for badge in sorted(badgesBonuses):
            addAwards.append({'title': badge.getUserName(),
             'icon': getBadgeIconPath(ICONS_SIZES.X110, badge.badgeID),
             'tooltip': {'isSpecial': True,
                         'specialAlias': TOOLTIPS_CONSTANTS.BADGE,
                         'specialArgs': [badge.badgeID]}})

        if hasTankCamo and hasNationCamo:
            addAwards.append({'title': '',
             'icon': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_AWARDS_110X110_CAMOUFLAGE,
             'tooltip': {'tooltip': makeTooltip(TOOLTIPS.PERSONALMISSIONS_AWARDS_CAMOUFLAGEALL_HEADER, TOOLTIPS.PERSONALMISSIONS_AWARDS_CAMOUFLAGEALL_BODY)}})
        elif hasTankCamo:
            addAwards.append({'title': '',
             'icon': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_AWARDS_110X110_CAMOUFLAGE,
             'tooltip': {'tooltip': makeTooltip(TOOLTIPS.PERSONALMISSIONS_AWARDS_CAMOUFLAGEONLY_HEADER, TOOLTIPS.PERSONALMISSIONS_AWARDS_CAMOUFLAGEONLY_BODY)}})
        elif hasNationCamo:
            addAwards.append({'title': '',
             'icon': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_AWARDS_110X110_CAMOUFLAGE,
             'tooltip': {'tooltip': makeTooltip(TOOLTIPS.PERSONALMISSIONS_AWARDS_CAMOUFLAGENATION_HEADER, TOOLTIPS.PERSONALMISSIONS_AWARDS_CAMOUFLAGENATION_BODY)}})
        return (mainAwards, addAwards)
