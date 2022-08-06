# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serialization/component_xml_deserializer.py
from typing import Tuple, Any
import ResMgr
from constants import IS_EDITOR
from items import decodeEnum
from items.components.c11n_constants import ApplyArea, Options
from items.utils import getEditorOnlySection
from serialization.definitions import FieldFlags, FieldTypes
from serialization.exceptions import SerializationException
from serialization.serializable_component import SerializableComponent
__all__ = ('ComponentXmlDeserializer',)

class ComponentXmlDeserializer(object):
    __slots__ = ('customTypes',)

    def __init__(self, customTypes):
        self.customTypes = customTypes
        super(ComponentXmlDeserializer, self).__init__()

    def decode(self, itemType, xmlCtx, section):
        obj = self.__decodeCustomType(itemType, xmlCtx, section)
        return obj

    def __decodeCustomType--- This code section failed: ---

  32       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'customTypes'
           6	LOAD_FAST         'customType'
           9	BINARY_SUBSCR     ''
          10	STORE_FAST        'cls'

  33      13	LOAD_FAST         'cls'
          16	CALL_FUNCTION_0   ''
          19	STORE_FAST        'instance'

  34      22	SETUP_LOOP        '644'
          25	LOAD_FAST         'cls'
          28	LOAD_ATTR         'fields'
          31	LOAD_ATTR         'iteritems'
          34	CALL_FUNCTION_0   ''
          37	GET_ITER          ''
          38	FOR_ITER          '643'
          41	UNPACK_SEQUENCE_2 ''
          44	STORE_FAST        'fname'
          47	STORE_FAST        'finfo'

  35      50	LOAD_FAST         'finfo'
          53	LOAD_ATTR         'flags'
          56	LOAD_GLOBAL       'FieldFlags'
          59	LOAD_ATTR         'NON_XML'
          62	BINARY_AND        ''
          63	POP_JUMP_IF_FALSE '72'

  36      66	CONTINUE          '38'
          69	JUMP_FORWARD      '72'
        72_0	COME_FROM         '69'

  38      72	LOAD_FAST         'section'
          75	LOAD_ATTR         'has_key'
          78	LOAD_FAST         'fname'
          81	CALL_FUNCTION_1   ''
          84	POP_JUMP_IF_TRUE  '175'

  39      87	LOAD_GLOBAL       'IS_EDITOR'
          90	POP_JUMP_IF_FALSE '38'
          93	LOAD_FAST         'finfo'
          96	LOAD_ATTR         'flags'
          99	LOAD_GLOBAL       'FieldFlags'
         102	LOAD_ATTR         'SAVE_AS_EDITOR_ONLY'
         105	BINARY_AND        ''
       106_0	COME_FROM         '90'
         106	POP_JUMP_IF_FALSE '38'

  40     109	LOAD_GLOBAL       'getEditorOnlySection'
         112	LOAD_FAST         'section'
         115	CALL_FUNCTION_1   ''
         118	STORE_FAST        'editorOnlySection'

  41     121	LOAD_FAST         'editorOnlySection'
         124	LOAD_CONST        ''
         127	COMPARE_OP        'is not'
         130	POP_JUMP_IF_FALSE '38'

  42     133	LOAD_FAST         'editorOnlySection'
         136	LOAD_ATTR         'has_key'
         139	LOAD_FAST         'fname'
         142	CALL_FUNCTION_1   ''
       145_0	COME_FROM         '130'
         145	POP_JUMP_IF_FALSE '38'

  43     148	LOAD_FAST         'editorOnlySection'
         151	STORE_FAST        'section'
         154	JUMP_ABSOLUTE     '166'

  45     157	CONTINUE          '38'
         160	JUMP_ABSOLUTE     '172'

  47     163	CONTINUE          '38'
         166	JUMP_ABSOLUTE     '175'

  49     169	CONTINUE          '38'
         172	JUMP_FORWARD      '175'
       175_0	COME_FROM         '172'

  51     175	LOAD_FAST         'finfo'
         178	LOAD_ATTR         'type'
         181	STORE_FAST        'ftype'

  52     184	LOAD_FAST         'ftype'
         187	LOAD_GLOBAL       'FieldTypes'
         190	LOAD_ATTR         'VARINT'
         193	COMPARE_OP        '=='
         196	POP_JUMP_IF_FALSE '217'

  53     199	LOAD_FAST         'section'
         202	LOAD_ATTR         'readInt'
         205	LOAD_FAST         'fname'
         208	CALL_FUNCTION_1   ''
         211	STORE_FAST        'value'
         214	JUMP_FORWARD      '552'

  54     217	LOAD_FAST         'ftype'
         220	LOAD_GLOBAL       'FieldTypes'
         223	LOAD_ATTR         'FLOAT'
         226	COMPARE_OP        '=='
         229	POP_JUMP_IF_FALSE '250'

  55     232	LOAD_FAST         'section'
         235	LOAD_ATTR         'readFloat'
         238	LOAD_FAST         'fname'
         241	CALL_FUNCTION_1   ''
         244	STORE_FAST        'value'
         247	JUMP_FORWARD      '552'

  56     250	LOAD_FAST         'ftype'
         253	LOAD_GLOBAL       'FieldTypes'
         256	LOAD_ATTR         'APPLY_AREA_ENUM'
         259	COMPARE_OP        '=='
         262	POP_JUMP_IF_FALSE '295'

  57     265	LOAD_FAST         'self'
         268	LOAD_ATTR         '__decodeEnum'
         271	LOAD_FAST         'section'
         274	LOAD_ATTR         'readString'
         277	LOAD_FAST         'fname'
         280	CALL_FUNCTION_1   ''
         283	LOAD_GLOBAL       'ApplyArea'
         286	CALL_FUNCTION_2   ''
         289	STORE_FAST        'value'
         292	JUMP_FORWARD      '552'

  58     295	LOAD_FAST         'ftype'
         298	LOAD_GLOBAL       'FieldTypes'
         301	LOAD_ATTR         'TAGS'
         304	COMPARE_OP        '=='
         307	POP_JUMP_IF_FALSE '340'

  59     310	LOAD_GLOBAL       'tuple'
         313	LOAD_FAST         'section'
         316	LOAD_ATTR         'readString'
         319	LOAD_FAST         'fname'
         322	CALL_FUNCTION_1   ''
         325	LOAD_ATTR         'split'
         328	CALL_FUNCTION_0   ''
         331	CALL_FUNCTION_1   ''
         334	STORE_FAST        'value'
         337	JUMP_FORWARD      '552'

  60     340	LOAD_FAST         'ftype'
         343	LOAD_GLOBAL       'FieldTypes'
         346	LOAD_ATTR         'STRING'
         349	COMPARE_OP        '=='
         352	POP_JUMP_IF_FALSE '373'

  61     355	LOAD_FAST         'section'
         358	LOAD_ATTR         'readString'
         361	LOAD_FAST         'fname'
         364	CALL_FUNCTION_1   ''
         367	STORE_FAST        'value'
         370	JUMP_FORWARD      '552'

  62     373	LOAD_FAST         'ftype'
         376	LOAD_GLOBAL       'FieldTypes'
         379	LOAD_ATTR         'OPTIONS_ENUM'
         382	COMPARE_OP        '=='
         385	POP_JUMP_IF_FALSE '418'

  63     388	LOAD_FAST         'self'
         391	LOAD_ATTR         '__decodeEnum'
         394	LOAD_FAST         'section'
         397	LOAD_ATTR         'readString'
         400	LOAD_FAST         'fname'
         403	CALL_FUNCTION_1   ''
         406	LOAD_GLOBAL       'Options'
         409	CALL_FUNCTION_2   ''
         412	STORE_FAST        'value'
         415	JUMP_FORWARD      '552'

  64     418	LOAD_FAST         'ftype'
         421	LOAD_GLOBAL       'FieldTypes'
         424	LOAD_ATTR         'TYPED_ARRAY'
         427	BINARY_AND        ''
         428	POP_JUMP_IF_FALSE '478'

  65     431	LOAD_FAST         'ftype'
         434	LOAD_GLOBAL       'FieldTypes'
         437	LOAD_ATTR         'TYPED_ARRAY'
         440	BINARY_XOR        ''
         441	STORE_FAST        'itemType'

  66     444	LOAD_FAST         'self'
         447	LOAD_ATTR         '__decodeArray'
         450	LOAD_FAST         'itemType'
         453	LOAD_FAST         'ctx'
         456	LOAD_FAST         'fname'
         459	BUILD_TUPLE_2     ''
         462	LOAD_FAST         'section'
         465	LOAD_FAST         'fname'
         468	BINARY_SUBSCR     ''
         469	CALL_FUNCTION_3   ''
         472	STORE_FAST        'value'
         475	JUMP_FORWARD      '552'

  67     478	LOAD_FAST         'ftype'
         481	LOAD_GLOBAL       'FieldTypes'
         484	LOAD_ATTR         'CUSTOM_TYPE_OFFSET'
         487	COMPARE_OP        '>='
         490	POP_JUMP_IF_FALSE '540'

  68     493	LOAD_FAST         'ftype'
         496	LOAD_GLOBAL       'FieldTypes'
         499	LOAD_ATTR         'CUSTOM_TYPE_OFFSET'
         502	BINARY_DIVIDE     ''
         503	STORE_FAST        'ftype'

  69     506	LOAD_FAST         'self'
         509	LOAD_ATTR         '__decodeCustomType'
         512	LOAD_FAST         'ftype'
         515	LOAD_FAST         'ctx'
         518	LOAD_FAST         'fname'
         521	BUILD_TUPLE_2     ''
         524	LOAD_FAST         'section'
         527	LOAD_FAST         'fname'
         530	BINARY_SUBSCR     ''
         531	CALL_FUNCTION_3   ''
         534	STORE_FAST        'value'
         537	JUMP_FORWARD      '552'

  71     540	LOAD_GLOBAL       'SerializationException'
         543	LOAD_CONST        'Unsupported item type'
         546	CALL_FUNCTION_1   ''
         549	RAISE_VARARGS_1   ''
       552_0	COME_FROM         '214'
       552_1	COME_FROM         '247'
       552_2	COME_FROM         '292'
       552_3	COME_FROM         '337'
       552_4	COME_FROM         '370'
       552_5	COME_FROM         '415'
       552_6	COME_FROM         '475'
       552_7	COME_FROM         '537'

  72     552	LOAD_FAST         'finfo'
         555	LOAD_ATTR         'flags'
         558	LOAD_GLOBAL       'FieldFlags'
         561	LOAD_ATTR         'DEPRECATED'
         564	BINARY_AND        ''
         565	UNARY_NOT         ''
         566	POP_JUMP_IF_TRUE  '584'
         569	LOAD_GLOBAL       'hasattr'
         572	LOAD_FAST         'instance'
         575	LOAD_FAST         'fname'
         578	CALL_FUNCTION_2   ''
       581_0	COME_FROM         '566'
         581	POP_JUMP_IF_FALSE '603'

  73     584	LOAD_GLOBAL       'setattr'
         587	LOAD_FAST         'instance'
         590	LOAD_FAST         'fname'
         593	LOAD_FAST         'value'
         596	CALL_FUNCTION_3   ''
         599	POP_TOP           ''
         600	JUMP_FORWARD      '603'
       603_0	COME_FROM         '600'

  75     603	LOAD_GLOBAL       'IS_EDITOR'
         606	POP_JUMP_IF_FALSE '38'
         609	LOAD_FAST         'finfo'
         612	LOAD_ATTR         'flags'
         615	LOAD_GLOBAL       'FieldFlags'
         618	LOAD_ATTR         'SAVE_AS_EDITOR_ONLY'
         621	BINARY_AND        ''
       622_0	COME_FROM         '606'
         622	POP_JUMP_IF_FALSE '38'

  76     625	LOAD_FAST         'section'
         628	LOAD_ATTR         'parentSection'
         631	CALL_FUNCTION_0   ''
         634	STORE_FAST        'section'
         637	JUMP_BACK         '38'
         640	JUMP_BACK         '38'
         643	POP_BLOCK         ''
       644_0	COME_FROM         '22'

  77     644	LOAD_FAST         'instance'
         647	RETURN_VALUE      ''

Syntax error at or near 'CONTINUE' token at offset 169

    def __decodeArray(self, itemType, ctx, section):
        result = []
        for i, (iname, isection) in enumerate(section.items()):
            if itemType == FieldTypes.VARINT:
                result.append(isection.asInt)
            if itemType == FieldTypes.FLOAT:
                result.append(isection.asFloat)
            if itemType >= FieldTypes.CUSTOM_TYPE_OFFSET:
                customType = itemType / FieldTypes.CUSTOM_TYPE_OFFSET
                ictx = (ctx, '{0} {1}'.format(iname, isection))
                result.append(self.__decodeCustomType(customType, ictx, isection))
            raise SerializationException('Unsupported item type')

        return result

    def __decodeEnum(self, value, enum):
        return decodeEnum(value, enum)[0]