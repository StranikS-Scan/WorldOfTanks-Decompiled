# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_progression/vo_builders/cfg_page_vos.py
import typing
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.events import LoadViewEvent
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.Scaleform.daapi.view.lobby.go_back_helper import getBackBtnDescription
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import resolveStateTooltip
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.veh_post_progression.vo_builders.base_page_vos import getBaseButtonsVO, getBaseDataVO, getBaseTitleVO
from helpers import int2roman, dependency
from skeletons.gui.game_control import IVehicleComparisonBasket
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
_DEMOUNT_VISIBILITY_COUNT = 2

@dependency.replace_none_kwargs(cmpBasket=IVehicleComparisonBasket)
def _getButtonsVO(vehicle, cmpBasket=None):
    baseVO = getBaseButtonsVO(vehicle)
    comparationFullTooltip = TOOLTIPS.VEHPOSTPROGRESSIONVIEW_BUTTON_COMPARE_DISABLED
    comparisonState, comparisonTooltip = resolveStateTooltip(cmpBasket, vehicle, '', comparationFullTooltip)
    baseVO.update({'compareBtnEnabled': comparisonState,
     'compareBtnLabel': backport.text(R.strings.veh_post_progression.vehPostProgressionView.button.compare()),
     'compareBtnTooltip': comparisonTooltip,
     'previewBtnEnabled': vehicle.isPreviewAllowed(),
     'previewBtnLabel': backport.text(R.strings.veh_post_progression.vehPostProgressionView.button.preview()),
     'isInInventory': vehicle.isInInventory,
     'vehicleState': 0,
     'previewAlias': VIEW_ALIAS.VEH_POST_PROGRESSION,
     'cmHandlerType': CONTEXT_MENU_HANDLER_TYPE.POST_PROGRESSION_VEHICLE})
    return baseVO


def getDataVO(vehicle, freeExp, exitEvent):
    baseVO = getBaseDataVO(vehicle)
    progressionAvailability = vehicle.postProgressionAvailability()
    showDemountAllPairs = len(vehicle.postProgression.getInstalledMultiIds()[0]) >= _DEMOUNT_VISIBILITY_COUNT
    demountIcon = backport.image(R.images.gui.maps.icons.library.destroy_hummer())
    baseVO.update({'showDemountAllPairsBtn': progressionAvailability.result and showDemountAllPairs,
     'showExpBlock': progressionAvailability.result,
     'vehicleButton': _getButtonsVO(vehicle),
     'vehicleInfo': {'isElite': vehicle.isElite,
                     'freeExp': freeExp,
                     'earnedXP': vehicle.xp},
     'backBtnLabel': backport.text(R.strings.menu.viewHeader.backBtn.label()),
     'backBtnDescrLabel': getBackBtnDescription(exitEvent, exitEvent.name, vehicle.shortUserName),
     'demountAllButtonLabel': text_styles.concatStylesToSingleLine(icons.makeImageTag(demountIcon, width=24, height=24, vSpace=-6), backport.text(R.strings.veh_post_progression.vehPostProgressionView.button.demountAllPairs()))})
    return baseVO


def getTitleVO(vehicle):
    baseVO = getBaseTitleVO(vehicle)
    tankTier = int2roman(vehicle.level)
    baseVO.update({'showInfoIcon': True,
     'tankTierStr': text_styles.grandTitle(tankTier),
     'tankTierStrSmall': text_styles.promoTitle(tankTier),
     'typeIconPath': getTypeBigIconPath(vehicle.type, vehicle.isElite),
     'isElite': vehicle.isElite})
    return baseVO
