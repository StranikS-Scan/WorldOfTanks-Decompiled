# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/py_object_wrappers.py
from constants import IS_EDITOR
if not IS_EDITOR:
    try:
        import _wulf as _py_objects
    except ImportError:
        import wulf_wrapper as _py_objects

else:
    import wulf_wrapper as _py_objects
PyObjectArray = _py_objects.PyObjectArray
PyObjectCommand = _py_objects.PyObjectCommand
PyGuiApplication = _py_objects.PyGuiApplication
PyObjectViewSettings = _py_objects.PyObjectViewSettings
PyObjectView = _py_objects.PyObjectView
PyObjectViewModel = _py_objects.PyObjectViewModel
PyObjectWindowSettings = _py_objects.PyObjectWindowSettings
PyObjectWindow = _py_objects.PyObjectWindow
PyObjectWindowsArea = _py_objects.PyObjectWindowsArea
isTranslatedKeyValid = _py_objects.isTranslatedKeyValid
isTranslatedTextExisted = _py_objects.isTranslatedTextExisted
getTranslatedText = _py_objects.getTranslatedText
getTranslatedPluralText = _py_objects.getTranslatedPluralText
getImagePath = _py_objects.getImagePath
getSoundEffectId = _py_objects.getSoundEffectId
getLayoutPath = _py_objects.getLayoutPath
getTranslatedTextByResId = _py_objects.getTranslatedTextByResId
getTranslatedPluralTextByResId = _py_objects.getTranslatedPluralTextByResId
getTranslatedKey = _py_objects.getTranslatedKey
getNumberFormat = _py_objects.getNumberFormat
getRealFormat = _py_objects.getRealFormat
getTimeFormat = _py_objects.getTimeFormat
getDateFormat = _py_objects.getDateFormat
caseMap = _py_objects.caseMap
__all__ = ('PyObjectArray', 'PyObjectCommand', 'PyGuiApplication', 'PyObjectViewSettings', 'PyObjectView', 'PyObjectViewModel', 'PyObjectWindowSettings', 'PyObjectWindow', 'PyObjectWindowsArea', 'isTranslatedKeyValid', 'isTranslatedTextExisted', 'getTranslatedText', 'getTranslatedPluralText', 'getImagePath', 'getSoundEffectId', 'getLayoutPath', 'getTranslatedTextByResId', 'getTranslatedPluralTextByResId', 'getTranslatedKey', 'getNumberFormat', 'getRealFormat', 'getTimeFormat', 'getDateFormat', 'caseMap')
