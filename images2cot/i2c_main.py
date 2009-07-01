import os

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

class I2cMain:
    """
    This is the images2cot program.
    """

    #
    # Class variables
    #
    window = None
    vbox1 = None

    #
    # Constructor
    #
    def __init__(self):
        # main window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("images2cot")
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy_event", self.destroy_event)
        self.window.set_size_request(800, 600)

        # vertical box
        self.vbox = gtk.VBox(False, 0)
        self.window.add(self.vbox)

        # menu bar
        mb = images2cot.MainMenuBar(self.window)
        self.menu_bar = mb.get()
        self.vbox.pack_start(self.menu_bar, False, False, 2)

        # horizontal pane, left side and right side
        self.hp1 = gtk.HPaned()
        self.hp1.set_position(400)
        self.vbox.pack_start(self.hp1, True, True, 2)

        # left child of horizontal pane, frame
        frame = gtk.Frame('Images')
        frame.set_shadow_type(gtk.SHADOW_OUT)
        frame.show()
        self.frm_images = frame
        self.hp1.add1(frame)

        # vbox in frm_images
        self.vbox_images = gtk.VBox()
        self.frm_images.add(self.vbox_images)
        self.vbox_images.show()

        # scroll window for list view
        self.scroll_images = gtk.ScrolledWindow()
        self.scroll_images.set_border_width(10)
        self.scroll_images.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.scroll_images.show()
        self.vbox_images.pack_start(self.scroll_images, True, True, 2)

        # list view for images
        self.lst_images = images2cot.ImagesList(self)
        self.lst_images = self.lst_images.get()
        self.lst_images.show_all()
        self.scroll_images.add_with_viewport(self.lst_images)

        # button list in the images frame
        self.bbox_images = gtk.HButtonBox()

        buttons = images2cot.I2cButtons()
        self.btn_add = buttons.get_btn_add(self.lst_images)
        self.btn_remove = buttons.get_btn_remove(self.lst_images)

        self.bbox_images.pack_start(self.btn_add, False, False, 2)
        self.bbox_images.pack_start(self.btn_remove, False, False, 2)
        self.bbox_images.show()
        self.vbox_images.pack_end(self.bbox_images, False, False, 2)
        self.frm_images.show_all()

        # right child of horizontal pane, frame
        frame = gtk.Frame('Exif Info')
        frame.set_shadow_type(gtk.SHADOW_OUT)
        frame.show()
        self.frm_exif = frame
        self.hp1.add2(frame)

        # scroll window for image info
        self.scroll_exif_info = gtk.ScrolledWindow()
        self.scroll_exif_info.set_border_width(5)
        self.scroll_exif_info.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.scroll_exif_info.show()

        self.frm_exif.add(self.scroll_exif_info)

        # text view for image info frame
        txt_info = gtk.TextView()
        txt_info.set_editable(False)
        self.scroll_exif_info.add(txt_info)
        txt_info.show()

        # horizontal pane, left side and right side
        self.hp2 = gtk.HPaned()
        self.hp2.set_position(400)
        self.vbox.pack_start(self.hp2, True, True, 2)

        # left child of horizontal pane
        frame = gtk.Frame('Image Preview')
        frame.set_shadow_type(gtk.SHADOW_OUT)
        frame.show()
        self.frm_img_prev = frame
        self.lst_images.frm_img_prev = frame
        self.hp2.add1(frame)

        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG)
        img.show()

        frame.add(img)

        # right child of horizontal pane, frame
        frame = gtk.Frame('Image Info')
        frame.set_shadow_type(gtk.SHADOW_OUT)
        frame.show()
        self.frm_img_info = frame
        self.hp2.add2(frame)

        self.scrl_info = gtk.ScrolledWindow()
        self.scrl_info.set_border_width(5)
        self.scrl_info.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.frm_img_info.add(self.scrl_info)

        self.txt_img_info = gtk.TextView()
        self.txt_img_info.set_editable(False)
        self.scrl_info.add(self.txt_img_info)

        self.scrl_info.show()
        self.txt_img_info.show()

        # horizontal box
        self.hbox = gtk.HBox(False, 0)
        self.vbox.pack_start(self.hbox, False, False, 20)

        # label: Destination
        label = gtk.Label('Destination:')
        label.show()
        self.hbox.pack_start(label, False, False, 10)

        # text entry box: Path
        self.entry = gtk.Entry()
        self.entry.set_text(os.getcwd() + '/xml_file.xml')
        self.hbox.pack_start(self.entry, True, True, 10)

        # Browse dialog button
        self.btn_browse = buttons.get_btn_browse()
        self.hbox.pack_start(self.btn_browse, False, False, 10)

        # Button box
        self.bbox = gtk.HButtonBox()
        self.bbox.set_layout(gtk.BUTTONBOX_END)
        self.bbox.set_spacing(5)
        #
        self.btn_preview = buttons.get_btn_preview()
        self.bbox.add(self.btn_preview)
        #
        self.btn_save = buttons.get_btn_save()
        self.bbox.add(self.btn_save)
        #
        self.btn_quit = buttons.get_btn_quit()
        self.bbox.add(self.btn_quit)
        #
        self.vbox.pack_start(self.bbox, False, False, 10)

        # status bar
        self.status = gtk.Statusbar()
        self.vbox.pack_start(self.status, False, False, 2)

        # Show
        self.status.show()
        self.bbox.show()
        self.entry.show()
        self.hbox.show()
        self.hp2.show()
        self.hp1.show()
        self.menu_bar.show()
        self.vbox.show()
        self.window.show()

    def main(self):
        gtk.main()

    def destroy_event(self, widget, event=None, data=None):
        print "Destroy event..."
        gtk.main_quit()
        return False

    def delete_event(self, widget=None, event=None, data=None):
        print "Delete event..."
        gtk.main_quit()
        return False
