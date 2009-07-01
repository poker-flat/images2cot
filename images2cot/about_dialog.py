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

class AboutDialog:
    """
    The about dialog from the main Help menu in the Menu Bar.
    """

    name = 'images2cot'
    version = '1.2.3.4'
    copyright = 'Copyright (C) 2009, Geographic Information Network of Alaska,\
 University of Alaska Fairbanks'
    comments = 'my comments'
    license = 'MIT License'
    website = 'http://gina.alaska.edu/'
    authors = [ ('Jonathan Sawyer') ]
    documenters = [ ('Jonathan Sawyer') ]

    def __init__(self, window):
        # init
        about = gtk.AboutDialog()

        # set attribs
        about.set_name(self.name)
        about.set_version('v%s' % self.version)
        about.set_copyright(self.copyright)
        about.set_comments(self.comments)
        about.set_license(self.license)
        about.set_website(self.website)
        about.set_authors(self.authors)
        about.set_documenters(self.documenters)

        about.set_modal(True)
        about.set_transient_for(window)

        # fin
        self.about = about

    def show(self, widget=None):
        # Dialog response constants:
        # gtk.RESPONSE_CLOSE,  gtk.RESPONSE_NONE,   gtk.RESPONSE_DELETE_EVENT
        # gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK,     gtk.RESPONSE_CLOSE
        # gtk.RESPONSE_HELP,   gtk.RESPONSE_REJECT, gtk.RESPONSE_ACCEPT

        response = self.about.run()

        if response == gtk.RESPONSE_CANCEL:
            self.about.hide()
            return True
        else:
            return False
