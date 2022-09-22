# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCQuestsView.py
from constants import ARENA_BONUS_TYPE
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.MissionDetailsContainerViewMeta import MissionDetailsContainerViewMeta
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events import formatters
from gui.server_events.awards_formatters import LABEL_ALIGN
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString
from skeletons.gui.game_control import IBootcampController
from uilogging.deprecated.bootcamp.constants import BC_LOG_KEYS, BC_LOG_ACTIONS
from uilogging.deprecated.bootcamp.loggers import BootcampLogger

class BCQuestsView(LobbySubView, MissionDetailsContainerViewMeta):
    __background_alpha__ = 0.8
    _bootcamp = dependency.descriptor(IBootcampController)
    _LINES_IN_DESCR = 3
    _TANK_LEVEL = 3
    _COMMA = ', '
    _OBTAINED_IMAGE_OFFSET = 6
    _MISSIONS_DONE = 0
    _MISSIONS_COUNT = 1
    _AWARD_LABEL_PADDING = 20
    _GOLD_LABEL = '500'
    _PAGES_LINKAGE = 'MissionDetailsPageGroup'
    uiBootcampLogger = BootcampLogger(BC_LOG_KEYS.BC_QUESTS_VIEW)

    def closeView(self):
        self.uiBootcampLogger.log(BC_LOG_ACTIONS.CLOSE)
        self.app.setBackgroundAlpha(0.0)
        self.destroy()

    def requestMissionData(self, index):
        isObtained = not self._bootcamp.needAwarding()
        vehicleSelector = self.getComponent(QUESTS_ALIASES.MISSIONS_VEHICLE_SELECTOR_ALIAS)
        if vehicleSelector is not None:
            criteria = REQ_CRITERIA.VEHICLE.LEVELS([self._TANK_LEVEL]) | REQ_CRITERIA.IN_OWNERSHIP
            vehicleSelector.setCriteria(None, criteria, [])
        bTypesData = formatters.packMissionBonusTypeElements([ARENA_BONUS_TYPE.REGULAR])
        bTypes = self._COMMA.join([ iconData.iconLabel for iconData in bTypesData ])
        tooltipBody = makeString(QUESTS.MISSIONDETAILS_CONDITIONS_BATTLEBONUSTYPE_BODY, battleBonusTypes=bTypes)
        missionData = {'title': text_styles.promoSubTitle(backport.text(R.strings.bootcamp.quest.title())),
         'battleConditions': [{'rendererLinkage': MISSIONS_ALIASES.BATTLE_CONDITION,
                               'linkageBig': MISSIONS_ALIASES.ANG_GROUP_BIG_LINKAGE,
                               'isDetailed': True,
                               'data': [{'title': text_styles.promoSubTitle(backport.text(R.strings.bootcamp.quest.name())),
                                         'description': text_styles.highlightText(backport.text(R.strings.bootcamp.quest.condition())),
                                         'state': MISSIONS_ALIASES.NONE,
                                         'icon': backport.image(R.images.gui.maps.icons.quests.battleCondition.c_128.icon_battle_condition_battles_128x128()),
                                         'maxDescLines': self._LINES_IN_DESCR}],
                               'linkage': MISSIONS_ALIASES.ANG_GROUP_DETAILED_LINKAGE}],
         'statusLabel': text_styles.concatStylesWithSpace(icons.inProgress(), text_styles.standard(backport.text(R.strings.quests.missionDetails.missionsComplete(), count=text_styles.stats(self._MISSIONS_DONE), total=text_styles.standard(self._MISSIONS_COUNT)))),
         'awards': [{'label': text_styles.gold(backport.text(R.strings.menu.premium.packet.days3())),
                     'padding': self._AWARD_LABEL_PADDING,
                     'imgSource': backport.image(R.images.gui.maps.icons.quests.bonuses.big.premium_plus_3()),
                     'align': LABEL_ALIGN.RIGHT,
                     'tooltip': TOOLTIPS.AWARDITEM_PREMIUM,
                     'obtainedImage': backport.image(R.images.gui.maps.icons.library.awardObtained()),
                     'isObtained': isObtained,
                     'obtainedImageOffset': self._OBTAINED_IMAGE_OFFSET}, {'label': text_styles.gold(self._GOLD_LABEL),
                     'padding': self._AWARD_LABEL_PADDING,
                     'imgSource': backport.image(R.images.gui.maps.icons.quests.bonuses.big.gold()),
                     'align': LABEL_ALIGN.RIGHT,
                     'tooltip': TOOLTIPS.AWARDITEM_GOLD,
                     'obtainedImage': backport.image(R.images.gui.maps.icons.library.awardObtained()),
                     'isObtained': isObtained,
                     'obtainedImageOffset': self._OBTAINED_IMAGE_OFFSET}],
         'background': 'default',
         'prebattleConditions': [formatters.packMissionPrebattleCondition(text_styles.main(bTypesData[0].iconLabel), ''.join([ iconData.icon for iconData in bTypesData ]), makeTooltip(QUESTS.MISSIONDETAILS_CONDITIONS_BATTLEBONUSTYPE, tooltipBody))],
         'uiDecoration': backport.image(R.images.gui.maps.icons.quests.decorations.default_750x264()),
         'statusTooltipData': {}}
        self.as_setMissionDataS(missionData)
        return

    def _populate(self):
        self.uiBootcampLogger.log(BC_LOG_ACTIONS.SHOW)
        super(BCQuestsView, self)._populate()
        self.as_setInitDataS({'pages': [{'buttonsGroup': self._PAGES_LINKAGE,
                    'pageIndex': 0,
                    'selected': True}]})
