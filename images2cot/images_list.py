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

import commands, gc

class ImagesList:

    listview = None
    liststore = None

    frm_img_prev = None

    def __init__(self, parent):
        liststore = gtk.ListStore(str, str, int, str, int, str)

        listview = gtk.TreeView(liststore)

        lvcol = gtk.TreeViewColumn('_Name')
        cell = gtk.CellRendererText()
        lvcol.pack_start(cell, True)
        lvcol.add_attribute(cell, 'text', 1)
        lvcol.set_sort_column_id(0)
        lvcol.set_reorderable(True)
        lvcol.set_resizable(True)
        listview.append_column(lvcol)

        lvcol = gtk.TreeViewColumn('S_ize')
        cell = gtk.CellRendererText()
        lvcol.pack_start(cell, True)
        lvcol.add_attribute(cell, 'text', 3)
        lvcol.set_sort_column_id(2)
        lvcol.set_reorderable(True)
        lvcol.set_resizable(True)
        listview.append_column(lvcol)

        lvcol = gtk.TreeViewColumn('Da_te Modified')
        cell = gtk.CellRendererText()
        lvcol.pack_start(cell, True)
        lvcol.add_attribute(cell, 'text', 5)
        lvcol.set_sort_column_id(4)
        lvcol.set_reorderable(True)
        lvcol.set_resizable(True)
        listview.append_column(lvcol)

        listview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        listview.connect('cursor-changed', self.select_cursor_row)

        self.listview = listview
        self.liststore = liststore

        self.current_image_selection = None

        self.parent = parent

        self.liststore.exif_dict = {}
        self.liststore.info_dict = {}

    def get(self):
        return self.listview

    def select_cursor_row(self, listview):
        """
        asdf

        @known_bugs  Multiple selections in this list generate not so good data
                     as to which rows are actually selected. If the user
                     selects rows one at a time, there is no problem.
        """

        selection_widget = listview.get_selection()

        data = selection_widget.get_selected_rows()
        liststore = data[0]
        path = data[1]
        
        path = path[0][0]

        # Grab the TreeModel so we can work with the data
        liststore = listview.get_model()
   
        # Grab the element in the TreeModel located by path
        iter = liststore.get_iter(path)
   
        imagepath = liststore.get_value(iter, 0)
   
        if imagepath == self.current_image_selection:
            # The selection did not change
            return
        else:
            self.current_image_selection = imagepath
            #print imagepath

            if self.parent.frm_img_prev:
                img = self.parent.frm_img_prev.get_child()
                self.parent.frm_img_prev.remove(img)

                del img
                gc.collect()
                
                img = gtk.Image()
                try:
                    img.set_from_pixbuf(
                        gtk.gdk.pixbuf_new_from_file(
                            imagepath
                        ).scale_simple(150,150,gtk.gdk.INTERP_BILINEAR)
                    )
                except:
                    img.set_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_DIALOG)
                img.show()

                self.parent.frm_img_prev.add(img)

            if self.parent.frm_exif:
                text_view = self.parent.frm_exif.get_child().get_child()
                
                buf = text_view.get_buffer()

                if liststore.exif_dict.has_key(imagepath):
                    buf.set_text(liststore.exif_dict[imagepath])
                else:
                    print 'liststore.exif_dict has not key. Error.'
                    buf.set_text('Error.')

            if self.parent.frm_img_info:
                text_info = self.parent.frm_img_info.get_child().get_child()

                buf = text_info.get_buffer()

                if liststore.info_dict.has_key(imagepath):
                    buf.set_text(liststore.info_dict[imagepath])
                else:
                    print 'liststore.info_dict has not key. Error.'
                    buf.set_text('Error.')
