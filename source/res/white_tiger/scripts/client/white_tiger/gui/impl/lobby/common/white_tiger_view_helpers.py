# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/common/white_tiger_view_helpers.py
from typing import List, TYPE_CHECKING
from gui.shared.missions.packers.bonus import TokenBonusUIPacker
from gui.impl.auxiliary.collections_helper import TmanTemplateBonusPacker
from gui.impl.auxiliary.rewards_helper import BlueprintBonusTypes
from gui.server_events.bonuses import mergeBonuses
from gui.shared.missions.packers.bonus import BonusUIPacker, ExtendedBlueprintBonusUIPacker, getDefaultBonusPackersMap, Customization3Dand2DbonusUIPacker, VehiclesBonusUIPacker
if TYPE_CHECKING:
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
WHITE_TIGER_MAPPING = {'tokens': TokenBonusUIPacker,
 'battleToken': TokenBonusUIPacker,
 'tmanToken': TmanTemplateBonusPacker,
 'vehicles': VehiclesBonusUIPacker,
 'customizations': Customization3Dand2DbonusUIPacker,
 BlueprintBonusTypes.BLUEPRINTS: ExtendedBlueprintBonusUIPacker,
 BlueprintBonusTypes.BLUEPRINTS_ANY: ExtendedBlueprintBonusUIPacker,
 BlueprintBonusTypes.FINAL_BLUEPRINTS: ExtendedBlueprintBonusUIPacker}
WIN_ICON_KEY = 'win'

def getWhiteTigerBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update(WHITE_TIGER_MAPPING)
    return BonusUIPacker(mapping)


def packBonuses(bonuses, showCount, isSpecial):
    result = []
    packer = getWhiteTigerBonusPacker()
    for bonus in mergeBonuses([ b for b in bonuses if b.isShowInGUI() ]):
        result.extend(packer.pack(bonus))

    return result[showCount:]
