# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/quests/utils.py
import typing
from epic_missions_config import getQuestConfig
from gui.impl import backport
from gui.impl.gen import R

def getQuestUiData(questName):
    config = getQuestConfig(questName)
    for itemData in config.itervalues():
        return (getQuestItemIcon(itemData), getQuestItemDescr(itemData), getQuestItemGoal(itemData))


def getQuestItemDescr(itemData):
    itemDescription = itemData['description']
    descrDyn = R.strings.fl_quests.dyn(itemDescription)()
    configs = itemData.get('config', {})
    paramsObj = configs.get('params', {}).copy()
    paramsObj.update(configs)
    for key, value in paramsObj.iteritems():
        if isinstance(value, int):
            paramsObj[key] = backport.getNiceNumberFormat(value)

    if descrDyn <= 0:
        return ''
    return backport.ntext(descrDyn, configs.get('goal', 0), **paramsObj) if itemDescription.endswith('plural') else backport.text(descrDyn, **paramsObj)


def getQuestItemGoal(itemData):
    configs = itemData.get('config', {})
    return configs.get('goal', configs.get('uniqueGoal', 1))


def getQuestItemIcon(itemData):
    return itemData['icon']
