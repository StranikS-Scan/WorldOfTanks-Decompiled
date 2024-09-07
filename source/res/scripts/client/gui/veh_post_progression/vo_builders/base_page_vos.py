# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_progression/vo_builders/base_page_vos.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, getRoleTextWithIcon
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

def getBaseButtonsVO(vehicle):
    iconName = getIconResourceName(getNationLessName(vehicle.name))
    return {'shopIconPath': backport.image(R.images.gui.maps.shop.vehicles.c_360x270.dyn(iconName)()),
     'compareBtnVisible': True,
     'goToVehicleViewBtnVisible': True,
     'isPremium': vehicle.isPremium,
     'vehicleId': vehicle.intCD,
     'isEarlyAccess': vehicle.isEarlyAccess}


def getBaseDataVO(vehicle):
    return {'showDemountAllPairsBtn': False,
     'showExpBlock': False,
     'vehicleButton': {},
     'vehicleInfo': {},
     'nation': vehicle.nationName}


def getBaseTitleVO(vehicle):
    tankUserName = vehicle.userName
    return {'intCD': vehicle.intCD,
     'tankNameStr': text_styles.grandTitle(tankUserName),
     'tankNameStrSmall': text_styles.promoTitle(tankUserName),
     'statusStr': '',
     'roleText': getRoleTextWithIcon(vehicle.role, vehicle.roleLabel),
     'showInfoIcon': False}
