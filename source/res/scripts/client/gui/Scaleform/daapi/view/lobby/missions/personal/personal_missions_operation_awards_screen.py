# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_operation_awards_screen.py
from gui.Scaleform.daapi.view.meta.PersonalMissionsOperationAwardsScreenMeta import PersonalMissionsOperationAwardsScreenMeta
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import AWARDS_SIZES, LABEL_ALIGN
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.settings import ICONS_SIZES
from gui.server_events.pm_constants import SOUNDS, PERSONAL_MISSIONS_SOUND_SPACE
from gui.shared.utils.functions import makeTooltip
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.server_events import finders
from helpers import dependency
from helpers.i18n import makeString as _ms
from shared_utils import first
from skeletons.gui.server_events import IEventsCache

class PersonalMissionsOperationAwardsScreen(PersonalMissionsOperationAwardsScreenMeta):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SOUND_SPACE
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, ctx):
        ctx = ctx or {}
        super(PersonalMissionsOperationAwardsScreen, self).__init__(ctx)
        self.__branch = ctx['branch']
        self.__operationID = ctx['operationID']
        self.__questsIds = ctx['questIds']
        self.__vehicleAward = None
        return

    def onPlaySound(self, soundType):
        self.soundManager.playSound(SOUNDS.TANK_AWARD_WINDOW)

    def onCloseWindow(self):
        self.destroy()
        self.soundManager.setRTPC(SOUNDS.RTCP_OVERLAY, SOUNDS.MIN_MISSIONS_ZOOM)

    def _populate(self):
        super(PersonalMissionsOperationAwardsScreen, self)._populate()
        badges, camouflageAward = self.__getBonuses(self.__questsIds)
        self.as_setInitDataS({'closeBtnLabel': PERSONAL_MISSIONS.AWARDSSCREEN_CLOSEBTN_LABEL,
         'header': self.__getHeader(),
         'headerExtra': PERSONAL_MISSIONS.AWARDSSCREEN_HEADEREXTRA,
         'campaignId': self.__branch,
         'vehicleData': self.__getVehicleData()})
        awards = self.__packBadges(badges)
        if camouflageAward:
            awards.append(camouflageAward)
        renderSize = 80 if self.__vehicleAward else 110
        self.as_setAwardDataS({'ribbonType': 'ribbon1',
         'rendererLinkage': 'RibbonAwardAnimUI',
         'gap': 20,
         'rendererWidth': renderSize,
         'rendererHeight': renderSize,
         'awards': awards})
        self.as_playAwardsAnimationS()
        self.soundManager.playSound(SOUNDS.TANK_AWARD_WINDOW)
        self.soundManager.setRTPC(SOUNDS.RTCP_OVERLAY, SOUNDS.MAX_MISSIONS_ZOOM)

    def __getHeader(self):
        operation = self._eventsCache.getPersonalMissions().getOperationsForBranch(self.__branch)[self.__operationID]
        if operation.isFullCompleted():
            l18nKey = PERSONAL_MISSIONS.AWARDSSCREEN_HEADER_FULLYCOMPLETED
        else:
            l18nKey = PERSONAL_MISSIONS.AWARDSSCREEN_HEADER
        return _ms(l18nKey, missionName=operation.getShortUserName())

    def __getVehicleData(self):
        if self.__vehicleAward is None:
            return
        else:
            vehicle, _ = first(self.__vehicleAward.getVehicles())
            vehName = vehicle.name
            vehIcon = RES_ICONS.getPersonalMissionVehicleAwardImage(ICONS_SIZES.X550, vehName.split(':')[-1])
            vehicleLevel = _ms(TOOLTIPS.level(vehicle.level))
            vehicleTypeIcon = getTypeBigIconPath(vehicle.type, vehicle.isElite)
            return {'vehicleSrc': vehIcon,
             'vehicleTypeIcon': vehicleTypeIcon,
             'vehicleName': vehicle.userName,
             'vehicleLevel': vehicleLevel} if vehIcon is not None else None

    def __packBadges(self, badges):
        result = []
        for badge in badges:
            result.append({'label': None,
             'imgSource': badge.getBigIcon() if self.__vehicleAward else badge.getIconX110(),
             'tooltip': None,
             'isSpecial': True,
             'specialAlias': TOOLTIPS_CONSTANTS.BADGE,
             'specialArgs': [badge.badgeID],
             'align': LABEL_ALIGN.RIGHT})

        return result

    def __getBonuses(self, tokensQuestsIds):
        finderFunc = finders.multipleTokenFinder(tokensQuestsIds)
        resultQuests = self._eventsCache.getHiddenQuests(finderFunc)
        vehicles = []
        achievements = []
        hasTankCamo = False
        hasNationCamo = False
        for quest in resultQuests.itervalues():
            if quest.getBonuses('customizations', []):
                hasTankCamo = True
                continue
            vehicles.extend(quest.getBonuses('vehicles', []))
            for bonus in quest.getBonuses('dossier', []):
                achievements.extend(bonus.getBadges())

            for bonus in quest.getBonuses('tokens', []):
                for token in bonus.getTokens():
                    if token.endswith(':camouflage'):
                        hasNationCamo = True

        self.__vehicleAward = first(vehicles)
        if hasTankCamo or hasNationCamo:
            if self.__vehicleAward:
                camouflageIcon = RES_ICONS.getBonusIcon(AWARDS_SIZES.BIG, 'camouflage')
            else:
                camouflageIcon = RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_AWARDS_110X110_CAMOUFLAGE
            if hasTankCamo and hasNationCamo:
                tooltipKeys = (TOOLTIPS.PERSONALMISSIONS_AWARDS_CAMOUFLAGEALL_HEADER, TOOLTIPS.PERSONALMISSIONS_AWARDS_CAMOUFLAGEALL_BODY)
            elif hasTankCamo:
                tooltipKeys = (TOOLTIPS.PERSONALMISSIONS_AWARDS_CAMOUFLAGEONLY_HEADER, TOOLTIPS.PERSONALMISSIONS_AWARDS_CAMOUFLAGEONLY_BODY)
            else:
                tooltipKeys = (TOOLTIPS.PERSONALMISSIONS_AWARDS_CAMOUFLAGENATION_HEADER, TOOLTIPS.PERSONALMISSIONS_AWARDS_CAMOUFLAGENATION_BODY)
            camouflageAward = {'imgSource': camouflageIcon,
             'itemName': 'camouflage',
             'tooltip': makeTooltip(*tooltipKeys)}
        else:
            camouflageAward = None
        return (sorted(achievements, reverse=True), camouflageAward)
