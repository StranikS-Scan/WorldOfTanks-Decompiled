# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/TankmenInterface.py
# Compiled at: 2019-03-08 18:30:21
import BigWorld
from CurrentVehicle import g_currentVehicle
from helpers.i18n import makeString
from adisp import async, process
from gui.Scaleform.windows import UIInterface
from gui import SystemMessages
from items.tankmen import getSkillsConfig, SKILL_NAMES, MAX_SKILL_LEVEL, SKILLS_BY_ROLES, PERKS
from items import vehicles, tankmen
from helpers.i18n import convert
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.utils.requesters import Requester, StatsRequester
from gui.Scaleform.utils.gui_items import formatTankmanPrice, getItemByCompact, getTankmanOpertnSysMessageType, isVehicleObserver
from gui.Scaleform.utils.gui_items import isVehicleObserver
from gui.Scaleform.utils.functions import makeTooltip
from AccountCommands import LOCK_REASON
from account_helpers.AccountPrebattle import AccountPrebattle
from gui.Scaleform.utils.dossiers_utils import getDossierMedals
from constants import DOSSIER_TYPE

class TankmenInterface(UIInterface):
    TANKMEN_ORDER = {'commander': 0,
     'gunner': 1,
     'driver': 2,
     'radioman': 3,
     'loader': 4}
    STATS_BLOCKS = {'tankman': (('common', ('battlesCount',)), ('studying', ('nextSkillXPLeft', 'avgExperience', 'nextSkillBattlesLeft'))),
     'medals': ('warrior', 'invader', 'sniper', 'defender', 'steelwall', 'supporter', 'scout', 'medalWittmann', 'medalOrlik', 'medalOskin', 'medalHalonen', 'medalBurda', 'medalBillotte', 'medalKolobanov', 'medalFadin')}

    def __init__(self, creator):
        UIInterface.__init__(self)
        self.creator = creator

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.addExternalCallbacks({'tankmen.buyTankman': self.onBuyTankman,
         'tankmen.equipTankman': self.onEquipTankman,
         'tankmen.unloadTankman': self.onUnloadTankman,
         'tankmen.dismissTankman': self.onDismissTankman,
         'tankmen.retrainingTankman': self.onRetrainingTankman,
         'tankmen.updateVehicleClassDropdown': self.updateVehicleClassDropdown,
         'tankmen.updateVehicleTypeDropdown': self.updateVehicleTypeDropdown,
         'tankmen.updateRoleDropdown': self.updateRoleDropdown,
         'tankmen.updateSkillsList': self.onUpdateSkillsList,
         'tankmen.showRecruitWindow': self.onShowRecruitWindow,
         'tankmen.addSkill': self.onAddSkill,
         'tankmen.dropSkill': self.onDropSkill,
         'tankmen.getPersonalCase': self.onGetPersonalCase,
         'tankmen.populateRetrainingWindow': self.onPopulateRetrainingWindow,
         'tankmen.getTankmanStats': self.onGetTankmanStats,
         'tankmen.getTankmanDocs': self.onGetTankmanDocs,
         'tankmen.replaceTankman': self.onReplaceTankman,
         'tankmemInterface.dropSkill': self.dropSkill})
        Waiting.hide('loadPage')

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks('tankmen.buyTankman', 'tankmen.equipTankman', 'tankmen.unloadTankman', 'tankmen.dismissTankman', 'tankmen.retrainingTankman', 'tankmen.updateVehicleClassDropdown', 'tankmen.updateVehicleTypeDropdown', 'tankmen.updateRoleDropdown', 'tankmen.showRecruitWindow', 'tankmen.updateSkillsList', 'tankmen.addSkill', 'tankmen.dropSkill', 'tankmen.getPersonalCase', 'tankmen.populateRetrainingWindow', 'tankmen.getTankmanStats', 'tankmen.getTankmanDocs', 'tankmen.replaceTankman', 'tankmemInterface.dropSkill', 'tankmen.getSkillDropWindow', 'tankmen.calcSkillDropWindow')
        del self.creator
        UIInterface.dispossessUI(self)

    def __updateCreator(self):
        if self.creator:
            self.creator.update()

    @async
    @process
    def __buyTankmanProcess(self, nationID, vehicleTypeID, role, tmanCostTypeIdx, slot, callback):
        upgradeParams = yield StatsRequester().getTankmanCost()
        freeTmanLeft = yield StatsRequester().getFreeTankmanLeft()
        if freeTmanLeft == 0 and tmanCostTypeIdx == 0:
            callback((False, '#system_messages:buyTankman/limit', None))

        def buyResponse(code, tmanInvID, tmanCompDescr):
            if code >= 0:
                callback((True, makeString('#system_messages:buyTankman/success') + formatTankmanPrice(upgradeParams, tmanCostTypeIdx), tmanInvID))
            else:
                callback((False, '#system_messages:buyTankman/server_error', None))
            return

        slots = yield StatsRequester().getTankmenBerthsCount()
        tankmen = yield Requester('tankman').getFromInventory()
        tankmenInBarracks = 0
        for tankman in tankmen:
            if not tankman.isInTank:
                tankmenInBarracks += 1

        if tankmenInBarracks >= slots:
            message = '#system_messages:buyTankman/not_enought_space'
        else:
            assert hasattr(BigWorld.player(), 'shop'), 'Request from shop is not possible'
            self.__callback = callback
            BigWorld.player().shop.buyTankman(nationID, vehicleTypeID, role, tmanCostTypeIdx, buyResponse)
            return
        if callback is not None:
            callback((False, message, None))
        return

    @process
    def __buyTankman(self, nationID, vehicleTypeID, role, tmanCostTypeIdx, slot):
        Waiting.show('recruting')
        success, message, tankmanID = yield self.__buyTankmanProcess(nationID, vehicleTypeID, role, tmanCostTypeIdx, slot)
        SystemMessages.pushI18nMessage(message, type=getTankmanOpertnSysMessageType(tmanCostTypeIdx) if success else SystemMessages.SM_TYPE.Error)
        if success and tankmanID is not None and slot is not None:
            tankmen = yield Requester('tankman').getFromInventory()
            for tman in tankmen:
                if tman.inventoryId == tankmanID:
                    tankman = tman
                    break

            vcls = yield Requester('vehicle').getFromInventory()
            for v in vcls:
                if v.descriptor.type.id == (nationID, vehicleTypeID):
                    vehicleInvId = v.inventoryId

            self.__equipTankman(tankman, vehicleInvId, int(slot))
        else:
            self.__updateCreator()
        Waiting.hide('recruting')
        return

    def onBuyTankman(self, callbackID, nationID, typeID, role, tmanCostTypeIdx, slot):
        self.__buyTankman(int(nationID), int(typeID), role, int(tmanCostTypeIdx), slot)

    @process
    def __equipTankman(self, tankman, vehicleID, slot):
        Waiting.show('equiping')
        if vehicleID is None:
            vehicleID = g_currentVehicle.vehicle.inventoryId
        success, message = yield tankman.equip(vehicleID, slot)
        SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Information if success else SystemMessages.SM_TYPE.Error)
        self.__updateCreator()
        Waiting.hide('equiping')
        return

    def onEquipTankman(self, callbackID, tankmanCompact, vehicleID, slot):
        tankman = getItemByCompact(tankmanCompact)
        if tankman is not None:
            self.__equipTankman(tankman, vehicleID, slot)
        return

    @process
    def __unloadTankman(self, tankman):
        Waiting.show('equiping')
        success, message = yield tankman.unload()
        SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Information if success else SystemMessages.SM_TYPE.Error)
        self.call('tankmen.unloadCompleted', [])
        self.__updateCreator()
        Waiting.hide('equiping')

    def onUnloadTankman(self, callbackID, tankmanCompact):
        tankman = getItemByCompact(tankmanCompact)
        if tankman is not None:
            self.__unloadTankman(tankman)
        return

    @process
    def __dismissTankman(self, tankman):
        Waiting.show('updating')
        success, message = yield tankman.dismiss()
        SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Information if success else SystemMessages.SM_TYPE.Error)
        self.__updateCreator()
        Waiting.hide('updating')

    def onDismissTankman(self, callbackID, tankmanCompact):
        tankman = getItemByCompact(tankmanCompact)
        self.__dismissTankman(tankman)

    @process
    def __retrainingTankman(self, tankman, vehicleTypeID, tmanCostTypeIdx):
        vehicleType = vehicles.g_cache.vehicle(tankman.nation, int(vehicleTypeID))
        success, message = yield tankman.respec(vehicleType.compactDescr, int(tmanCostTypeIdx))
        SystemMessages.pushI18nMessage(message, type=getTankmanOpertnSysMessageType(tmanCostTypeIdx) if success else SystemMessages.SM_TYPE.Error)
        self.call('tankmen.retrainingComplete', [])
        self.__updateCreator()
        Waiting.hide('retraining')

    @process
    def onRetrainingTankman(self, callbackID, tankmanCompact, vehicleTypeID, tmanTypeCost):
        Waiting.show('retraining')
        tankman = getItemByCompact(tankmanCompact)
        upgradeParams = yield StatsRequester().getTankmanCost()
        gold = yield StatsRequester().getGold()
        if tankman is not None or upgradeParams[2]['gold'] > gold:
            self.__retrainingTankman(tankman, vehicleTypeID, tmanTypeCost)
        return

    def __getSkillNextLevelCost(self, tankman):
        nextSkillLevel = tankman.descriptor.roleLevel if len(tankman.descriptor.skills) == 0 or tankman.descriptor.roleLevel != MAX_SKILL_LEVEL else tankman.descriptor.lastSkillLevel
        return tankman.descriptor.levelUpXpCost(nextSkillLevel, len(tankman.descriptor.skills) if tankman.descriptor.roleLevel == 100 else 0) - tankman.descriptor.freeXP

    def __isNewSkillReady(self, tankman):
        if len(tankman.skills) == 0:
            return tankman.roleLevel == 100
        return tankman.lastSkillLevel == 100

    def __getData(self, item, dossier, extDossier, tankman):
        if item == 'effectiveShots':
            if dossier['shots'] != 0:
                return '%d%%' % round(float(dossier['hits']) / dossier['shots'] * 100)
            return '0%'
        if item == 'avgExperience':
            if extDossier['battlesCount'] != 0:
                return BigWorld.wg_getIntegralFormat(round(float(extDossier['xp']) / extDossier['battlesCount']))
            return BigWorld.wg_getIntegralFormat(0)
        if item == 'nextSkillXPLeft':
            if not self.__isNewSkillReady(tankman):
                return self.__getSkillNextLevelCost(tankman)
            else:
                return BigWorld.wg_getIntegralFormat(0)
        elif item == 'nextSkillBattlesLeft':
            if dossier['battlesCount'] != 0 and extDossier['xp'] != 0 and extDossier['battlesCount'] != 0:
                if not self.__isNewSkillReady(tankman):
                    return BigWorld.wg_getIntegralFormat(round(self.__getSkillNextLevelCost(tankman) / round(float(extDossier['xp']) / extDossier['battlesCount']) + 1))
                else:
                    return BigWorld.wg_getIntegralFormat(0)
            else:
                return ''
        return BigWorld.wg_getNiceNumberFormat(dossier[item])

    def __getExtra(self, block, item, dossier, extDossier, tankman):
        extra = ''
        if block == 'common':
            if item != 'battlesCount' and dossier['battlesCount'] != 0:
                extra = '(%d%%)' % round(float(dossier[item]) / dossier['battlesCount'] * 100)
        elif item == 'nextSkillXPLeft':
            if tankman is not None:
                if not self.__isNewSkillReady(tankman):
                    extra = '(' + makeString('#item_types:tankman/skills/main' if len(tankman.skills) == 0 or tankman.roleLevel != MAX_SKILL_LEVEL else convert(getSkillsConfig()[tankman.skills[len(tankman.skills) - 1]]['userString'])) + ')'
                else:
                    extra = '(' + makeString('#menu:profile/stats/items/ready') + ')'
        elif item == 'nextSkillBattlesLeft':
            if dossier['battlesCount'] == 0 or extDossier['xp'] == 0:
                extra = '(' + makeString('#menu:profile/stats/items/unknown') + ')'
        return extra

    @process
    def onGetTankmanStats(self, callbackID, tankmanID):
        Waiting.show('updating')
        dossier = yield StatsRequester().getTankmanDossier(tankmanID)
        tankmen = yield Requester('tankman').getFromInventory()
        tankman = None
        for t in tankmen:
            if t.inventoryId == tankmanID:
                tankman = t

        vcl = yield tankman.currentVehicle
        if vcl is not None:
            extDossier = yield StatsRequester().getVehicleDossier(vcl.descriptor.type.compactDescr)
        else:
            extDossier = yield StatsRequester().getAccountDossier()
        stats = [len(self.STATS_BLOCKS['tankman'])]
        for block in self.STATS_BLOCKS['tankman']:
            stats.append(block[0])
            stats.append(len(block[1]))
            for item in block[1]:
                stats.append(item)
                stats.append(self.__getData(item, dossier, extDossier, tankman))
                stats.append(self.__getExtra(block[0], item, dossier, extDossier, tankman))

        achievs = getDossierMedals(dossier, DOSSIER_TYPE.TANKMAN)
        self.call('tankmen.setStats', stats)
        self.call('tankmen.setAchievements', achievs)
        Waiting.hide('updating')
        return

    @process
    def __replaceTankman(self, tankman, firstnameID=None, lastnameID=None, iconID=None, isFemale=None):
        success, message = yield tankman.replacePassport(firstnameID, lastnameID, iconID, isFemale)
        SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.FinancialTransactionWithGold if success else SystemMessages.SM_TYPE.Error)
        self.call('tankmen.replacePassportComplete', [])
        self.__updateCreator()
        Waiting.hide('replacePassport')

    def onReplaceTankman(self, callbackID, tankmanCompact, firstnameID, lastnameID, iconID, isFemale):
        Waiting.show('replacePassport')
        tankman = getItemByCompact(tankmanCompact)
        self.__replaceTankman(tankman, int(firstnameID) if firstnameID is not None else firstnameID, int(lastnameID) if lastnameID is not None else lastnameID, int(iconID) if iconID is not None else iconID, isFemale)
        return

    def onGetTankmanDocs(self, callbackID, tankmanCompact):
        tankman = getItemByCompact(tankmanCompact)
        self.__getTankmanDocs(tankman)

    @process
    def __getTankmanDocs(self, tankman):
        Waiting.show('updating')
        passportCost = yield StatsRequester().getPassportChangeCost()
        gold = yield StatsRequester().getGold()
        data = [passportCost, gold]

        def isNormalGroup(group, id):
            for i in range(len(tankman.nationConfig['normalGroups'])):
                if id in tankman.nationConfig['normalGroups'][i][group]:
                    return True

            return False

        data.append(0)
        number_index = len(data) - 1
        for id in tankman.nationConfig['firstNames'].keys():
            if isNormalGroup('firstNames', id):
                data.append(id)
                data.append(tankman.nationConfig['firstNames'][id])
                data[number_index] += 1

        data.append(0)
        number_index = len(data) - 1
        for id in tankman.nationConfig['lastNames'].keys():
            if isNormalGroup('lastNames', id):
                data.append(id)
                data.append(tankman.nationConfig['lastNames'][id])
                data[number_index] += 1

        data.append(0)
        number_index = len(data) - 1
        for id in tankman.nationConfig['icons'].keys():
            if isNormalGroup('icons', id):
                data.append(id)
                data.append(tankman.nationConfig['icons'][id])
                data[number_index] += 1

        self.call('tankmen.populateTankmanDocs', data)
        self.__updateCreator()
        Waiting.hide('updating')

    def onAddSkill(self, callbackID, tankmanCompact, skillname):
        tankman = getItemByCompact(tankmanCompact)
        self.__addSkill(tankman, skillname)

    @process
    def __addSkill(self, tankman, skillname):
        Waiting.show('studying')
        success, message = yield tankman.addSkill(skillname)
        SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Information if success else SystemMessages.SM_TYPE.Error)
        self.call('tankmen.addSkillComplete', [])
        self.__updateCreator()
        Waiting.hide('studying')

    def onDropSkill(self, callbackID, tankmanCompact, skillname):
        tankman = getItemByCompact(tankmanCompact)
        tmanDescr = tankmen.TankmanDescr(tankman.compactDescr)
        tmanDescr.dropSkill(skillname)
        skillsStr = ''
        for skill in tmanDescr.skills:
            skillLevel = tmanDescr.lastSkillLevel if tmanDescr.skills.index(skill) == len(tmanDescr.skills) - 1 else 100
            skillsStr += ', %s %d' % (getSkillsConfig()[skill]['userString'], skillLevel)

        self.call('common.showMessageDialog', ['skillDropWindow',
         True,
         True,
         makeString('#dialogs:skillDropWindow/message') % getSkillsConfig()[skillname]['userString'],
         'tankmemInterface.dropSkill',
         tankmanCompact,
         skillname])

    def dropSkill(self, cid, tankmanCompact, skillname):
        tankman = getItemByCompact(tankmanCompact)
        self.__dropSkill(tankman, skillname)

    @process
    def __dropSkill(self, tankman, skillname):
        Waiting.show('deleting')
        success, message = yield tankman.dropSkill(skillname)
        SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Information if success else SystemMessages.SM_TYPE.Error)
        self.call('tankmen.dropSkillComplete', [])
        self.__updateCreator()
        Waiting.hide('deleting')

    def onUpdateSkillsList(self, callbackID, tankmanCompact):
        tankman = getItemByCompact(tankmanCompact)
        self.__updateSkillsList(tankman)

    def __updateSkillsList(self, tankman):
        Waiting.show('updating')
        data = [makeString('#dialogs:addSkillWindow/label') % makeString('#dialogs:addSkillWindow/label/' + tankman.descriptor.role)]
        new_skill = len(tankman.skills) == 0 and tankman.roleLevel == 100 or tankman.lastSkillLevel == 100
        for skill in SKILL_NAMES:
            if skill in SKILLS_BY_ROLES[tankman.descriptor.role] and skill not in tankman.skills:
                data.append(skill)
                data.append(getSkillsConfig()[skill]['userString'])
                data.append(getSkillsConfig()[skill]['description'])
                data.append(makeTooltip(getSkillsConfig()[skill]['userString'], None, makeString('#tooltips:personal_case/skills_list/item/note') if new_skill else None))

        self.call('tankmen.setSkillsList', data)
        Waiting.hide('updating')
        return

    @process
    def updateVehicleClassDropdown(self, callbackID, nationID):
        Waiting.show('updating')
        unlocks = yield StatsRequester().getUnlocks()
        modulesAll = yield Requester('vehicle').getFromShop()
        data = []
        modulesAll.sort()
        for module in modulesAll:
            compdecs = module.descriptor.type.compactDescr
            if compdecs in unlocks and module.descriptor.type.id[0] == nationID and module.type not in data:
                data.append(module.type)

        self.call('tankmen.setVehicleClassDropdown', data)
        Waiting.hide('updating')

    @process
    def updateVehicleTypeDropdown(self, callbackID, nationID, vclass):
        Waiting.show('updating')
        unlocks = yield StatsRequester().getUnlocks()
        modulesAll = yield Requester('vehicle').getFromShop()
        data = []
        modulesAll.sort()
        for module in modulesAll:
            compdecs = module.descriptor.type.compactDescr
            if compdecs in unlocks and module.descriptor.type.id[0] == nationID and module.type == vclass:
                data.append(module.descriptor.type.id[1])
                data.append(module.descriptor.type.shortUserString)

        self.call('tankmen.setVehicleTypeDropdown', data)
        Waiting.hide('updating')

    @process
    def updateRoleDropdown(self, callbackID, nationID, vclass, typeID):
        Waiting.show('updating')
        unlocks = yield StatsRequester().getUnlocks()
        modulesAll = yield Requester('vehicle').getFromShop()
        data = []
        modulesAll.sort()
        for module in modulesAll:
            compdecs = module.descriptor.type.compactDescr
            if compdecs in unlocks and module.descriptor.type.id[0] == nationID and module.descriptor.type.id[1] == typeID:
                for role in module.descriptor.type.crewRoles:
                    if role[0] not in data:
                        data.append(role[0])
                        data.append(convert(getSkillsConfig()[role[0]]['userString']))

        self.call('tankmen.setRoleDropdown', data)
        Waiting.hide('updating')

    @process
    def onGetPersonalCase(self, callbackID, tankmanID):
        tankmen = yield Requester('tankman').getFromInventory()
        tankman = None
        for tman in tankmen:
            if tman.inventoryId == tankmanID:
                tankman = tman

        if tankman is None:
            return
        else:
            curVcl = yield tankman.currentVehicle
            data = []
            data.append(tankman.firstname)
            data.append(tankman.lastname)
            data.append(tankman.rank)
            data.append(tankman.roleLevel)
            data.append(tankman.role)
            data.append(tankman.vehicle.type.shortUserString)
            data.append(tankman.icon)
            data.append(tankman.iconRank)
            data.append(tankman.iconRole)
            data.append(tankman.vehicleIconContour)
            data.append(tankman.inventoryId)
            data.append(tankman.nation)
            data.append(tankman.vehicle.type.id[1])
            data.append(tankman.isInTank)
            data.append(tankman.descriptor.role)
            data.append(tankman.vehicleType)
            data.append(tankman.lastSkillLevel)
            data.append(tankman.descriptor.firstNameID)
            data.append(tankman.descriptor.lastNameID)
            data.append(tankman.descriptor.iconID)
            data.append(tankman.pack())
            if tankman.isInTank:
                data.append(curVcl.descriptor.type.userString)
                data.append(curVcl.descriptor.type.id[1])
            else:
                data.append('')
                data.append(-1)
            isLocked, msg = TankmenInterface.getTankmanLockMessage(curVcl) if tankman.isInTank else (False, '')
            data.append(isLocked)
            data.append(msg)
            data.append(curVcl.repairCost > 0 if tankman.isInTank else False)
            data.append(makeString('#dialogs:addSkillWindow/label') % makeString('#dialogs:addSkillWindow/label/' + tankman.descriptor.role))
            skills_count = 0
            for skill in SKILL_NAMES:
                if skill in SKILLS_BY_ROLES[tankman.descriptor.role]:
                    skills_count += 1

            data.append(skills_count)
            data.append(len(tankman.skills))
            for skill in tankman.skills:
                skillLevel = tankman.lastSkillLevel if tankman.skills.index(skill) == len(tankman.skills) - 1 else 100
                data.append(skill)
                data.append(getSkillsConfig()[skill]['userString'])
                data.append(getSkillsConfig()[skill]['description'])
                data.append(getSkillsConfig()[skill]['icon'])
                data.append(skill not in PERKS or skillLevel == 100)
                data.append(makeTooltip(getSkillsConfig()[skill]['userString'], getSkillsConfig()[skill]['description'], makeString('#tooltips:personal_case/skills/skill/note')))

            self.call('tankmen.populatePersonalCase', data)
            return

    @staticmethod
    def getTankmanLockMessage(invVehicle):
        if invVehicle.lock == LOCK_REASON.ON_ARENA:
            return (True, makeString('#menu:tankmen/lockReason/inbattle'))
        if invVehicle.repairCost > 0:
            return (False, makeString('#menu:tankmen/lockReason/broken'))
        if AccountPrebattle.isSquad() and AccountPrebattle.isMemberReady() and invVehicle.isCurrent:
            return (True, makeString('#menu:tankmen/lockReason/prebattle'))
        return (False, '')

    def onShowRecruitWindow(self, callbackID):
        self.__showRecruitWindow()

    @process
    def __showRecruitWindow(self):
        Waiting.show('updating')
        credits = yield StatsRequester().getCredits()
        gold = yield StatsRequester().getGold()
        upgradeParams = yield StatsRequester().getTankmanCost()
        data = [credits,
         gold,
         round(upgradeParams[1]['credits']),
         round(upgradeParams[2]['gold'])]
        self.call('tankmen.showRecruit', data)
        Waiting.hide('updating')

    def onPopulateRetrainingWindow(self, callbackID, tankmanCompact):
        tankman = getItemByCompact(tankmanCompact)
        if tankman is not None:
            self.__populateRetrainingWindow(tankman)
        return

    @process
    def __populateRetrainingWindow(self, tankman):
        Waiting.show('updating')
        tManCost = yield StatsRequester().getTankmanCost()
        if tManCost:
            unlockedVehicleCDs = yield StatsRequester().getUnlocks()
            vehicleShopItems = yield Requester('vehicle').getFromShop()
            gold = yield StatsRequester().getGold()
            credits = yield StatsRequester().getCredits()
            data = [-1,
             -1,
             -1,
             -1]
            vehicle = tankman.vehicle
            _, inNationId = vehicle.type.id
            data.extend((inNationId, tankman.vehicleType, vehicle.type.shortUserString))
            vehicleShopItems.sort()
            for vehicle in vehicleShopItems:
                vehicleCD = vehicle.descriptor.type.compactDescr
                if isVehicleObserver(vehicleCD):
                    continue
                for roles in vehicle.descriptor.type.crewRoles:
                    if tankman.descriptor.role == roles[0]:
                        nationId, inNationId = vehicle.descriptor.type.id
                        if vehicleCD in unlockedVehicleCDs and nationId == tankman.nation and inNationId not in data:
                            data.append(inNationId)
                            data.append(vehicle.type)
                            data.append(vehicle.descriptor.type.shortUserString)

            data[:4] = (tManCost[2]['gold'],
             tManCost[1]['credits'],
             gold,
             credits)
            self.call('tankmen.populateRetrainingWindow', data)
        Waiting.hide('updating')
