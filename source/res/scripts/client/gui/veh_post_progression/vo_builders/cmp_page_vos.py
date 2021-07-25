# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_progression/vo_builders/cmp_page_vos.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.veh_post_progression.vo_builders.base_page_vos import getBaseButtonsVO, getBaseDataVO, getBaseTitleVO
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

def _getButtonsVO(vehicle):
    baseVO = getBaseButtonsVO(vehicle)
    baseVO.update({'compareBtnVisible': False,
     'goToVehicleViewBtnVisible': False})
    return baseVO


def getDataVO(vehicle):
    baseVO = getBaseDataVO(vehicle)
    baseVO.update({'vehicleButton': _getButtonsVO(vehicle)})
    return baseVO


def getTitleVO(vehicle):
    baseVO = getBaseTitleVO(vehicle)
    tankUserName = vehicle.userName
    titleRes = R.strings.veh_post_progression.vehPostProgressionCmpView.title()
    baseVO.update({'tankNameStr': text_styles.grandTitle(backport.text(titleRes, title=tankUserName)),
     'tankNameStrSmall': text_styles.promoTitle(backport.text(titleRes, title=tankUserName))})
    return baseVO
