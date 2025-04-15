# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/avatar_input_handler/hb_map_case_mode.py
import logging
import Math
from AvatarInputHandler.DynamicCameras import ArcadeCamera
import AvatarInputHandler.MapCaseMode as BaseMapCaseMode
from historical_battles.hb_constants import CTRL_MODE_NAME
logger = logging.getLogger(__name__)

class _ArtilleryStrikeHBSelector(BaseMapCaseMode._ArcadeBomberStrikeSelector):
    pass


class _ArtilleryMortarHBSelector(BaseMapCaseMode._ArcadeBomberStrikeSelector):
    pass


class _ArtilleryRocketHBSelector(BaseMapCaseMode._ArcadeBomberStrikeSelector):
    pass


class _BomberHBSelector(BaseMapCaseMode._ArcadeBomberStrikeSelector):
    pass


class _AttackPlaneHBSelector(BaseMapCaseMode._DirectionalAreaStrikeSelector):
    pass


class _MinefieldHBSelector(BaseMapCaseMode._ArcadeFLMinesSelector):
    pass


class _ReconPlaneHBSelector(BaseMapCaseMode._DirectionalAreaStrikeSelector):
    pass


class AoeArcadeMapCaseControlMode(BaseMapCaseMode.ArcadeMapCaseControlMode):
    MODE_NAME = CTRL_MODE_NAME.AOE_MAP_CASE_ARCADE

    def _createCamera(self, config, offset=None):
        if offset is None:
            offset = Math.Vector2(0, 0)
        return ArcadeCamera.ArcadeCameraAOE(config, offset)
