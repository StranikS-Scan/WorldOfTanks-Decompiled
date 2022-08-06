# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/idle_test/htest.py
from importlib import import_module
from idlelib.macosxSupport import _initializeTkVariantTests
import Tkinter as tk
AboutDialog_spec = {'file': 'aboutDialog',
 'kwds': {'title': 'aboutDialog test',
          '_htest': True},
 'msg': 'Test every button. Ensure Python, TK and IDLE versions are correctly displayed.\n [Close] to exit.'}
_calltip_window_spec = {'file': 'CallTipWindow',
 'kwds': {},
 'msg': "Typing '(' should display a calltip.\nTyping ') should hide the calltip.\n"}
_class_browser_spec = {'file': 'ClassBrowser',
 'kwds': {},
 'msg': 'Inspect names of module, class(with superclass if applicable), methods and functions.\nToggle nested items.\nDouble clicking on items prints a traceback for an exception that is ignored.'}
_color_delegator_spec = {'file': 'ColorDelegator',
 'kwds': {},
 'msg': 'The text is sample Python code.\nEnsure components like comments, keywords, builtins,\nstring, definitions, and break are correctly colored.\nThe default color scheme is in idlelib/config-highlight.def'}
ConfigDialog_spec = {'file': 'configDialog',
 'kwds': {'title': 'ConfigDialogTest',
          '_htest': True},
 'msg': "IDLE preferences dialog.\nIn the 'Fonts/Tabs' tab, changing font face, should update the font face of the text in the area below it.\nIn the 'Highlighting' tab, try different color schemes. Clicking items in the sample program should update the choices above it.\nIn the 'Keys', 'General' and 'Extensions' tabs, test settings of interest.\n[Ok] to close the dialog.[Apply] to apply the settings and and [Cancel] to revert all changes.\nRe-run the test to ensure changes made have persisted."}
_dyn_option_menu_spec = {'file': 'dynOptionMenuWidget',
 'kwds': {},
 'msg': "Select one of the many options in the 'old option set'.\nClick the button to change the option set.\nSelect one of the many options in the 'new option set'."}
_editor_window_spec = {'file': 'EditorWindow',
 'kwds': {},
 'msg': 'Test editor functions of interest.\nBest to close editor first.'}
GetCfgSectionNameDialog_spec = {'file': 'configSectionNameDialog',
 'kwds': {'title': 'Get Name',
          'message': 'Enter something',
          'used_names': {'abc'},
          '_htest': True},
 'msg': "After the text entered with [Ok] is stripped, <nothing>, 'abc', or more that 30 chars are errors.\nClose 'Get Name' with a valid entry (printed to Shell), [Cancel], or [X]"}
GetHelpSourceDialog_spec = {'file': 'configHelpSourceEdit',
 'kwds': {'title': 'Get helpsource',
          '_htest': True},
 'msg': 'Enter menu item name and help file path\n <nothing> and more than 30 chars are invalid menu item names.\n<nothing>, file does not exist are invalid path items.\nTest for incomplete web address for help file path.\nA valid entry will be printed to shell with [0k].\n[Cancel] will print None to shell'}
GetKeysDialog_spec = {'file': 'keybindingDialog',
 'kwds': {'title': 'Test keybindings',
          'action': 'find-again',
          'currentKeySequences': [''],
          '_htest': True},
 'msg': 'Test for different key modifier sequences.\n<nothing> is invalid.\nNo modifier key is invalid.\nShift key with [a-z],[0-9], function key, move key, tab, space is invalid.\nNo validitity checking if advanced key binding entry is used.'}
_grep_dialog_spec = {'file': 'GrepDialog',
 'kwds': {},
 'msg': "Click the 'Show GrepDialog' button.\nTest the various 'Find-in-files' functions.\nThe results should be displayed in a new '*Output*' window.\n'Right-click'->'Goto file/line' anywhere in the search results should open that file \nin a new EditorWindow."}
_io_binding_spec = {'file': 'IOBinding',
 'kwds': {},
 'msg': 'Test the following bindings.\n<Control-o> to open file from dialog.\nEdit the file.\n<Control-p> to print the file.\n<Control-s> to save the file.\n<Alt-s> to save-as another file.\n<Control-c> to save-copy-as another file.\nCheck that changes were saved by opening the file elsewhere.'}
_multi_call_spec = {'file': 'MultiCall',
 'kwds': {},
 'msg': 'The following actions should trigger a print to console or IDLE Shell.\nEntering and leaving the text area, key entry, <Control-Key>,\n<Alt-Key-a>, <Control-Key-a>, <Alt-Control-Key-a>, \n<Control-Button-1>, <Alt-Button-1> and focusing out of the window\nare sequences to be tested.'}
_multistatus_bar_spec = {'file': 'MultiStatusBar',
 'kwds': {},
 'msg': "Ensure presence of multi-status bar below text area.\nClick 'Update Status' to change the multi-status text"}
_object_browser_spec = {'file': 'ObjectBrowser',
 'kwds': {},
 'msg': 'Double click on items upto the lowest level.\nAttributes of the objects and related information will be displayed side-by-side at each level.'}
_path_browser_spec = {'file': 'PathBrowser',
 'kwds': {},
 'msg': 'Test for correct display of all paths in sys.path.\nToggle nested items upto the lowest level.\nDouble clicking on an item prints a traceback\nfor an exception that is ignored.'}
_percolator_spec = {'file': 'Percolator',
 'kwds': {},
 'msg': "There are two tracers which can be toggled using a checkbox.\nToggling a tracer 'on' by checking it should print tracer output to the console or to the IDLE shell.\nIf both the tracers are 'on', the output from the tracer which was switched 'on' later, should be printed first\nTest for actions like text entry, and removal."}
_replace_dialog_spec = {'file': 'ReplaceDialog',
 'kwds': {},
 'msg': "Click the 'Replace' button.\nTest various replace options in the 'Replace dialog'.\nClick [Close] or [X] to close the 'Replace Dialog'."}
_search_dialog_spec = {'file': 'SearchDialog',
 'kwds': {},
 'msg': "Click the 'Search' button.\nTest various search options in the 'Search dialog'.\nClick [Close] or [X] to close the 'Search Dialog'."}
_scrolled_list_spec = {'file': 'ScrolledList',
 'kwds': {},
 'msg': 'You should see a scrollable list of items\nSelecting (clicking) or double clicking an item prints the name to the console or Idle shell.\nRight clicking an item will display a popup.'}
show_idlehelp_spec = {'file': 'help',
 'kwds': {},
 'msg': 'If the help text displays, this works.\nText is selectable. Window is scrollable.'}
_stack_viewer_spec = {'file': 'StackViewer',
 'kwds': {},
 'msg': "A stacktrace for a NameError exception.\nExpand 'idlelib ...' and '<locals>'.\nCheck that exc_value, exc_tb, and exc_type are correct.\n"}
_tabbed_pages_spec = {'file': 'tabbedpages',
 'kwds': {},
 'msg': "Toggle between the two tabs 'foo' and 'bar'\nAdd a tab by entering a suitable name for it.\nRemove an existing tab by entering its name.\nRemove all existing tabs.\n<nothing> is an invalid add page and remove page name.\n"}
TextViewer_spec = {'file': 'textView',
 'kwds': {'title': 'Test textView',
          'text': 'The quick brown fox jumps over the lazy dog.\n' * 35,
          '_htest': True},
 'msg': 'Test for read-only property of text.\nText is selectable. Window is scrollable.'}
_tooltip_spec = {'file': 'ToolTip',
 'kwds': {},
 'msg': 'Place mouse cursor over both the buttons\nA tooltip should appear with some text.'}
_tree_widget_spec = {'file': 'TreeWidget',
 'kwds': {},
 'msg': 'The canvas is scrollable.\nClick on folders upto to the lowest level.'}
_undo_delegator_spec = {'file': 'UndoDelegator',
 'kwds': {},
 'msg': 'Click [Undo] to undo any action.\nClick [Redo] to redo any action.\nClick [Dump] to dump the current state by printing to the console or the IDLE shell.\n'}
_widget_redirector_spec = {'file': 'WidgetRedirector',
 'kwds': {},
 'msg': 'Every text insert should be printed to the console or the IDLE shell.'}

def run(*tests):
    root = tk.Tk()
    root.title('IDLE htest')
    root.resizable(0, 0)
    _initializeTkVariantTests(root)
    frameLabel = tk.Frame(root, padx=10)
    frameLabel.pack()
    text = tk.Text(frameLabel, wrap='word')
    text.configure(bg=root.cget('bg'), relief='flat', height=4, width=70)
    scrollbar = tk.Scrollbar(frameLabel, command=text.yview)
    text.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y', expand=False)
    text.pack(side='left', fill='both', expand=True)
    test_list = []
    if tests:
        for test in tests:
            test_spec = globals()[test.__name__ + '_spec']
            test_spec['name'] = test.__name__
            test_list.append((test_spec, test))

    else:
        for k, d in globals().items():
            if k.endswith('_spec'):
                test_name = k[:-5]
                test_spec = d
                test_spec['name'] = test_name
                mod = import_module('idlelib.' + test_spec['file'])
                test = getattr(mod, test_name)
                test_list.append((test_spec, test))

    test_name = [tk.StringVar('')]
    callable_object = [None]
    test_kwds = [None]

    def next():
        if len(test_list) == 1:
            next_button.pack_forget()
        test_spec, callable_object[0] = test_list.pop()
        test_kwds[0] = test_spec['kwds']
        test_kwds[0]['parent'] = root
        test_name[0].set('Test ' + test_spec['name'])
        text.configure(state='normal')
        text.delete('1.0', 'end')
        text.insert('1.0', test_spec['msg'])
        text.configure(state='disabled')

    def run_test():
        widget = callable_object[0](**test_kwds[0])
        try:
            print widget.result
        except AttributeError:
            pass

    button = tk.Button(root, textvariable=test_name[0], command=run_test)
    button.pack()
    next_button = tk.Button(root, text='Next', command=next)
    next_button.pack()
    next()
    root.mainloop()
    return


if __name__ == '__main__':
    run()
