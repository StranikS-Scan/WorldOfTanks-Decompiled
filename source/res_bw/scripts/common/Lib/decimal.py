# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/decimal.py
# Compiled at: 2010-05-25 20:46:16

--- This code section failed: ---

 116       0	LOAD_CONST        '\nThis is a Py2.3 implementation of decimal floating point arithmetic based on\nthe General Decimal Arithmetic Specification:\n\n    www2.hursley.ibm.com/decimal/decarith.html\n\nand IEEE standard 854-1987:\n\n    www.cs.berkeley.edu/~ejr/projects/754/private/drafts/854-1987/dir.html\n\nDecimal floating point has finite precision with arbitrarily large bounds.\n\nThe purpose of this module is to support arithmetic using familiar\n"schoolhouse" rules and to avoid some of the tricky representation\nissues associated with binary floating point.  The package is especially\nuseful for financial applications or for contexts where users have\nexpectations that are at odds with binary floating point (for instance,\nin binary floating point, 1.00 % 0.1 gives 0.09999999999999995 instead\nof the expected Decimal(\'0.00\') returned by decimal floating point).\n\nHere are some examples of using the decimal module:\n\n>>> from decimal import *\n>>> setcontext(ExtendedContext)\n>>> Decimal(0)\nDecimal(\'0\')\n>>> Decimal(\'1\')\nDecimal(\'1\')\n>>> Decimal(\'-.0123\')\nDecimal(\'-0.0123\')\n>>> Decimal(123456)\nDecimal(\'123456\')\n>>> Decimal(\'123.45e12345678901234567890\')\nDecimal(\'1.2345E+12345678901234567892\')\n>>> Decimal(\'1.33\') + Decimal(\'1.27\')\nDecimal(\'2.60\')\n>>> Decimal(\'12.34\') + Decimal(\'3.87\') - Decimal(\'18.41\')\nDecimal(\'-2.20\')\n>>> dig = Decimal(1)\n>>> print dig / Decimal(3)\n0.333333333\n>>> getcontext().prec = 18\n>>> print dig / Decimal(3)\n0.333333333333333333\n>>> print dig.sqrt()\n1\n>>> print Decimal(3).sqrt()\n1.73205080756887729\n>>> print Decimal(3) ** 123\n4.85192780976896427E+58\n>>> inf = Decimal(1) / Decimal(0)\n>>> print inf\nInfinity\n>>> neginf = Decimal(-1) / Decimal(0)\n>>> print neginf\n-Infinity\n>>> print neginf + inf\nNaN\n>>> print neginf * inf\n-Infinity\n>>> print dig / 0\nInfinity\n>>> getcontext().traps[DivisionByZero] = 1\n>>> print dig / 0\nTraceback (most recent call last):\n  ...\n  ...\n  ...\nDivisionByZero: x / 0\n>>> c = Context()\n>>> c.traps[InvalidOperation] = 0\n>>> print c.flags[InvalidOperation]\n0\n>>> c.divide(Decimal(0), Decimal(0))\nDecimal(\'NaN\')\n>>> c.traps[InvalidOperation] = 1\n>>> print c.flags[InvalidOperation]\n1\n>>> c.flags[InvalidOperation] = 0\n>>> print c.flags[InvalidOperation]\n0\n>>> print c.divide(Decimal(0), Decimal(0))\nTraceback (most recent call last):\n  ...\n  ...\n  ...\nInvalidOperation: 0 / 0\n>>> print c.flags[InvalidOperation]\n1\n>>> c.flags[InvalidOperation] = 0\n>>> c.traps[InvalidOperation] = 0\n>>> print c.divide(Decimal(0), Decimal(0))\nNaN\n>>> print c.flags[InvalidOperation]\n1\n>>>\n'
           3	STORE_NAME        '__doc__'

 120       6	LOAD_CONST        'Decimal'
           9	LOAD_CONST        'Context'

 123      12	LOAD_CONST        'DefaultContext'
          15	LOAD_CONST        'BasicContext'
          18	LOAD_CONST        'ExtendedContext'

 126      21	LOAD_CONST        'DecimalException'
          24	LOAD_CONST        'Clamped'
          27	LOAD_CONST        'InvalidOperation'
          30	LOAD_CONST        'DivisionByZero'

 127      33	LOAD_CONST        'Inexact'
          36	LOAD_CONST        'Rounded'
          39	LOAD_CONST        'Subnormal'
          42	LOAD_CONST        'Overflow'
          45	LOAD_CONST        'Underflow'

 130      48	LOAD_CONST        'ROUND_DOWN'
          51	LOAD_CONST        'ROUND_HALF_UP'
          54	LOAD_CONST        'ROUND_HALF_EVEN'
          57	LOAD_CONST        'ROUND_CEILING'

 131      60	LOAD_CONST        'ROUND_FLOOR'
          63	LOAD_CONST        'ROUND_UP'
          66	LOAD_CONST        'ROUND_HALF_DOWN'
          69	LOAD_CONST        'ROUND_05UP'

 134      72	LOAD_CONST        'setcontext'
          75	LOAD_CONST        'getcontext'
          78	LOAD_CONST        'localcontext'
          81	BUILD_LIST_25     ''
          84	STORE_NAME        '__all__'

 137      87	LOAD_CONST        -1
          90	LOAD_CONST        ''
          93	IMPORT_NAME       'copy'
          96	STORE_NAME        '_copy'

 138      99	LOAD_CONST        -1
         102	LOAD_CONST        ''
         105	IMPORT_NAME       'numbers'
         108	STORE_NAME        '_numbers'

 140     111	SETUP_EXCEPT      '149'

 141     114	LOAD_CONST        -1
         117	LOAD_CONST        ('namedtuple',)
         120	IMPORT_NAME       'collections'
         123	IMPORT_FROM       'namedtuple'
         126	STORE_NAME        '_namedtuple'
         129	POP_TOP           ''

 142     130	LOAD_NAME         '_namedtuple'
         133	LOAD_CONST        'DecimalTuple'
         136	LOAD_CONST        'sign digits exponent'
         139	CALL_FUNCTION_2   ''
         142	STORE_NAME        'DecimalTuple'
         145	POP_BLOCK         ''
         146	JUMP_FORWARD      '175'
       149_0	COME_FROM         '111'

 143     149	DUP_TOP           ''
         150	LOAD_NAME         'ImportError'
         153	COMPARE_OP        'exception match'
         156	JUMP_IF_FALSE     '174'
         159	POP_TOP           ''
         160	POP_TOP           ''
         161	POP_TOP           ''

 144     162	LOAD_LAMBDA       '<code_object <lambda>>'
         165	MAKE_FUNCTION_0   ''
         168	STORE_NAME        'DecimalTuple'
         171	JUMP_FORWARD      '175'
         174	END_FINALLY       ''
       175_0	COME_FROM         '146'
       175_1	COME_FROM         '174'

 147     175	LOAD_CONST        'ROUND_DOWN'
         178	STORE_NAME        'ROUND_DOWN'

 148     181	LOAD_CONST        'ROUND_HALF_UP'
         184	STORE_NAME        'ROUND_HALF_UP'

 149     187	LOAD_CONST        'ROUND_HALF_EVEN'
         190	STORE_NAME        'ROUND_HALF_EVEN'

 150     193	LOAD_CONST        'ROUND_CEILING'
         196	STORE_NAME        'ROUND_CEILING'

 151     199	LOAD_CONST        'ROUND_FLOOR'
         202	STORE_NAME        'ROUND_FLOOR'

 152     205	LOAD_CONST        'ROUND_UP'
         208	STORE_NAME        'ROUND_UP'

 153     211	LOAD_CONST        'ROUND_HALF_DOWN'
         214	STORE_NAME        'ROUND_HALF_DOWN'

 154     217	LOAD_CONST        'ROUND_05UP'
         220	STORE_NAME        'ROUND_05UP'

 158     223	LOAD_CONST        'DecimalException'
         226	LOAD_NAME         'ArithmeticError'
         229	BUILD_TUPLE_1     ''
         232	LOAD_CONST        '<code_object DecimalException>'
         235	MAKE_FUNCTION_0   ''
         238	CALL_FUNCTION_0   ''
         241	BUILD_CLASS       ''
         242	STORE_NAME        'DecimalException'

 181     245	LOAD_CONST        'Clamped'
         248	LOAD_NAME         'DecimalException'
         251	BUILD_TUPLE_1     ''
         254	LOAD_CONST        '<code_object Clamped>'
         257	MAKE_FUNCTION_0   ''
         260	CALL_FUNCTION_0   ''
         263	BUILD_CLASS       ''
         264	STORE_NAME        'Clamped'

 193     267	LOAD_CONST        'InvalidOperation'
         270	LOAD_NAME         'DecimalException'
         273	BUILD_TUPLE_1     ''
         276	LOAD_CONST        '<code_object InvalidOperation>'
         279	MAKE_FUNCTION_0   ''
         282	CALL_FUNCTION_0   ''
         285	BUILD_CLASS       ''
         286	STORE_NAME        'InvalidOperation'

 222     289	LOAD_CONST        'ConversionSyntax'
         292	LOAD_NAME         'InvalidOperation'
         295	BUILD_TUPLE_1     ''
         298	LOAD_CONST        '<code_object ConversionSyntax>'
         301	MAKE_FUNCTION_0   ''
         304	CALL_FUNCTION_0   ''
         307	BUILD_CLASS       ''
         308	STORE_NAME        'ConversionSyntax'

 232     311	LOAD_CONST        'DivisionByZero'
         314	LOAD_NAME         'DecimalException'
         317	LOAD_NAME         'ZeroDivisionError'
         320	BUILD_TUPLE_2     ''
         323	LOAD_CONST        '<code_object DivisionByZero>'
         326	MAKE_FUNCTION_0   ''
         329	CALL_FUNCTION_0   ''
         332	BUILD_CLASS       ''
         333	STORE_NAME        'DivisionByZero'

 248     336	LOAD_CONST        'DivisionImpossible'
         339	LOAD_NAME         'InvalidOperation'
         342	BUILD_TUPLE_1     ''
         345	LOAD_CONST        '<code_object DivisionImpossible>'
         348	MAKE_FUNCTION_0   ''
         351	CALL_FUNCTION_0   ''
         354	BUILD_CLASS       ''
         355	STORE_NAME        'DivisionImpossible'

 259     358	LOAD_CONST        'DivisionUndefined'
         361	LOAD_NAME         'InvalidOperation'
         364	LOAD_NAME         'ZeroDivisionError'
         367	BUILD_TUPLE_2     ''
         370	LOAD_CONST        '<code_object DivisionUndefined>'
         373	MAKE_FUNCTION_0   ''
         376	CALL_FUNCTION_0   ''
         379	BUILD_CLASS       ''
         380	STORE_NAME        'DivisionUndefined'

 270     383	LOAD_CONST        'Inexact'
         386	LOAD_NAME         'DecimalException'
         389	BUILD_TUPLE_1     ''
         392	LOAD_CONST        '<code_object Inexact>'
         395	MAKE_FUNCTION_0   ''
         398	CALL_FUNCTION_0   ''
         401	BUILD_CLASS       ''
         402	STORE_NAME        'Inexact'

 282     405	LOAD_CONST        'InvalidContext'
         408	LOAD_NAME         'InvalidOperation'
         411	BUILD_TUPLE_1     ''
         414	LOAD_CONST        '<code_object InvalidContext>'
         417	MAKE_FUNCTION_0   ''
         420	CALL_FUNCTION_0   ''
         423	BUILD_CLASS       ''
         424	STORE_NAME        'InvalidContext'

 296     427	LOAD_CONST        'Rounded'
         430	LOAD_NAME         'DecimalException'
         433	BUILD_TUPLE_1     ''
         436	LOAD_CONST        '<code_object Rounded>'
         439	MAKE_FUNCTION_0   ''
         442	CALL_FUNCTION_0   ''
         445	BUILD_CLASS       ''
         446	STORE_NAME        'Rounded'

 308     449	LOAD_CONST        'Subnormal'
         452	LOAD_NAME         'DecimalException'
         455	BUILD_TUPLE_1     ''
         458	LOAD_CONST        '<code_object Subnormal>'
         461	MAKE_FUNCTION_0   ''
         464	CALL_FUNCTION_0   ''
         467	BUILD_CLASS       ''
         468	STORE_NAME        'Subnormal'

 319     471	LOAD_CONST        'Overflow'
         474	LOAD_NAME         'Inexact'
         477	LOAD_NAME         'Rounded'
         480	BUILD_TUPLE_2     ''
         483	LOAD_CONST        '<code_object Overflow>'
         486	MAKE_FUNCTION_0   ''
         489	CALL_FUNCTION_0   ''
         492	BUILD_CLASS       ''
         493	STORE_NAME        'Overflow'

 357     496	LOAD_CONST        'Underflow'
         499	LOAD_NAME         'Inexact'
         502	LOAD_NAME         'Rounded'
         505	LOAD_NAME         'Subnormal'
         508	BUILD_TUPLE_3     ''
         511	LOAD_CONST        '<code_object Underflow>'
         514	MAKE_FUNCTION_0   ''
         517	CALL_FUNCTION_0   ''
         520	BUILD_CLASS       ''
         521	STORE_NAME        'Underflow'

 373     524	LOAD_NAME         'Clamped'
         527	LOAD_NAME         'DivisionByZero'
         530	LOAD_NAME         'Inexact'
         533	LOAD_NAME         'Overflow'
         536	LOAD_NAME         'Rounded'

 374     539	LOAD_NAME         'Underflow'
         542	LOAD_NAME         'InvalidOperation'
         545	LOAD_NAME         'Subnormal'
         548	BUILD_LIST_8      ''
         551	STORE_NAME        '_signals'

 377     554	BUILD_MAP         ''
         557	LOAD_NAME         'InvalidOperation'
         560	LOAD_NAME         'ConversionSyntax'
         563	STORE_MAP         ''

 378     564	LOAD_NAME         'InvalidOperation'
         567	LOAD_NAME         'DivisionImpossible'
         570	STORE_MAP         ''

 379     571	LOAD_NAME         'InvalidOperation'
         574	LOAD_NAME         'DivisionUndefined'
         577	STORE_MAP         ''

 380     578	LOAD_NAME         'InvalidOperation'
         581	LOAD_NAME         'InvalidContext'
         584	STORE_MAP         ''
         585	STORE_NAME        '_condition_map'

 390     588	SETUP_EXCEPT      '607'

 391     591	LOAD_CONST        -1
         594	LOAD_CONST        ''
         597	IMPORT_NAME       'threading'
         600	STORE_NAME        'threading'
         603	POP_BLOCK         ''
         604	JUMP_FORWARD      '673'
       607_0	COME_FROM         '588'

 392     607	DUP_TOP           ''
         608	LOAD_NAME         'ImportError'
         611	COMPARE_OP        'exception match'
         614	JUMP_IF_FALSE     '672'
         617	POP_TOP           ''
         618	POP_TOP           ''
         619	POP_TOP           ''

 394     620	LOAD_CONST        -1
         623	LOAD_CONST        ''
         626	IMPORT_NAME       'sys'
         629	STORE_NAME        'sys'

 395     632	LOAD_CONST        'MockThreading'
         635	LOAD_NAME         'object'
         638	BUILD_TUPLE_1     ''
         641	LOAD_CONST        '<code_object MockThreading>'
         644	MAKE_FUNCTION_0   ''
         647	CALL_FUNCTION_0   ''
         650	BUILD_CLASS       ''
         651	STORE_NAME        'MockThreading'

 398     654	LOAD_NAME         'MockThreading'
         657	CALL_FUNCTION_0   ''
         660	STORE_NAME        'threading'

 399     663	DELETE_NAME       'sys'
         666	DELETE_NAME       'MockThreading'
         669	JUMP_FORWARD      '673'
         672	END_FINALLY       ''
       673_0	COME_FROM         '604'
       673_1	COME_FROM         '672'

 401     673	SETUP_EXCEPT      '687'

 402     676	LOAD_NAME         'threading'
         679	LOAD_ATTR         'local'
         682	POP_TOP           ''
         683	POP_BLOCK         ''
         684	JUMP_FORWARD      '758'
       687_0	COME_FROM         '673'

 404     687	DUP_TOP           ''
         688	LOAD_NAME         'AttributeError'
         691	COMPARE_OP        'exception match'
         694	JUMP_IF_FALSE     '757'
         697	POP_TOP           ''
         698	POP_TOP           ''
         699	POP_TOP           ''

 408     700	LOAD_NAME         'hasattr'
         703	LOAD_NAME         'threading'
         706	LOAD_ATTR         'currentThread'
         709	CALL_FUNCTION_0   ''
         712	LOAD_CONST        '__decimal_context__'
         715	CALL_FUNCTION_2   ''
         718	JUMP_IF_FALSE     '736'

 409     721	LOAD_NAME         'threading'
         724	LOAD_ATTR         'currentThread'
         727	CALL_FUNCTION_0   ''
         730	DELETE_ATTR       '__decimal_context__'
         733	JUMP_FORWARD      '736'
       736_0	COME_FROM         '733'

 411     736	LOAD_CONST        '<code_object setcontext>'
         739	MAKE_FUNCTION_0   ''
         742	STORE_NAME        'setcontext'

 418     745	LOAD_CONST        '<code_object getcontext>'
         748	MAKE_FUNCTION_0   ''
         751	STORE_NAME        'getcontext'
         754	JUMP_FORWARD      '824'
         757	END_FINALLY       ''
       758_0	COME_FROM         '684'

 434     758	LOAD_NAME         'threading'
         761	LOAD_ATTR         'local'
         764	CALL_FUNCTION_0   ''
         767	STORE_NAME        'local'

 435     770	LOAD_NAME         'hasattr'
         773	LOAD_NAME         'local'
         776	LOAD_CONST        '__decimal_context__'
         779	CALL_FUNCTION_2   ''
         782	JUMP_IF_FALSE     '794'

 436     785	LOAD_NAME         'local'
         788	DELETE_ATTR       '__decimal_context__'
         791	JUMP_FORWARD      '794'
       794_0	COME_FROM         '791'

 438     794	LOAD_NAME         'local'
         797	LOAD_CONST        '<code_object getcontext>'
         800	MAKE_FUNCTION_1   ''
         803	STORE_NAME        'getcontext'

 452     806	LOAD_NAME         'local'
         809	LOAD_CONST        '<code_object setcontext>'
         812	MAKE_FUNCTION_1   ''
         815	STORE_NAME        'setcontext'

 459     818	DELETE_NAME       'threading'
         821	DELETE_NAME       'local'
       824_0	COME_FROM         '757'

 461     824	LOAD_NAME         'None'
         827	LOAD_CONST        '<code_object localcontext>'
         830	MAKE_FUNCTION_1   ''
         833	STORE_NAME        'localcontext'

 503     836	LOAD_CONST        'Decimal'
         839	LOAD_NAME         'object'
         842	BUILD_TUPLE_1     ''
         845	LOAD_CONST        '<code_object Decimal>'
         848	MAKE_FUNCTION_0   ''
         851	CALL_FUNCTION_0   ''
         854	BUILD_CLASS       ''
         855	STORE_NAME        'Decimal'

3553     858	LOAD_NAME         'False'
         861	LOAD_CONST        '<code_object _dec_from_triple>'
         864	MAKE_FUNCTION_1   ''
         867	STORE_NAME        '_dec_from_triple'

3572     870	LOAD_NAME         '_numbers'
         873	LOAD_ATTR         'Number'
         876	LOAD_ATTR         'register'
         879	LOAD_NAME         'Decimal'
         882	CALL_FUNCTION_1   ''
         885	POP_TOP           ''

3579     886	BUILD_LIST_0      ''
         889	LOAD_NAME         'Decimal'
         892	LOAD_ATTR         '__dict__'
         895	LOAD_ATTR         'keys'
         898	CALL_FUNCTION_0   ''
         901	GET_ITER          ''
         902	FOR_ITER          '935'
         905	STORE_NAME        'name'

3580     908	LOAD_NAME         'name'
         911	LOAD_ATTR         'startswith'
         914	LOAD_CONST        '_round_'
         917	CALL_FUNCTION_1   ''
         920	JUMP_IF_FALSE     '932'
         923	LOAD_NAME         'name'
         926	LIST_APPEND       ''
         929	JUMP_FORWARD      '932'
       932_0	COME_FROM         '929'
         932	CONTINUE          '902'
         935	STORE_NAME        'rounding_functions'

3581     938	SETUP_LOOP        '997'
         941	LOAD_NAME         'rounding_functions'
         944	GET_ITER          ''
         945	FOR_ITER          '996'
         948	STORE_NAME        'name'

3583     951	LOAD_NAME         'name'
         954	LOAD_CONST        1
         957	SLICE+1           ''
         958	LOAD_ATTR         'upper'
         961	CALL_FUNCTION_0   ''
         964	STORE_NAME        'globalname'

3584     967	LOAD_NAME         'globals'
         970	CALL_FUNCTION_0   ''
         973	LOAD_NAME         'globalname'
         976	BINARY_SUBSCR     ''
         977	STORE_NAME        'val'

3585     980	LOAD_NAME         'name'
         983	LOAD_NAME         'Decimal'
         986	LOAD_ATTR         '_pick_rounding_function'
         989	LOAD_NAME         'val'
         992	STORE_SUBSCR      ''
         993	JUMP_BACK         '945'
         996	POP_BLOCK         ''
       997_0	COME_FROM         '938'

3587     997	DELETE_NAME       'name'
        1000	DELETE_NAME       'val'
        1003	DELETE_NAME       'globalname'
        1006	DELETE_NAME       'rounding_functions'

3589    1009	LOAD_CONST        '_ContextManager'
        1012	LOAD_NAME         'object'
        1015	BUILD_TUPLE_1     ''
        1018	LOAD_CONST        '<code_object _ContextManager>'
        1021	MAKE_FUNCTION_0   ''
        1024	CALL_FUNCTION_0   ''
        1027	BUILD_CLASS       ''
        1028	STORE_NAME        '_ContextManager'

3604    1031	LOAD_CONST        'Context'
        1034	LOAD_NAME         'object'
        1037	BUILD_TUPLE_1     ''
        1040	LOAD_CONST        '<code_object Context>'
        1043	MAKE_FUNCTION_0   ''
        1046	CALL_FUNCTION_0   ''
        1049	BUILD_CLASS       ''
        1050	STORE_NAME        'Context'

4896    1053	LOAD_CONST        '_WorkRep'
        1056	LOAD_NAME         'object'
        1059	BUILD_TUPLE_1     ''
        1062	LOAD_CONST        '<code_object _WorkRep>'
        1065	MAKE_FUNCTION_0   ''
        1068	CALL_FUNCTION_0   ''
        1071	BUILD_CLASS       ''
        1072	STORE_NAME        '_WorkRep'

4924    1075	LOAD_CONST        0
        1078	LOAD_CONST        '<code_object _normalize>'
        1081	MAKE_FUNCTION_1   ''
        1084	STORE_NAME        '_normalize'

4959    1087	BUILD_MAP         ''

4960    1090	LOAD_CONST        4
        1093	LOAD_CONST        '0'
        1096	STORE_MAP         ''
        1097	LOAD_CONST        3
        1100	LOAD_CONST        '1'
        1103	STORE_MAP         ''
        1104	LOAD_CONST        2
        1107	LOAD_CONST        '2'
        1110	STORE_MAP         ''
        1111	LOAD_CONST        2
        1114	LOAD_CONST        '3'
        1117	STORE_MAP         ''

4961    1118	LOAD_CONST        1
        1121	LOAD_CONST        '4'
        1124	STORE_MAP         ''
        1125	LOAD_CONST        1
        1128	LOAD_CONST        '5'
        1131	STORE_MAP         ''
        1132	LOAD_CONST        1
        1135	LOAD_CONST        '6'
        1138	STORE_MAP         ''
        1139	LOAD_CONST        1
        1142	LOAD_CONST        '7'
        1145	STORE_MAP         ''

4962    1146	LOAD_CONST        0
        1149	LOAD_CONST        '8'
        1152	STORE_MAP         ''
        1153	LOAD_CONST        0
        1156	LOAD_CONST        '9'
        1159	STORE_MAP         ''
        1160	LOAD_CONST        0
        1163	LOAD_CONST        'a'
        1166	STORE_MAP         ''
        1167	LOAD_CONST        0
        1170	LOAD_CONST        'b'
        1173	STORE_MAP         ''

4963    1174	LOAD_CONST        0
        1177	LOAD_CONST        'c'
        1180	STORE_MAP         ''
        1181	LOAD_CONST        0
        1184	LOAD_CONST        'd'
        1187	STORE_MAP         ''
        1188	LOAD_CONST        0
        1191	LOAD_CONST        'e'
        1194	STORE_MAP         ''
        1195	LOAD_CONST        0
        1198	LOAD_CONST        'f'
        1201	STORE_MAP         ''
        1202	LOAD_CONST        '<code_object _nbits>'
        1205	MAKE_FUNCTION_1   ''
        1208	STORE_NAME        '_nbits'

4972    1211	LOAD_CONST        '<code_object _sqrt_nearest>'
        1214	MAKE_FUNCTION_0   ''
        1217	STORE_NAME        '_sqrt_nearest'

4987    1220	LOAD_CONST        '<code_object _rshift_nearest>'
        1223	MAKE_FUNCTION_0   ''
        1226	STORE_NAME        '_rshift_nearest'

4995    1229	LOAD_CONST        '<code_object _div_nearest>'
        1232	MAKE_FUNCTION_0   ''
        1235	STORE_NAME        '_div_nearest'

5003    1238	LOAD_CONST        8
        1241	LOAD_CONST        '<code_object _ilog>'
        1244	MAKE_FUNCTION_1   ''
        1247	STORE_NAME        '_ilog'

5051    1250	LOAD_CONST        '<code_object _dlog10>'
        1253	MAKE_FUNCTION_0   ''
        1256	STORE_NAME        '_dlog10'

5085    1259	LOAD_CONST        '<code_object _dlog>'
        1262	MAKE_FUNCTION_0   ''
        1265	STORE_NAME        '_dlog'

5129    1268	LOAD_CONST        '_Log10Memoize'
        1271	LOAD_NAME         'object'
        1274	BUILD_TUPLE_1     ''
        1277	LOAD_CONST        '<code_object _Log10Memoize>'
        1280	MAKE_FUNCTION_0   ''
        1283	CALL_FUNCTION_0   ''
        1286	BUILD_CLASS       ''
        1287	STORE_NAME        '_Log10Memoize'

5164    1290	LOAD_NAME         '_Log10Memoize'
        1293	CALL_FUNCTION_0   ''
        1296	LOAD_ATTR         'getdigits'
        1299	STORE_NAME        '_log10_digits'

5166    1302	LOAD_CONST        8
        1305	LOAD_CONST        '<code_object _iexp>'
        1308	MAKE_FUNCTION_1   ''
        1311	STORE_NAME        '_iexp'

5203    1314	LOAD_CONST        '<code_object _dexp>'
        1317	MAKE_FUNCTION_0   ''
        1320	STORE_NAME        '_dexp'

5239    1323	LOAD_CONST        '<code_object _dpower>'
        1326	MAKE_FUNCTION_0   ''
        1329	STORE_NAME        '_dpower'

5281    1332	BUILD_MAP         ''

5282    1335	LOAD_CONST        100
        1338	LOAD_CONST        '1'
        1341	STORE_MAP         ''
        1342	LOAD_CONST        70
        1345	LOAD_CONST        '2'
        1348	STORE_MAP         ''
        1349	LOAD_CONST        53
        1352	LOAD_CONST        '3'
        1355	STORE_MAP         ''
        1356	LOAD_CONST        40
        1359	LOAD_CONST        '4'
        1362	STORE_MAP         ''
        1363	LOAD_CONST        31
        1366	LOAD_CONST        '5'
        1369	STORE_MAP         ''

5283    1370	LOAD_CONST        23
        1373	LOAD_CONST        '6'
        1376	STORE_MAP         ''
        1377	LOAD_CONST        16
        1380	LOAD_CONST        '7'
        1383	STORE_MAP         ''
        1384	LOAD_CONST        10
        1387	LOAD_CONST        '8'
        1390	STORE_MAP         ''
        1391	LOAD_CONST        5
        1394	LOAD_CONST        '9'
        1397	STORE_MAP         ''
        1398	LOAD_CONST        '<code_object _log10_lb>'
        1401	MAKE_FUNCTION_1   ''
        1404	STORE_NAME        '_log10_lb'

5292    1407	LOAD_NAME         'False'
        1410	LOAD_CONST        '<code_object _convert_other>'
        1413	MAKE_FUNCTION_1   ''
        1416	STORE_NAME        '_convert_other'

5310    1419	LOAD_NAME         'Context'
        1422	LOAD_CONST        'prec'

5311    1425	LOAD_CONST        28
        1428	LOAD_CONST        'rounding'
        1431	LOAD_NAME         'ROUND_HALF_EVEN'
        1434	LOAD_CONST        'traps'

5312    1437	LOAD_NAME         'DivisionByZero'
        1440	LOAD_NAME         'Overflow'
        1443	LOAD_NAME         'InvalidOperation'
        1446	BUILD_LIST_3      ''
        1449	LOAD_CONST        'flags'

5313    1452	BUILD_LIST_0      ''
        1455	LOAD_CONST        'Emax'

5314    1458	LOAD_CONST        999999999
        1461	LOAD_CONST        'Emin'

5315    1464	LOAD_CONST        -999999999
        1467	LOAD_CONST        'capitals'

5316    1470	LOAD_CONST        1
        1473	CALL_FUNCTION_1792 ''
        1476	STORE_NAME        'DefaultContext'

5324    1479	LOAD_NAME         'Context'
        1482	LOAD_CONST        'prec'

5325    1485	LOAD_CONST        9
        1488	LOAD_CONST        'rounding'
        1491	LOAD_NAME         'ROUND_HALF_UP'
        1494	LOAD_CONST        'traps'

5326    1497	LOAD_NAME         'DivisionByZero'
        1500	LOAD_NAME         'Overflow'
        1503	LOAD_NAME         'InvalidOperation'
        1506	LOAD_NAME         'Clamped'
        1509	LOAD_NAME         'Underflow'
        1512	BUILD_LIST_5      ''
        1515	LOAD_CONST        'flags'

5327    1518	BUILD_LIST_0      ''
        1521	CALL_FUNCTION_1024 ''
        1524	STORE_NAME        'BasicContext'

5330    1527	LOAD_NAME         'Context'
        1530	LOAD_CONST        'prec'

5331    1533	LOAD_CONST        9
        1536	LOAD_CONST        'rounding'
        1539	LOAD_NAME         'ROUND_HALF_EVEN'
        1542	LOAD_CONST        'traps'

5332    1545	BUILD_LIST_0      ''
        1548	LOAD_CONST        'flags'

5333    1551	BUILD_LIST_0      ''
        1554	CALL_FUNCTION_1024 ''
        1557	STORE_NAME        'ExtendedContext'

5351    1560	LOAD_CONST        -1
        1563	LOAD_CONST        ''
        1566	IMPORT_NAME       're'
        1569	STORE_NAME        're'

5352    1572	LOAD_NAME         're'
        1575	LOAD_ATTR         'compile'

5369    1578	LOAD_CONST        '        # A numeric string consists of:\n#    \\s*\n    (?P<sign>[-+])?              # an optional sign, followed by either...\n    (\n        (?=\\d|\\.\\d)              # ...a number (with at least one digit)\n        (?P<int>\\d*)             # having a (possibly empty) integer part\n        (\\.(?P<frac>\\d*))?       # followed by an optional fractional part\n        (E(?P<exp>[-+]?\\d+))?    # followed by an optional exponent, or...\n    |\n        Inf(inity)?              # ...an infinity, or...\n    |\n        (?P<signal>s)?           # ...an (optionally signaling)\n        NaN                      # NaN\n        (?P<diag>\\d*)            # with (possibly empty) diagnostic info.\n    )\n#    \\s*\n    \\Z\n'
        1581	LOAD_NAME         're'
        1584	LOAD_ATTR         'VERBOSE'
        1587	LOAD_NAME         're'
        1590	LOAD_ATTR         'IGNORECASE'
        1593	BINARY_OR         ''
        1594	LOAD_NAME         're'
        1597	LOAD_ATTR         'UNICODE'
        1600	BINARY_OR         ''
        1601	CALL_FUNCTION_2   ''
        1604	LOAD_ATTR         'match'
        1607	STORE_NAME        '_parser'

5371    1610	LOAD_NAME         're'
        1613	LOAD_ATTR         'compile'
        1616	LOAD_CONST        '0*$'
        1619	CALL_FUNCTION_1   ''
        1622	LOAD_ATTR         'match'
        1625	STORE_NAME        '_all_zeros'

5372    1628	LOAD_NAME         're'
        1631	LOAD_ATTR         'compile'
        1634	LOAD_CONST        '50*$'
        1637	CALL_FUNCTION_1   ''
        1640	LOAD_ATTR         'match'
        1643	STORE_NAME        '_exact_half'

5384    1646	LOAD_NAME         're'
        1649	LOAD_ATTR         'compile'

5395    1652	LOAD_CONST        '\\A\n(?:\n   (?P<fill>.)?\n   (?P<align>[<>=^])\n)?\n(?P<sign>[-+ ])?\n(?P<zeropad>0)?\n(?P<minimumwidth>(?!0)\\d+)?\n(?:\\.(?P<precision>0|(?!0)\\d+))?\n(?P<type>[eEfFgG%])?\n\\Z\n'
        1655	LOAD_NAME         're'
        1658	LOAD_ATTR         'VERBOSE'
        1661	CALL_FUNCTION_2   ''
        1664	STORE_NAME        '_parse_format_specifier_regex'

5397    1667	DELETE_NAME       're'

5399    1670	LOAD_CONST        '<code_object _parse_format_specifier>'
        1673	MAKE_FUNCTION_0   ''
        1676	STORE_NAME        '_parse_format_specifier'

5457    1679	LOAD_CONST        '<code_object _format_align>'
        1682	MAKE_FUNCTION_0   ''
        1685	STORE_NAME        '_format_align'

5507    1688	LOAD_NAME         'Decimal'
        1691	LOAD_CONST        'Inf'
        1694	CALL_FUNCTION_1   ''
        1697	STORE_NAME        '_Infinity'

5508    1700	LOAD_NAME         'Decimal'
        1703	LOAD_CONST        '-Inf'
        1706	CALL_FUNCTION_1   ''
        1709	STORE_NAME        '_NegativeInfinity'

5509    1712	LOAD_NAME         'Decimal'
        1715	LOAD_CONST        'NaN'
        1718	CALL_FUNCTION_1   ''
        1721	STORE_NAME        '_NaN'

5510    1724	LOAD_NAME         'Decimal'
        1727	LOAD_CONST        0
        1730	CALL_FUNCTION_1   ''
        1733	STORE_NAME        '_Zero'

5511    1736	LOAD_NAME         'Decimal'
        1739	LOAD_CONST        1
        1742	CALL_FUNCTION_1   ''
        1745	STORE_NAME        '_One'

5512    1748	LOAD_NAME         'Decimal'
        1751	LOAD_CONST        -1
        1754	CALL_FUNCTION_1   ''
        1757	STORE_NAME        '_NegativeOne'

5515    1760	LOAD_NAME         '_Infinity'
        1763	LOAD_NAME         '_NegativeInfinity'
        1766	BUILD_TUPLE_2     ''
        1769	STORE_NAME        '_SignedInfinity'

5519    1772	LOAD_NAME         '__name__'
        1775	LOAD_CONST        '__main__'
        1778	COMPARE_OP        '=='
        1781	JUMP_IF_FALSE     '1831'

5520    1784	LOAD_CONST        -1
        1787	LOAD_CONST        ''
        1790	IMPORT_NAME       'doctest'
        1793	STORE_NAME        'doctest'
        1796	LOAD_CONST        -1
        1799	LOAD_CONST        ''
        1802	IMPORT_NAME_CONT  'sys'
        1805	STORE_NAME        'sys'

5521    1808	LOAD_NAME         'doctest'
        1811	LOAD_ATTR         'testmod'
        1814	LOAD_NAME         'sys'
        1817	LOAD_ATTR         'modules'
        1820	LOAD_NAME         '__name__'
        1823	BINARY_SUBSCR     ''
        1824	CALL_FUNCTION_1   ''
        1827	POP_TOP           ''
        1828	JUMP_FORWARD      '1831'
      1831_0	COME_FROM         '1828'

Syntax error at or near 'JUMP_FORWARD' token at offset 929
