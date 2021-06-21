# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_porgression/vo_builders/main_page_vos.py
import typing
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.events import LoadViewEvent
from gui.shared.formatters import text_styles, getRoleText
from gui.shared.gui_items.Vehicle import getTypeBigIconPath, getNationLessName, getIconResourceName
from gui.Scaleform.daapi.view.lobby.go_back_helper import getBackBtnDescription
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import resolveStateTooltip
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from helpers import int2roman, dependency
from skeletons.gui.game_control import IVehicleComparisonBasket
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
_DEMOUNT_VISIBILITY_COUNT = 2

@dependency.replace_none_kwargs(cmpBasket=IVehicleComparisonBasket)
def getButtonsVO(vehicle, cmpBasket=None):
    comparationFullTooltip = TOOLTIPS.VEHPOSTPROGRESSIONVIEW_BUTTON_COMPARE_DISABLED
    comparisonState, comparisonTooltip = resolveStateTooltip(cmpBasket, vehicle, '', comparationFullTooltip)
    iconName = getIconResourceName(getNationLessName(vehicle.name))
    return {'shopIconPath': backport.image(R.images.gui.maps.shop.vehicles.c_360x270.dyn(iconName)()),
     'compareBtnVisible': True,
     'compareBtnEnabled': comparisonState,
     'compareBtnLabel': backport.text(R.strings.veh_post_progression.vehPostProgressionView.button.compare()),
     'compareBtnTooltip': comparisonTooltip,
     'previewBtnEnabled': vehicle.isPreviewAllowed(),
     'previewBtnLabel': backport.text(R.strings.veh_post_progression.vehPostProgressionView.button.preview()),
     'isPremium': vehicle.isPremium or vehicle.buyPrices.itemPrice.isActionPrice(),
     'isInInventory': vehicle.isInInventory,
     'vehicleId': vehicle.intCD,
     'vehicleState': 0,
     'previewAlias': VIEW_ALIAS.VEH_POST_PROGRESSION,
     'cmHandlerType': CONTEXT_MENU_HANDLER_TYPE.POST_PROGRESSION_VEHICLE}


def getDataVO(vehicle, freeExp, exitEvent):
    progressionAvailability = vehicle.postProgressionAvailability
    showDemountAllPairs = len(vehicle.postProgression.getInstalledMultiIds()[0]) >= _DEMOUNT_VISIBILITY_COUNT
    return {'showDemountAllPairsBtn': progressionAvailability.result and showDemountAllPairs,
     'showExpBlock': progressionAvailability.result,
     'backBtnLabel': backport.text(R.strings.menu.viewHeader.backBtn.label()),
     'backBtnDescrLabel': getBackBtnDescription(exitEvent, exitEvent.name, vehicle.shortUserName),
     'vehicleButton': getButtonsVO(vehicle),
     'vehicleInfo': {'isElite': vehicle.isElite,
                     'freeExp': freeExp,
                     'earnedXP': vehicle.xp},
     'nation': vehicle.nationName}


def getTitleVO(vehicle):
    tankTier = int2roman(vehicle.level)
    tankUserName = vehicle.userName
    return {'intCD': vehicle.intCD,
     'tankTierStr': text_styles.grandTitle(tankTier),
     'tankNameStr': text_styles.grandTitle(tankUserName),
     'tankTierStrSmall': text_styles.promoTitle(tankTier),
     'tankNameStrSmall': text_styles.promoTitle(tankUserName),
     'typeIconPath': getTypeBigIconPath(vehicle.type, vehicle.isElite),
     'isElite': vehicle.isElite,
     'statusStr': '',
     'roleText': getRoleText(vehicle.role, vehicle.roleLabel)}
