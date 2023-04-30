# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/skill_parameters/formatters.py
import typing
from gui.impl import backport
from gui.impl.backport import getNiceNumberFormat
from gui.impl.gen import R
from gui.shared.gui_items import VEHICLE_ATTR_TO_KPI_NAME_MAP
from gui.shared.items_parameters.param_name_helper import getVehicleParameterText
from items.components.component_constants import EMPTY_STRING
from items.components.skills_constants import ParamMeasureType, ParamSignType
if typing.TYPE_CHECKING:
    from items.readers.skills_readers import SkillDescrsArg

def getDescriptionValue(paramDescrArg, value):
    return _formatParamValue(paramDescrArg, abs(value))


def _formatParamValue(paramDescrArg, value):
    convertedValue = value * 100 if paramDescrArg.measureType is ParamMeasureType.PERCENTS else value
    formattedValue = str(getNiceNumberFormat(round(convertedValue, 3)))
    measuredValue = getMeasureText(formattedValue, paramDescrArg)
    return measuredValue


def getMeasureText(value, perkparamDescrArg):
    return str(backport.text(R.strings.crew_perks.measureType.dyn(perkparamDescrArg.measureType)(), value))


def getKpiValue(paramDescrArg, value):
    sign = getParamSign(paramDescrArg.sign)
    result = sign + _formatParamValue(paramDescrArg, abs(value))
    return result


def getParamSign(value):
    return EMPTY_STRING if value is ParamSignType.SIGN_LESS else str(backport.text(R.strings.crew_perks.sign.dyn(value)()))


def getKpiDescription(paramDescrArg):
    paramName = paramDescrArg.name
    if paramDescrArg.sign is ParamSignType.SIGN_LESS:
        return str(backport.text(R.strings.tank_setup.kpi.bonus.neutral.dyn(paramName)()))
    isPositive = paramDescrArg.sign is ParamSignType.PLUS
    if paramName in VEHICLE_ATTR_TO_KPI_NAME_MAP:
        kpiText = getVehicleParameterText(VEHICLE_ATTR_TO_KPI_NAME_MAP[paramName], isPositive=isPositive, isTTC=True)
    else:
        kpiText = getVehicleParameterText(paramName, isPositive=isPositive, isTTC=True)
    return str(backport.text(kpiText))
