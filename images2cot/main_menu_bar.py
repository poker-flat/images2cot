PYGTKVERSION = "2.0"

try:
    import pygtk
    pygtk.require(PYGTKVERSION)
except:
    print "PyGTK version", PYGTKVERSION, "required."
    sys.exit(1)

try:
    import gtk
except:
    sys.exit(1)

import images2cot

class MainMenuBar:
    """
    asdf
    """

    def __init__(self, window):
        ad = images2cot.AboutDialog(window)

        ui = '''<ui>
    <menubar name="MenuBar">
        <menu action="FileMenu">
            <menuitem action="New" />
            <menuitem action="Open" />
            <menuitem action="Save" />
            <menuitem action="SaveAs" />
            <separator />
            <menuitem action="Quit" />
        </menu>
        <menu action="EditMenu">
            <menuitem action="Preferences" />
        </menu>
        <menu action="HelpMenu">
            <menuitem action="Help" />
            <menuitem action="About" />
        </menu>
    </menubar>
</ui>'''
        self.ui = ui
        self.window = window

        actions = [
            ('FileMenu', None, '_File'),
            ('New',  gtk.STOCK_NEW, '_New', '<Control>n',
                'New file', self.null),
            ('Open', gtk.STOCK_OPEN, '_Open', '<Control>o',
                'Open file', self.null),
            ('Save', gtk.STOCK_SAVE, '_Save', '<Control>s',
                'Save file', self.null),
            ('SaveAs', gtk.STOCK_SAVE_AS, 'Save _As', '<Control><Shift>s',
                'Save file as', self.null),
            ('Quit', gtk.STOCK_QUIT, '_Quit', '<Control>q',
                'Quit the Program', gtk.main_quit),
            ('EditMenu', None, '_Edit'),
            ('Preferences', gtk.STOCK_PREFERENCES, '_Preferences', None,
                'Edit preferences', self.null),
            ('HelpMenu', None, '_Help'),
            ('Help', gtk.STOCK_HELP, '_Help', 'F1',
                'Help me', self.null),
            ('About', gtk.STOCK_ABOUT, '_About', 'F12',
                'About images2cot', ad.show),
        ]
        self.actions = actions

        uimanager = gtk.UIManager()
        accelgroup = uimanager.get_accel_group()
        window.add_accel_group(accelgroup)

        actiongroup = gtk.ActionGroup('images2cot_main_actiongroup')
        self.actiongroup = actiongroup
        actiongroup.add_actions(actions)

        uimanager.insert_action_group(actiongroup, 0)
        uimanager.add_ui_from_string(ui)
        self.menu_bar = uimanager.get_widget('/MenuBar')

    def null(self, data=None):
        print data

    def get(self):
        return self.menu_bar
