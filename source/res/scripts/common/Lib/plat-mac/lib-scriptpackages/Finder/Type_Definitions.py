# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/lib-scriptpackages/Finder/Type_Definitions.py
import aetools
import MacOS
_code = 'tpdf'

class Type_Definitions_Events:
    pass


class alias_list(aetools.ComponentItem):
    want = 'alst'


class label(aetools.ComponentItem):
    want = 'clbl'


class _Prop_color(aetools.NProperty):
    which = 'colr'
    want = 'cRGB'


class _Prop_index(aetools.NProperty):
    which = 'pidx'
    want = 'long'


class _Prop_name(aetools.NProperty):
    which = 'pnam'
    want = 'utxt'


class preferences(aetools.ComponentItem):
    want = 'cprf'


class _Prop_button_view_arrangement(aetools.NProperty):
    which = 'barr'
    want = 'earr'


class _Prop_button_view_icon_size(aetools.NProperty):
    which = 'bisz'
    want = 'long'


class _Prop_calculates_folder_sizes(aetools.NProperty):
    which = 'sfsz'
    want = 'bool'


class _Prop_delay_before_springing(aetools.NProperty):
    which = 'dela'
    want = 'shor'


class _Prop_list_view_icon_size(aetools.NProperty):
    which = 'lisz'
    want = 'long'


class _Prop_shows_comments(aetools.NProperty):
    which = 'scom'
    want = 'bool'


class _Prop_shows_creation_date(aetools.NProperty):
    which = 'scda'
    want = 'bool'


class _Prop_shows_kind(aetools.NProperty):
    which = 'sknd'
    want = 'bool'


class _Prop_shows_label(aetools.NProperty):
    which = 'slbl'
    want = 'bool'


class _Prop_shows_modification_date(aetools.NProperty):
    which = 'sdat'
    want = 'bool'


class _Prop_shows_size(aetools.NProperty):
    which = 'ssiz'
    want = 'bool'


class _Prop_shows_version(aetools.NProperty):
    which = 'svrs'
    want = 'bool'


class _Prop_spatial_view_arrangement(aetools.NProperty):
    which = 'iarr'
    want = 'earr'


class _Prop_spatial_view_icon_size(aetools.NProperty):
    which = 'iisz'
    want = 'long'


class _Prop_spring_open_folders(aetools.NProperty):
    which = 'sprg'
    want = 'bool'


class _Prop_uses_relative_dates(aetools.NProperty):
    which = 'urdt'
    want = 'bool'


class _Prop_uses_simple_menus(aetools.NProperty):
    which = 'usme'
    want = 'bool'


class _Prop_uses_wide_grid(aetools.NProperty):
    which = 'uswg'
    want = 'bool'


class _Prop_view_font(aetools.NProperty):
    which = 'vfnt'
    want = 'long'


class _Prop_view_font_size(aetools.NProperty):
    which = 'vfsz'
    want = 'long'


class _Prop_window(aetools.NProperty):
    which = 'cwin'
    want = 'pwnd'


class icon_view_options(aetools.ComponentItem):
    want = 'icop'


_Prop_arrangement = _Prop_spatial_view_arrangement

class _Prop_icon_size(aetools.NProperty):
    which = 'lvis'
    want = 'shor'


class icon_family(aetools.ComponentItem):
    want = 'ifam'


class _Prop_large_32_bit_icon(aetools.NProperty):
    which = 'il32'
    want = 'il32'


class _Prop_large_4_bit_icon(aetools.NProperty):
    which = 'icl4'
    want = 'icl4'


class _Prop_large_8_bit_icon(aetools.NProperty):
    which = 'icl8'
    want = 'icl8'


class _Prop_large_8_bit_mask(aetools.NProperty):
    which = 'l8mk'
    want = 'l8mk'


class _Prop_large_monochrome_icon_and_mask(aetools.NProperty):
    which = 'ICN#'
    want = 'ICN#'


class _Prop_small_32_bit_icon(aetools.NProperty):
    which = 'is32'
    want = 'is32'


class _Prop_small_4_bit_icon(aetools.NProperty):
    which = 'ics4'
    want = 'ics4'


class _Prop_small_8_bit_icon(aetools.NProperty):
    which = 'ics8'
    want = 'ics8'


_Prop_small_8_bit_mask = _Prop_small_8_bit_icon

class _Prop_small_monochrome_icon_and_mask(aetools.NProperty):
    which = 'ics#'
    want = 'ics#'


class column(aetools.ComponentItem):
    want = 'lvcl'


class _Prop_sort_direction(aetools.NProperty):
    which = 'sord'
    want = 'sodr'


class _Prop_visible(aetools.NProperty):
    which = 'pvis'
    want = 'bool'


class _Prop_width(aetools.NProperty):
    which = 'clwd'
    want = 'shor'


columns = column

class list_view_options(aetools.ComponentItem):
    want = 'lvop'


class _Prop_sort_column(aetools.NProperty):
    which = 'srtc'
    want = 'lvcl'


alias_list._superclassnames = []
alias_list._privpropdict = {}
alias_list._privelemdict = {}
label._superclassnames = []
label._privpropdict = {'color': _Prop_color,
 'index': _Prop_index,
 'name': _Prop_name}
label._privelemdict = {}
preferences._superclassnames = []
preferences._privpropdict = {'button_view_arrangement': _Prop_button_view_arrangement,
 'button_view_icon_size': _Prop_button_view_icon_size,
 'calculates_folder_sizes': _Prop_calculates_folder_sizes,
 'delay_before_springing': _Prop_delay_before_springing,
 'list_view_icon_size': _Prop_list_view_icon_size,
 'shows_comments': _Prop_shows_comments,
 'shows_creation_date': _Prop_shows_creation_date,
 'shows_kind': _Prop_shows_kind,
 'shows_label': _Prop_shows_label,
 'shows_modification_date': _Prop_shows_modification_date,
 'shows_size': _Prop_shows_size,
 'shows_version': _Prop_shows_version,
 'spatial_view_arrangement': _Prop_spatial_view_arrangement,
 'spatial_view_icon_size': _Prop_spatial_view_icon_size,
 'spring_open_folders': _Prop_spring_open_folders,
 'uses_relative_dates': _Prop_uses_relative_dates,
 'uses_simple_menus': _Prop_uses_simple_menus,
 'uses_wide_grid': _Prop_uses_wide_grid,
 'view_font': _Prop_view_font,
 'view_font_size': _Prop_view_font_size,
 'window': _Prop_window}
preferences._privelemdict = {'label': label}
icon_view_options._superclassnames = []
icon_view_options._privpropdict = {'arrangement': _Prop_arrangement,
 'icon_size': _Prop_icon_size}
icon_view_options._privelemdict = {}
icon_family._superclassnames = []
icon_family._privpropdict = {'large_32_bit_icon': _Prop_large_32_bit_icon,
 'large_4_bit_icon': _Prop_large_4_bit_icon,
 'large_8_bit_icon': _Prop_large_8_bit_icon,
 'large_8_bit_mask': _Prop_large_8_bit_mask,
 'large_monochrome_icon_and_mask': _Prop_large_monochrome_icon_and_mask,
 'small_32_bit_icon': _Prop_small_32_bit_icon,
 'small_4_bit_icon': _Prop_small_4_bit_icon,
 'small_8_bit_icon': _Prop_small_8_bit_icon,
 'small_8_bit_mask': _Prop_small_8_bit_mask,
 'small_monochrome_icon_and_mask': _Prop_small_monochrome_icon_and_mask}
icon_family._privelemdict = {}
column._superclassnames = []
column._privpropdict = {'index': _Prop_index,
 'name': _Prop_name,
 'sort_direction': _Prop_sort_direction,
 'visible': _Prop_visible,
 'width': _Prop_width}
column._privelemdict = {}
list_view_options._superclassnames = []
list_view_options._privpropdict = {'calculates_folder_sizes': _Prop_calculates_folder_sizes,
 'icon_size': _Prop_icon_size,
 'sort_column': _Prop_sort_column,
 'uses_relative_dates': _Prop_uses_relative_dates}
list_view_options._privelemdict = {'column': column}
_classdeclarations = {'alst': alias_list,
 'clbl': label,
 'cprf': preferences,
 'icop': icon_view_options,
 'ifam': icon_family,
 'lvcl': column,
 'lvop': list_view_options}
_propdeclarations = {'ICN#': _Prop_large_monochrome_icon_and_mask,
 'barr': _Prop_button_view_arrangement,
 'bisz': _Prop_button_view_icon_size,
 'clwd': _Prop_width,
 'colr': _Prop_color,
 'cwin': _Prop_window,
 'dela': _Prop_delay_before_springing,
 'iarr': _Prop_spatial_view_arrangement,
 'icl4': _Prop_large_4_bit_icon,
 'icl8': _Prop_large_8_bit_icon,
 'ics#': _Prop_small_monochrome_icon_and_mask,
 'ics4': _Prop_small_4_bit_icon,
 'ics8': _Prop_small_8_bit_icon,
 'iisz': _Prop_spatial_view_icon_size,
 'il32': _Prop_large_32_bit_icon,
 'is32': _Prop_small_32_bit_icon,
 'l8mk': _Prop_large_8_bit_mask,
 'lisz': _Prop_list_view_icon_size,
 'lvis': _Prop_icon_size,
 'pidx': _Prop_index,
 'pnam': _Prop_name,
 'pvis': _Prop_visible,
 'scda': _Prop_shows_creation_date,
 'scom': _Prop_shows_comments,
 'sdat': _Prop_shows_modification_date,
 'sfsz': _Prop_calculates_folder_sizes,
 'sknd': _Prop_shows_kind,
 'slbl': _Prop_shows_label,
 'sord': _Prop_sort_direction,
 'sprg': _Prop_spring_open_folders,
 'srtc': _Prop_sort_column,
 'ssiz': _Prop_shows_size,
 'svrs': _Prop_shows_version,
 'urdt': _Prop_uses_relative_dates,
 'usme': _Prop_uses_simple_menus,
 'uswg': _Prop_uses_wide_grid,
 'vfnt': _Prop_view_font,
 'vfsz': _Prop_view_font_size}
_compdeclarations = {}
_enumdeclarations = {}
