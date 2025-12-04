# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/vignette_settings_switcher.py
import BigWorld
_VIEWS_TO_VIGNETTE_CHANGE = {}
_defaultVignetteIntensity = None

def checkVignetteSettings(viewName):
    global _defaultVignetteIntensity
    vignetteSettings = BigWorld.PyRenderSettings().getVignetteSettings()
    if _defaultVignetteIntensity is None:
        _defaultVignetteIntensity = vignetteSettings.w
    vignetteSettings.w = _VIEWS_TO_VIGNETTE_CHANGE.get(viewName, _defaultVignetteIntensity)
    BigWorld.PyRenderSettings().setVignetteSettings(vignetteSettings)
    return
