# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/balance.py
import BigWorld
import sys
from block import Meta, Block, InitParam, buildStrKeysValue, EDITOR_TYPE
from slot_types import SLOT_TYPE, arrayOf
from type import VScriptStruct, VScriptStructField
from visual_script.misc import errorVScript, ASPECT
import ResMgr
import constants
import nations
_IS_VSE_EDITOR = sys.executable.endswith('vscript_editor.exe') or sys.executable.endswith('vscript_validator.exe')
constants.IS_EDITOR = constants.IS_EDITOR and not _IS_VSE_EDITOR
import items.vehicles as iv
_dataSection = None
_gList = None

class VsePaths(object):

    def __enter__(self):
        if _IS_VSE_EDITOR:
            self.prevArenaPath = constants.ARENA_TYPE_XML_PATH
            self.prevItemDefPath = constants.ITEM_DEFS_PATH
            self.prevTypeXMLType = iv._VEHICLE_TYPE_XML_PATH
            constants.ARENA_TYPE_XML_PATH = '../../../res/wot/scripts/arena_defs/'
            constants.ITEM_DEFS_PATH = '../../../res/wot/scripts/item_defs/'
            iv._VEHICLE_TYPE_XML_PATH = constants.ITEM_DEFS_PATH + 'vehicles/'

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _IS_VSE_EDITOR:
            constants.ARENA_TYPE_XML_PATH = self.prevArenaPath
            constants.ITEM_DEFS_PATH = self.prevItemDefPath
            iv._VEHICLE_TYPE_XML_PATH = self.prevTypeXMLType


def cache():
    if not iv.g_cache:
        with VsePaths():
            from items import init
            init(False, None)
            from items.vehicles import init
            init(False, None)
    return iv.g_cache


def getVehicleList(naton):
    if not iv.g_list:
        cache()
    return iv.g_list(naton)


def eqDataSection(eqName):
    global _dataSection
    if not _dataSection:
        if constants.IS_CELLAPP or constants.IS_CLIENT:
            xmlPath = constants.ITEM_DEFS_PATH
        else:
            xmlPath = '../../../res/wot/scripts/item_defs/'
        xmlPath += 'vehicles/common/equipments.xml'
        _dataSection = ResMgr.openSection(xmlPath)
    ds = ResMgr.DataSection(eqName)
    ds.copy(_dataSection[eqName])
    return ds


def getArtefact(name):
    return cache().equipments()[cache().equipmentIDs()[name]]


class EquipmentMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.SERVER, ASPECT.CLIENT, ASPECT.HANGAR]


class ConfigParamStruct(VScriptStruct):
    name = VScriptStructField('name', SLOT_TYPE.STR)
    value = VScriptStructField('value', SLOT_TYPE.STR)

    def __repr__(self):
        return 'ConfigParam(name = {}, value = {})'.format(self.name, self.value)


class ReloadClientPlan(Block, EquipmentMeta):

    def __init__(self, *args, **kwargs):
        super(ReloadClientPlan, self).__init__(*args, **kwargs)
        self._inSlot = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        if constants.IS_CELLAPP:

            def reloader(*args):
                for avatar in BigWorld.entities.valuesOfType('Avatar', 0):
                    if avatar.isClientConnected:
                        self._writeLog('send reload to client {}'.format(avatar.id))
                        avatar.ownClient.showDevelopmentInfo(100, '')

            BigWorld.addTimer(reloader, 1.0)
        self._out.call()


class ResMgrSpy(object):

    def __init__(self, block, params):
        self.spyParams = params
        self.__spyParamsPaths = []
        self.__block = block
        import sys
        sys.settrace(None)
        sys.settrace(self.traceCalls)
        return

    def stop(self):
        import sys
        sys.settrace(None)
        return

    def traceCalls(self, frame, event, arg):
        self.__traceCalls(frame, event)
        return self.traceCalls

    def __traceCalls(self, frame, event):
        if event != 'call':
            return
        co = frame.f_code
        if not co.co_name.startswith('read'):
            return
        l = frame.f_locals
        if 'section' not in l or 'subsectionName' not in l:
            return
        attr = self.__path(l['section']) + l['subsectionName']
        self.spyParams.discard(attr)

    def __path(self, section):
        if section.name == 'script':
            return ''
        parent = section.parentSection()
        return '' if not parent else self.__path(parent) + section.name + '/'


class IntCompDescrDecoder(Block, EquipmentMeta):

    def __init__(self, *args, **kwargs):
        super(IntCompDescrDecoder, self).__init__(*args, **kwargs)
        self._intCDs = self._makeDataInputSlot('incCD', arrayOf(SLOT_TYPE.INT))

    def captionText(self):
        pass

    def __parseCDs(self):
        cache()
        from items import vehicles, ITEM_TYPE_NAMES
        err = ''
        results = []
        for intCD in self._intCDs.getValue():
            try:
                itemTypeID, nationID, vehID = vehicles.parseIntCompactDescr(intCD)
                item = vehicles.getItemByCompactDescr(intCD)
            except Exception as e:
                err += '{}: {}\n'.format(intCD, e)
                results.append(err)
                continue

            results.append('{} {} {}\n'.format(intCD, (nations.NAMES[nationID], ITEM_TYPE_NAMES[itemTypeID], vehID), item.name))

        return (results, err)

    def _execute(self):
        pass

    def validate(self):
        results, err = self.__parseCDs()
        for res in results:
            self._writeLog(res)

        return err


class EquipmentParams(Block, EquipmentMeta):

    def __init__(self, *args, **kwargs):
        super(EquipmentParams, self).__init__(*args, **kwargs)
        self.eqName = self._getInitParams()
        self._inSlot = self._makeEventInputSlot('in', self._execute)
        self._params = self._makeDataInputSlot('Parameters', arrayOf('ConfigParamStruct'))
        self._out = self._makeEventOutputSlot('out')

    def captionText(self):
        return self.eqName

    @classmethod
    def initParams(cls):
        return [InitParam('EquipmentName', SLOT_TYPE.STR, buildStrKeysValue('large_repairkit_battle_royale', 'regenerationKit', 'arcade_minefield_battle_royale', 'healPoint', 'selfBuff', 'trappoint', 'afterburning_battle_royale', 'repairpoint', 'arcade_bomber_battle_royale', 'spawn_kamikaze', 'arcade_smoke_battle_royale_with_damage', 'berserker', 'fireCircle', 'adaptationHealthRestore', 'corrodingShot', 'clingBrander', 'thunderStrike', 'shotPassion'), EDITOR_TYPE.STR_KEY_SELECTOR)]

    def _execute(self):
        self._writeLog('_execute {}'.format(self._params.getValue()))
        errString = self._processParams()
        if errString:
            return errorVScript(self, errString)
        else:
            if constants.IS_CELLAPP:
                from items.vehicles import g_cache
                import InfluenceZone
                eqExtra = g_cache.commonConfig['extrasDict'].get(self.eqName)
                if eqExtra:
                    eqExtra._readConfig(None, None)
            self._out.call()
            return

    def validate(self):
        return self._processParams()

    def _processParams(self):
        if not self._params.getValue():
            return ''
        else:
            import sys
            self._writeLog('_processParams {}'.format((self._params.getValue(), sys.executable)))
            spy = None
            try:
                try:
                    equipment = getArtefact(self.eqName)
                    equipmentSection = eqDataSection(self.eqName)
                    section = equipmentSection['script']
                    for param in self._params.getValue():
                        if not param.name:
                            continue
                        section.writeString(param.name, param.value)

                    if _IS_VSE_EDITOR:
                        spy = ResMgrSpy(self, {param.name for param in self._params.getValue()})
                    equipment.init(None, equipmentSection)
                except Exception as e:
                    return 'error {}'.format(e)

            finally:
                if spy:
                    spy.stop()

            return 'Were not read {}'.format(spy.spyParams) if spy and spy.spyParams else ''
