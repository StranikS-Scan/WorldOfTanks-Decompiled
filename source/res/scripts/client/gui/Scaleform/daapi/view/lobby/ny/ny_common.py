# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_common.py
from gui.Scaleform.genConsts.NY_CONSTANTS import NY_CONSTANTS
from gui.Scaleform.locale.NY import NY
from gui.server_events.awards_formatters import AWARDS_SIZES, QuestsBonusComposer, Ny18ToysFormatter, NY18DiscountFormatter, getMisssionsFormattersMap, AwardsPacker
from items.new_year_types import NATIONAL_SETTINGS
from new_year.new_year_controller import NewYearController
_REWARDS_RIBBON_DATA = {'ribbonType': 'ribbon1',
 'rendererLinkage': NY_CONSTANTS.NY_LINKAGE_RIBBON_AWARD_ANIM_RENDERER,
 'gap': 20,
 'rendererWidth': 80,
 'rendererHeight': 80,
 'awards': []}
NO_SETTING_BOX_ID = 'any'
SETTINGS_TO_LOCALIZATIONS_MAP = {'soviet': 'new_year',
 'modernWestern': 'christmas',
 'traditionalWestern': 'old_christmas',
 'asian': 'eastern_new_year'}
SORTED_NATIONS_SETTINGS = sorted(NATIONAL_SETTINGS, key=NewYearController.getSettingIndexInNationsOrder)

def getRewardsRibbonData(bonuses):
    _REWARDS_RIBBON_DATA['awards'] = _BONUSES_FORMATTER.getFormattedBonuses(bonuses, size=AWARDS_SIZES.BIG)
    return _REWARDS_RIBBON_DATA


def getFilterRadioButtons():
    result = [{'label': NY.getNationFilterLabel('all')}]
    for settingName in SORTED_NATIONS_SETTINGS:
        locKey = SETTINGS_TO_LOCALIZATIONS_MAP.get(settingName, settingName)
        result.append({'label': NY.getNationFilterLabel(locKey)})

    return result


class _Ny18BonusComposer(QuestsBonusComposer):

    def __init__(self, awardsFormatter=None):
        if awardsFormatter is None:
            formatters_map = getMisssionsFormattersMap()
            formatters_map['ny18Toys'] = Ny18ToysFormatter()
            formatters_map['battleToken'] = NY18DiscountFormatter()
            awardsFormatter = AwardsPacker(formatters_map)
        super(_Ny18BonusComposer, self).__init__(awardsFormatter)
        return

    def _packBonus(self, preformatted, size=AWARDS_SIZES.SMALL):
        base_data = super(_Ny18BonusComposer, self)._packBonus(preformatted, size)
        if isinstance(preformatted, Ny18ToysFormatter.XMassPreformattedBonus):
            base_data['level'] = preformatted.level
            base_data['rank'] = preformatted.rank
            base_data['setting'] = preformatted.setting
        base_data['bonusName'] = preformatted.bonusName
        return base_data


_BONUSES_FORMATTER = _Ny18BonusComposer()
