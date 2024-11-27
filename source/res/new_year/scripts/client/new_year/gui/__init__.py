# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/__init__.py


def replaceNewYearNavigation():
    from helpers import dependency
    from skeletons.gui.impl import INewYearNavigation
    from new_year.gui.impl.new_year.navigation import NewYearNavigation
    dependency.replaceInstance(INewYearNavigation, NewYearNavigation)


_NY_VIGNETTE_INTENSITY = 0.7

def addNewYearVignetteSettings(personality):
    from constants_utils import addVignetteSettings
    addVignetteSettings('hangar', _NY_VIGNETTE_INTENSITY, personality)
    addVignetteSettings('heroVehiclePreviewPage', _NY_VIGNETTE_INTENSITY, personality)
    addVignetteSettings('vehiclePreviewPage', _NY_VIGNETTE_INTENSITY, personality)
    addVignetteSettings('ny_navigation', _NY_VIGNETTE_INTENSITY, personality)
