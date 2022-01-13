# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/hero_tank_preview_constants.py
from collections import namedtuple
from helpers import dependency
from skeletons.gui.game_control import IHeroTankController
_VehicleData = namedtuple('_SpecialParamsVehicle', ('name', 'styleID'))
_OFFSPRING_VEHICLE = _VehicleData(name='usa:A127_TL_1_LPC', styleID=83)
_PreviewParams = namedtuple('_PreviewParams', ('buyButtonLabel', 'enterEvent', 'exitEvent'))
_SPECIAL_PREVIEW_PARAMS = {_OFFSPRING_VEHICLE: _PreviewParams(buyButtonLabel='offspring', enterEvent='ev_fest_off_hero_tank_in', exitEvent='ev_fest_off_hero_tank_out')}

@dependency.replace_none_kwargs(heroTanksControl=IHeroTankController)
def getHeroTankPreviewParams(heroTanksControl=None):
    vName = heroTanksControl.getCurrentVehicleName()
    vStyleId = heroTanksControl.getCurrentTankStyleId()
    specialParams = _SPECIAL_PREVIEW_PARAMS.get(_VehicleData(vName, vStyleId))
    if specialParams:
        return specialParams
    else:
        buyButtonLabel = heroTanksControl.getCurrentVehicleAction()
        return _PreviewParams(buyButtonLabel=buyButtonLabel, enterEvent=None, exitEvent=None)
