# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/anomalies_utils.py
from __future__ import absolute_import
import re
from builtins import range
import typing
import BigWorld
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from halloween.configs.hw_upgrades_config import getConfig
from halloween.skeletons.halloween_anomalies_controller import IHalloweenAnomaliesController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.impl import backport
from gui.impl.gen import R
from gui import makeHtmlString
from gui.battle_control import avatar_getter
if typing.TYPE_CHECKING:
    from typing import Optional, List, Set
_TEXT_PATH_ANOMALIES = R.strings.halloween_buffs.buffs

class _StyleBase(object):
    DEFAULT_STYLE = ''
    EPIC_STYLE = ''
    SECRET_STYLE = ''

    @classmethod
    def getStyle(cls, isEpic=False, isSecret=False):
        style = cls.DEFAULT_STYLE
        if isSecret:
            style = cls.SECRET_STYLE
        elif isEpic:
            style = cls.EPIC_STYLE
        return style


class _ParamStyle(_StyleBase):
    DEFAULT_STYLE = 'boldTitle'
    EPIC_STYLE = 'boldTitleEpic'
    SECRET_STYLE = 'boldTitleSecret'


class _DescriptionStyle(_StyleBase):
    DEFAULT_STYLE = 'hwAnomalyDescriptor'
    EPIC_STYLE = 'hwAnomalyDescriptorEpic'
    SECRET_STYLE = 'hwAnomalyDescriptorSecret'


class _TitleStyle(_StyleBase):
    DEFAULT_STYLE = 'title'
    EPIC_STYLE = 'titleEpic'
    SECRET_STYLE = 'titleSecret'


@dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def selectAnomaly(anomalyIDx=None, anomalyID=None, sessionProvider=None):
    if sessionProvider is None or sessionProvider.isReplayPlaying or anomalyIDx is None and anomalyID is None:
        return
    else:
        vehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID, None)
        if not vehicle:
            return
        if anomalyIDx is None:
            anomalyIDx = vehicle.HWVehicleOptionsRequesterComponent.upgradeOptions.index(anomalyID)
        hwBattleGuiCtrl = sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        hwBattleGuiCtrl.onSelectAnomaly(anomalyIDx)
        vehicle.HWVehicleOptionsRequesterComponent.selectUpgrade(anomalyIDx)
        return


@dependency.replace_none_kwargs(anomaliesCtrl=IHalloweenAnomaliesController)
def isAnomalyInCombo(anomalyID, anomaliesCtrl=None):
    vehicle = BigWorld.player().vehicle
    if vehicle and vehicle.isPlayerVehicle and anomaliesCtrl is not None:
        playerUsedAnomalies = vehicle.HWVehicleAnomaliesComponent.usedAnomalies
        for recipe in anomaliesCtrl.recipes.values():
            if anomalyID in recipe.ingredients:
                return bool(set(recipe.ingredients) & set(playerUsedAnomalies))

    return False


def isAnomalyNew(anomalyID):
    vehicle = BigWorld.player().vehicle
    return anomalyID not in vehicle.HWVehicleAnomaliesComponent.knownAnomalies if vehicle and vehicle.isPlayerVehicle else False


def _getParams(anomalyName):
    config = getConfig()
    vehicle = avatar_getter.getPlayerVehicle()
    vehicleName = vehicle.typeDescriptor.name.split(':')[1]
    return config.upgrade[anomalyName].getVehicleConfig(vehicleName).param


def anomalyHeader(anomalyName):
    return backport.text(_TEXT_PATH_ANOMALIES.dyn(anomalyName).header())


def anomalyBody(anomalyName):
    params = _getParams(anomalyName)
    body = backport.text(_TEXT_PATH_ANOMALIES.dyn(anomalyName).body(), **params)
    return re.sub('\\{\\{[^}]*\\}\\}', '', body)


def anomalyTitle(anomalyName, isEpic=False, isSecret=False):
    htmlPath = 'html_templates:battle/anomalyTitle'
    title = anomalyHeader(anomalyName=anomalyName)
    return makeHtmlString(htmlPath, _TitleStyle.getStyle(isEpic, isSecret), {'text': title})


def anomalyDescriptionList(anomalyName, valueConvert=None, isEpic=False, isSecret=False):
    htmlPath = 'html_templates:battle/textStyle'
    params = _getParams(anomalyName)
    descriptions = _TEXT_PATH_ANOMALIES.dyn(anomalyName).dyn('description')
    values = _TEXT_PATH_ANOMALIES.dyn(anomalyName).dyn('value')
    info = []
    for idx in range(1, descriptions.length() + 1):
        styleBoldParam = _ParamStyle.getStyle(isEpic, isSecret)
        value = makeHtmlString(htmlPath, styleBoldParam, {'text': backport.text(values.num(idx)(), **params)}) if values.num(idx).exists() else ''
        if not descriptions.num(idx).exists():
            continue
        description = backport.text(descriptions.num(idx)(), value=value)
        desc = makeHtmlString(htmlPath, _DescriptionStyle.getStyle(isEpic, isSecret), {'text': description})
        if valueConvert:
            desc = valueConvert(desc)
        info.append(desc)

    return info


def getKnownAnomaliesIDs():
    knownAnomaliesIDs = set()
    vehicle = BigWorld.player().vehicle
    if vehicle and vehicle.isPlayerVehicle:
        knownAnomaliesIDs.update(vehicle.HWVehicleAnomaliesComponent.knownAnomalies)
    return knownAnomaliesIDs
