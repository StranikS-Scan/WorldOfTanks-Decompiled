# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/pickle.py
# Compiled at: 2010-05-25 20:46:16

--- This code section failed: ---

  25       0	LOAD_CONST        'Create portable serialized representations of Python objects.\n\nSee module cPickle for a (much) faster implementation.\nSee module copy_reg for a mechanism for registering custom picklers.\nSee module pickletools source for extensive comments.\n\nClasses:\n\n    Pickler\n    Unpickler\n\nFunctions:\n\n    dump(object, file)\n    dumps(object) -> string\n    load(file) -> object\n    loads(string) -> object\n\nMisc variables:\n\n    __version__\n    format_version\n    compatible_formats\n\n'
           3	STORE_NAME        '__doc__'

  27       6	LOAD_CONST        '$Revision: 65524 $'
           9	STORE_NAME        '__version__'

  29      12	LOAD_CONST        -1
          15	LOAD_CONST        ('*',)
          18	IMPORT_NAME       'types'
          21	IMPORT_STAR       ''

  30      22	LOAD_CONST        -1
          25	LOAD_CONST        ('dispatch_table',)
          28	IMPORT_NAME       'copy_reg'
          31	IMPORT_FROM       'dispatch_table'
          34	STORE_NAME        'dispatch_table'
          37	POP_TOP           ''

  31      38	LOAD_CONST        -1
          41	LOAD_CONST        ('_extension_registry', '_inverted_registry', '_extension_cache')
          44	IMPORT_NAME       'copy_reg'
          47	IMPORT_FROM       '_extension_registry'
          50	STORE_NAME        '_extension_registry'
          53	IMPORT_FROM       '_inverted_registry'
          56	STORE_NAME        '_inverted_registry'
          59	IMPORT_FROM       '_extension_cache'
          62	STORE_NAME        '_extension_cache'
          65	POP_TOP           ''

  32      66	LOAD_CONST        -1
          69	LOAD_CONST        ''
          72	IMPORT_NAME       'marshal'
          75	STORE_NAME        'marshal'

  33      78	LOAD_CONST        -1
          81	LOAD_CONST        ''
          84	IMPORT_NAME       'sys'
          87	STORE_NAME        'sys'

  34      90	LOAD_CONST        -1
          93	LOAD_CONST        ''
          96	IMPORT_NAME       'struct'
          99	STORE_NAME        'struct'

  35     102	LOAD_CONST        -1
         105	LOAD_CONST        ''
         108	IMPORT_NAME       're'
         111	STORE_NAME        're'

  37     114	LOAD_CONST        'PickleError'
         117	LOAD_CONST        'PicklingError'
         120	LOAD_CONST        'UnpicklingError'
         123	LOAD_CONST        'Pickler'

  38     126	LOAD_CONST        'Unpickler'
         129	LOAD_CONST        'dump'
         132	LOAD_CONST        'dumps'
         135	LOAD_CONST        'load'
         138	LOAD_CONST        'loads'
         141	BUILD_LIST_9      ''
         144	STORE_NAME        '__all__'

  41     147	LOAD_CONST        '2.0'
         150	STORE_NAME        'format_version'

  42     153	LOAD_CONST        '1.0'

  43     156	LOAD_CONST        '1.1'

  44     159	LOAD_CONST        '1.2'

  45     162	LOAD_CONST        '1.3'

  46     165	LOAD_CONST        '2.0'
         168	BUILD_LIST_5      ''
         171	STORE_NAME        'compatible_formats'

  51     174	LOAD_CONST        2
         177	STORE_NAME        'HIGHEST_PROTOCOL'

  56     180	LOAD_NAME         'marshal'
         183	LOAD_ATTR         'loads'
         186	STORE_NAME        'mloads'

  58     189	LOAD_CONST        'PickleError'
         192	LOAD_NAME         'Exception'
         195	BUILD_TUPLE_1     ''
         198	LOAD_CONST        '<code_object PickleError>'
         201	MAKE_FUNCTION_0   ''
         204	CALL_FUNCTION_0   ''
         207	BUILD_CLASS       ''
         208	STORE_NAME        'PickleError'

  62     211	LOAD_CONST        'PicklingError'
         214	LOAD_NAME         'PickleError'
         217	BUILD_TUPLE_1     ''
         220	LOAD_CONST        '<code_object PicklingError>'
         223	MAKE_FUNCTION_0   ''
         226	CALL_FUNCTION_0   ''
         229	BUILD_CLASS       ''
         230	STORE_NAME        'PicklingError'

  69     233	LOAD_CONST        'UnpicklingError'
         236	LOAD_NAME         'PickleError'
         239	BUILD_TUPLE_1     ''
         242	LOAD_CONST        '<code_object UnpicklingError>'
         245	MAKE_FUNCTION_0   ''
         248	CALL_FUNCTION_0   ''
         251	BUILD_CLASS       ''
         252	STORE_NAME        'UnpicklingError'

  82     255	LOAD_CONST        '_Stop'
         258	LOAD_NAME         'Exception'
         261	BUILD_TUPLE_1     ''
         264	LOAD_CONST        '<code_object _Stop>'
         267	MAKE_FUNCTION_0   ''
         270	CALL_FUNCTION_0   ''
         273	BUILD_CLASS       ''
         274	STORE_NAME        '_Stop'

  87     277	SETUP_EXCEPT      '300'

  88     280	LOAD_CONST        -1
         283	LOAD_CONST        ('PyStringMap',)
         286	IMPORT_NAME       'org.python.core'
         289	IMPORT_FROM       'PyStringMap'
         292	STORE_NAME        'PyStringMap'
         295	POP_TOP           ''
         296	POP_BLOCK         ''
         297	JUMP_FORWARD      '323'
       300_0	COME_FROM         '277'

  89     300	DUP_TOP           ''
         301	LOAD_NAME         'ImportError'
         304	COMPARE_OP        'exception match'
         307	JUMP_IF_FALSE     '322'
         310	POP_TOP           ''
         311	POP_TOP           ''
         312	POP_TOP           ''

  90     313	LOAD_NAME         'None'
         316	STORE_NAME        'PyStringMap'
         319	JUMP_FORWARD      '323'
         322	END_FINALLY       ''
       323_0	COME_FROM         '297'
       323_1	COME_FROM         '322'

  93     323	SETUP_EXCEPT      '334'

  94     326	LOAD_NAME         'UnicodeType'
         329	POP_TOP           ''
         330	POP_BLOCK         ''
         331	JUMP_FORWARD      '357'
       334_0	COME_FROM         '323'

  95     334	DUP_TOP           ''
         335	LOAD_NAME         'NameError'
         338	COMPARE_OP        'exception match'
         341	JUMP_IF_FALSE     '356'
         344	POP_TOP           ''
         345	POP_TOP           ''
         346	POP_TOP           ''

  96     347	LOAD_NAME         'None'
         350	STORE_NAME        'UnicodeType'
         353	JUMP_FORWARD      '357'
         356	END_FINALLY       ''
       357_0	COME_FROM         '331'
       357_1	COME_FROM         '356'

 102     357	LOAD_CONST        '('
         360	STORE_NAME        'MARK'

 103     363	LOAD_CONST        '.'
         366	STORE_NAME        'STOP'

 104     369	LOAD_CONST        '0'
         372	STORE_NAME        'POP'

 105     375	LOAD_CONST        '1'
         378	STORE_NAME        'POP_MARK'

 106     381	LOAD_CONST        '2'
         384	STORE_NAME        'DUP'

 107     387	LOAD_CONST        'F'
         390	STORE_NAME        'FLOAT'

 108     393	LOAD_CONST        'I'
         396	STORE_NAME        'INT'

 109     399	LOAD_CONST        'J'
         402	STORE_NAME        'BININT'

 110     405	LOAD_CONST        'K'
         408	STORE_NAME        'BININT1'

 111     411	LOAD_CONST        'L'
         414	STORE_NAME        'LONG'

 112     417	LOAD_CONST        'M'
         420	STORE_NAME        'BININT2'

 113     423	LOAD_CONST        'N'
         426	STORE_NAME        'NONE'

 114     429	LOAD_CONST        'P'
         432	STORE_NAME        'PERSID'

 115     435	LOAD_CONST        'Q'
         438	STORE_NAME        'BINPERSID'

 116     441	LOAD_CONST        'R'
         444	STORE_NAME        'REDUCE'

 117     447	LOAD_CONST        'S'
         450	STORE_NAME        'STRING'

 118     453	LOAD_CONST        'T'
         456	STORE_NAME        'BINSTRING'

 119     459	LOAD_CONST        'U'
         462	STORE_NAME        'SHORT_BINSTRING'

 120     465	LOAD_CONST        'V'
         468	STORE_NAME        'UNICODE'

 121     471	LOAD_CONST        'X'
         474	STORE_NAME        'BINUNICODE'

 122     477	LOAD_CONST        'a'
         480	STORE_NAME        'APPEND'

 123     483	LOAD_CONST        'b'
         486	STORE_NAME        'BUILD'

 124     489	LOAD_CONST        'c'
         492	STORE_NAME        'GLOBAL'

 125     495	LOAD_CONST        'd'
         498	STORE_NAME        'DICT'

 126     501	LOAD_CONST        '}'
         504	STORE_NAME        'EMPTY_DICT'

 127     507	LOAD_CONST        'e'
         510	STORE_NAME        'APPENDS'

 128     513	LOAD_CONST        'g'
         516	STORE_NAME        'GET'

 129     519	LOAD_CONST        'h'
         522	STORE_NAME        'BINGET'

 130     525	LOAD_CONST        'i'
         528	STORE_NAME        'INST'

 131     531	LOAD_CONST        'j'
         534	STORE_NAME        'LONG_BINGET'

 132     537	LOAD_CONST        'l'
         540	STORE_NAME        'LIST'

 133     543	LOAD_CONST        ']'
         546	STORE_NAME        'EMPTY_LIST'

 134     549	LOAD_CONST        'o'
         552	STORE_NAME        'OBJ'

 135     555	LOAD_CONST        'p'
         558	STORE_NAME        'PUT'

 136     561	LOAD_CONST        'q'
         564	STORE_NAME        'BINPUT'

 137     567	LOAD_CONST        'r'
         570	STORE_NAME        'LONG_BINPUT'

 138     573	LOAD_CONST        's'
         576	STORE_NAME        'SETITEM'

 139     579	LOAD_CONST        't'
         582	STORE_NAME        'TUPLE'

 140     585	LOAD_CONST        ')'
         588	STORE_NAME        'EMPTY_TUPLE'

 141     591	LOAD_CONST        'u'
         594	STORE_NAME        'SETITEMS'

 142     597	LOAD_CONST        'G'
         600	STORE_NAME        'BINFLOAT'

 144     603	LOAD_CONST        'I01\n'
         606	STORE_NAME        'TRUE'

 145     609	LOAD_CONST        'I00\n'
         612	STORE_NAME        'FALSE'

 149     615	LOAD_CONST        '\x80'
         618	STORE_NAME        'PROTO'

 150     621	LOAD_CONST        '\x81'
         624	STORE_NAME        'NEWOBJ'

 151     627	LOAD_CONST        '\x82'
         630	STORE_NAME        'EXT1'

 152     633	LOAD_CONST        '\x83'
         636	STORE_NAME        'EXT2'

 153     639	LOAD_CONST        '\x84'
         642	STORE_NAME        'EXT4'

 154     645	LOAD_CONST        '\x85'
         648	STORE_NAME        'TUPLE1'

 155     651	LOAD_CONST        '\x86'
         654	STORE_NAME        'TUPLE2'

 156     657	LOAD_CONST        '\x87'
         660	STORE_NAME        'TUPLE3'

 157     663	LOAD_CONST        '\x88'
         666	STORE_NAME        'NEWTRUE'

 158     669	LOAD_CONST        '\x89'
         672	STORE_NAME        'NEWFALSE'

 159     675	LOAD_CONST        '\x8a'
         678	STORE_NAME        'LONG1'

 160     681	LOAD_CONST        '\x8b'
         684	STORE_NAME        'LONG4'

 162     687	LOAD_NAME         'EMPTY_TUPLE'
         690	LOAD_NAME         'TUPLE1'
         693	LOAD_NAME         'TUPLE2'
         696	LOAD_NAME         'TUPLE3'
         699	BUILD_LIST_4      ''
         702	STORE_NAME        '_tuplesize2code'

 165     705	LOAD_NAME         '__all__'
         708	LOAD_ATTR         'extend'
         711	BUILD_LIST_0      ''
         714	LOAD_NAME         'dir'
         717	CALL_FUNCTION_0   ''
         720	GET_ITER          ''
         721	FOR_ITER          '757'
         724	STORE_NAME        'x'
         727	LOAD_NAME         're'
         730	LOAD_ATTR         'match'
         733	LOAD_CONST        '[A-Z][A-Z0-9_]+$'
         736	LOAD_NAME         'x'
         739	CALL_FUNCTION_2   ''
         742	JUMP_IF_FALSE     '754'
         745	LOAD_NAME         'x'
         748	LIST_APPEND       ''
         751	JUMP_FORWARD      '754'
       754_0	COME_FROM         '751'
         754	CONTINUE          '721'
         757	CALL_FUNCTION_1   ''
         760	POP_TOP           ''

 166     761	DELETE_NAME       'x'

 171     764	LOAD_CONST        'Pickler'
         767	BUILD_TUPLE_0     ''
         770	LOAD_CONST        '<code_object Pickler>'
         773	MAKE_FUNCTION_0   ''
         776	CALL_FUNCTION_0   ''
         779	BUILD_CLASS       ''
         780	STORE_NAME        'Pickler'

 777     783	LOAD_CONST        '<code_object _keep_alive>'
         786	MAKE_FUNCTION_0   ''
         789	STORE_NAME        '_keep_alive'

 797     792	BUILD_MAP         ''
         795	STORE_NAME        'classmap'

 799     798	LOAD_CONST        '<code_object whichmodule>'
         801	MAKE_FUNCTION_0   ''
         804	STORE_NAME        'whichmodule'

 827     807	LOAD_CONST        'Unpickler'
         810	BUILD_TUPLE_0     ''
         813	LOAD_CONST        '<code_object Unpickler>'
         816	MAKE_FUNCTION_0   ''
         819	CALL_FUNCTION_0   ''
         822	BUILD_CLASS       ''
         823	STORE_NAME        'Unpickler'

1253     826	LOAD_CONST        '_EmptyClass'
         829	BUILD_TUPLE_0     ''
         832	LOAD_CONST        '<code_object _EmptyClass>'
         835	MAKE_FUNCTION_0   ''
         838	CALL_FUNCTION_0   ''
         841	BUILD_CLASS       ''
         842	STORE_NAME        '_EmptyClass'

1258     845	LOAD_CONST        -1
         848	LOAD_CONST        ''
         851	IMPORT_NAME       'binascii'
         854	STORE_NAME        '_binascii'

1260     857	LOAD_CONST        '<code_object encode_long>'
         860	MAKE_FUNCTION_0   ''
         863	STORE_NAME        'encode_long'

1326     866	LOAD_CONST        '<code_object decode_long>'
         869	MAKE_FUNCTION_0   ''
         872	STORE_NAME        'decode_long'

1356     875	SETUP_EXCEPT      '898'

1357     878	LOAD_CONST        -1
         881	LOAD_CONST        ('StringIO',)
         884	IMPORT_NAME       'cStringIO'
         887	IMPORT_FROM       'StringIO'
         890	STORE_NAME        'StringIO'
         893	POP_TOP           ''
         894	POP_BLOCK         ''
         895	JUMP_FORWARD      '931'
       898_0	COME_FROM         '875'

1358     898	DUP_TOP           ''
         899	LOAD_NAME         'ImportError'
         902	COMPARE_OP        'exception match'
         905	JUMP_IF_FALSE     '930'
         908	POP_TOP           ''
         909	POP_TOP           ''
         910	POP_TOP           ''

1359     911	LOAD_CONST        -1
         914	LOAD_CONST        ('StringIO',)
         917	IMPORT_NAME       'StringIO'
         920	IMPORT_FROM       'StringIO'
         923	STORE_NAME        'StringIO'
         926	POP_TOP           ''
         927	JUMP_FORWARD      '931'
         930	END_FINALLY       ''
       931_0	COME_FROM         '895'
       931_1	COME_FROM         '930'

1361     931	LOAD_NAME         'None'
         934	LOAD_CONST        '<code_object dump>'
         937	MAKE_FUNCTION_1   ''
         940	STORE_NAME        'dump'

1364     943	LOAD_NAME         'None'
         946	LOAD_CONST        '<code_object dumps>'
         949	MAKE_FUNCTION_1   ''
         952	STORE_NAME        'dumps'

1369     955	LOAD_CONST        '<code_object load>'
         958	MAKE_FUNCTION_0   ''
         961	STORE_NAME        'load'

1372     964	LOAD_CONST        '<code_object loads>'
         967	MAKE_FUNCTION_0   ''
         970	STORE_NAME        'loads'

1378     973	LOAD_CONST        '<code_object _test>'
         976	MAKE_FUNCTION_0   ''
         979	STORE_NAME        '_test'

1382     982	LOAD_NAME         '__name__'
         985	LOAD_CONST        '__main__'
         988	COMPARE_OP        '=='
         991	JUMP_IF_FALSE     '1004'

1383     994	LOAD_NAME         '_test'
         997	CALL_FUNCTION_0   ''
        1000	POP_TOP           ''
        1001	JUMP_FORWARD      '1004'
      1004_0	COME_FROM         '1001'

Syntax error at or near 'JUMP_FORWARD' token at offset 751
