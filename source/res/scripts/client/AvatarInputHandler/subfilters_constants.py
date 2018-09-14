# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/subfilters_constants.py


class AVATAR_SUBFILTERS(object):
    CAMERA_SHOT_POINT = 0
    CAMERA_ARTY_SHOT_POINT = 1
    CAMERA_ARTY_TRANSLATION = 2
    CAMERA_ARTY_ROTATION = 3


class FILTER_INTERPOLATION_TYPE(object):
    LINEAR = 0
    SLERP_OF_CARTESIAN = 1
    ANGLE_RADIANS = 2
    SPHERICAL_RADIANS = 3
