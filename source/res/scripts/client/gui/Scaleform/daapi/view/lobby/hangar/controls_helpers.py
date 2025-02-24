# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/controls_helpers.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.limited_ui.lui_rules_storage import LUI_RULES
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.game_control import IEasyTankEquipController, ILimitedUIController
if typing.TYPE_CHECKING:
    from gui.vehicle_view_states import IVehicleViewState
EasyTankEquipSetupData = typing.NamedTuple('EasyTankEquipSetupData', [('visible', bool), ('enabled', bool), ('tooltip', str)])

class IHangarControlsHelper(object):
    __slots__ = ()

    @classmethod
    def getEasyTankEquipSetupData(cls, state, needToShowRepairButton, isAvailableForVehicleByLevel):
        raise NotImplementedError


class DefaultHangarHelper(IHangarControlsHelper):
    __slots__ = ()

    @classmethod
    def getEasyTankEquipSetupData(cls, state, needToShowRepairButton, isAvailableForVehicleByLevel):
        return EasyTankEquipSetupData(False, False, '')


class RandomHangarHelper(IHangarControlsHelper):
    __slots__ = ()
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __easyTankEquipController = dependency.descriptor(IEasyTankEquipController)
    _RES_SHORTCUT = R.strings.tooltips.hangar.easyTankEquip

    @classmethod
    def getEasyTankEquipSetupData(cls, state, needToShowRepairButton, isAvailableForVehicleByLevel):
        isEasyTankEquipAvailableForVehicle = state.isEasyTankEquipEnabled()
        isEasyTankEquipAvailable = isEasyTankEquipAvailableForVehicle and cls.__easyTankEquipController.config.enabled
        easyTankEquipVisibility = state.isEasyTankEquipVisible() and not needToShowRepairButton and cls.__limitedUIController.isRuleCompleted(LUI_RULES.EasyTankEquipEntryPoint)
        if isEasyTankEquipAvailable:
            tooltipHeader = text_styles.middleTitle(backport.text(cls._RES_SHORTCUT.header()))
            tooltipBody = text_styles.main(backport.text(cls._RES_SHORTCUT.body()))
        elif not isEasyTankEquipAvailableForVehicle:
            if not isAvailableForVehicleByLevel:
                tooltipHeader = None
                tooltipBody = text_styles.main(backport.text(cls._RES_SHORTCUT.disabled.inappropriateVehicle.body(), tier=cls.__easyTankEquipController.config.minVehicleLevel))
            else:
                tooltipHeader = text_styles.middleTitle(backport.text(cls._RES_SHORTCUT.disabled.default.header()))
                tooltipBody = text_styles.main(backport.text(cls._RES_SHORTCUT.disabled.default.body()))
        else:
            tooltipHeader = text_styles.middleTitle(backport.text(cls._RES_SHORTCUT.disabled.switch.header()))
            tooltipBody = text_styles.main(backport.text(cls._RES_SHORTCUT.disabled.switch.body()))
        return EasyTankEquipSetupData(easyTankEquipVisibility, isEasyTankEquipAvailable, makeTooltip(header=tooltipHeader, body=tooltipBody))
