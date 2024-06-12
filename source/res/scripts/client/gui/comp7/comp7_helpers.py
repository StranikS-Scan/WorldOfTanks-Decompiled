# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/comp7/comp7_helpers.py
import typing
from gui import GUI_SETTINGS
if typing.TYPE_CHECKING:
    from typing import List

def getWhatsNewPages():
    return GUI_SETTINGS.whatsNewPageComp7Slides.get('pages', [])


def getIntroPages():
    return GUI_SETTINGS.IntroPagesComp7Slides.get('pages', [])


def getWhatsNewSeasonVehicles():
    return GUI_SETTINGS.whatsNewPageComp7Slides.get('seasonVehicles', [])


def getIntroVehicles():
    return GUI_SETTINGS.IntroPagesComp7Slides.get('seasonVehicles', [])


def getWhatsNewMapsAdded():
    return GUI_SETTINGS.whatsNewPageComp7Slides.get('newMaps', [])


def getWhatsNewMapsDeleted():
    return GUI_SETTINGS.whatsNewPageComp7Slides.get('deprecatedMaps', [])
