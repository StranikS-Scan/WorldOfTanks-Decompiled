# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/py_object_wrappers.py
try:
    import _wulf as _py_objects
except ImportError:
    import wulf_wrapper as _py_objects

PyObjectArray = _py_objects.PyObjectArray
PyObjectCommand = _py_objects.PyObjectCommand
PyGuiApplication = _py_objects.PyGuiApplication
PyObjectView = _py_objects.PyObjectView
PyObjectViewModel = _py_objects.PyObjectViewModel
PyObjectWindow = _py_objects.PyObjectWindow
PyObjectWindowsArea = _py_objects.PyObjectWindowsArea
isTranslatedKeyValid = _py_objects.isTranslatedKeyValid
isTranslatedTextExisted = _py_objects.isTranslatedTextExisted
getTranslatedText = _py_objects.getTranslatedText
getImagePath = _py_objects.getImagePath
getSoundEffectId = _py_objects.getSoundEffectId
getTranslatedTextByResId = _py_objects.getTranslatedTextByResId
__all__ = ('PyObjectArray', 'PyObjectCommand', 'PyGuiApplication', 'PyObjectView', 'PyObjectViewModel', 'PyObjectWindow', 'PyObjectWindowsArea', 'isTranslatedKeyValid', 'isTranslatedTextExisted', 'getTranslatedText', 'getImagePath', 'getSoundEffectId', 'getTranslatedTextByResId')
