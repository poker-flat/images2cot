import os, datetime, commands

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

class I2cButtons:
    def __init__(self):
        pass

    def get_btn_quit(self):
        """
        asdf
        """
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_BUTTON)
        btn_quit = gtk.Button("_Quit")
        btn_quit.set_image(img)
        btn_quit.show()

        btn_quit.connect("clicked", gtk.main_quit)

        return btn_quit

    def get_btn_save(self, listview=None, entry=None):
        """
        asdf
        """
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_SAVE, gtk.ICON_SIZE_BUTTON)
        btn_save = gtk.Button("_Save XML File...")
        btn_save.set_image(img)
        btn_save.show()

        btn_save.connect('clicked', self.btn_save_clicked, listview, entry)

        return btn_save

    def btn_save_clicked(self, widget=None, listview=None, entry=None):
        if entry:
            path = entry.get_text()

            if entry.get_text:
                import os

                fhandle = open(path, 'w')

                if not fhandle:
                    return False

        if listview:
            liststore = listview.get_model()

            iter = liststore.get_iter_first()

            txt = '' 

            while iter:
                imagepath = liststore.get_value(iter, 0)
                
                iter = liststore.iter_next(iter)

                raw = liststore.exif_dict[imagepath]

                if raw != 'Error.' and raw:
                    parser = images2cot.JheadParser()
                    parser.parse_block(raw)

                    parsed = parser.write_xml(file=False)

                    if parsed:
                        txt = txt + parsed

            fhandle.write(txt)

            fhandle.close()

    def get_btn_preview(self, listview=None):
        """
        asdf
        """
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_PRINT_PREVIEW, gtk.ICON_SIZE_BUTTON)
        btn_preview = gtk.Button("P_review XML File...")
        btn_preview.set_image(img)
        btn_preview.show()

        btn_preview.connect('clicked', self.btn_preview_clicked, listview)

        return btn_preview

    def btn_preview_clicked(self, widget=None, listview=None):
        if listview:
            liststore = listview.get_model()

            iter = liststore.get_iter_first()

            txt = '' 

            while iter:
                imagepath = liststore.get_value(iter, 0)
                
                iter = liststore.iter_next(iter)

                raw = liststore.exif_dict[imagepath]

                if raw != 'Error.' and raw:
                    parser = images2cot.JheadParser()
                    parser.parse_block(raw)

                    parsed = parser.write_xml(file=False)

                    if parsed:
                        txt = txt + parsed

            new_window = images2cot.TextWindow("XML Preview", txt)

    def get_btn_browse(self):
        """
        asdf
        """
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_BUTTON)
        btn_browse = gtk.Button('_Browse...')
        btn_browse.set_image(img)
        btn_browse.show()

        btn_browse.connect('clicked', self.btn_browse_clicked)

        return btn_browse

    def btn_browse_clicked(self, widget=None):
        print 'btn_browse_clicked'

    def get_btn_remove(self, list=None, i2c=None):
        """
        asdf
        """
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_BUTTON)
        btn_remove = gtk.Button('Remo_ve Selected')
        btn_remove.set_image(img)
        btn_remove.show()

        btn_remove.connect('clicked', self.btn_remove_clicked, list, i2c)

        return btn_remove

    def btn_remove_clicked(self, widget=None, list=None, i2c=None):
        """
        This function is called when the 'Remove' button is clicked. The
        action sends a gtk.ListView object as a parameter.

        Iterate over the selected data and remove their entries from the
        ListStore.
        """

        selection_widget = list.get_selection()

        data = selection_widget.get_selected_rows()
        liststore = data[0]
        remove = data[1]

        # We want to remove the entries from the botton up because the 'path'
        # gets updated per every addition/deletion.
        remove.reverse()

        for item in remove:
            # Grab the TreeIter object from the list store pointed at by
            # item[0] (item[0] is the 'path', which is just an integer)
            iter = liststore.get_iter(item[0])

            # Remove the item from the list pointed at by `iter'.
            liststore.remove(iter)

    def get_btn_add(self, list=None):
        """
        asdf
        """
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)
        btn_add = gtk.Button('_Add Image(s)')
        btn_add.set_image(img)
        btn_add.show()

        btn_add.connect('clicked', self.btn_add_clicked, list)

        return btn_add

    def btn_add_clicked(self, widget=None, list=None):
        """
        asdf
        """

        # Open up a file chooser dialog
        dialog = gtk.FileChooserDialog("Add images to list...",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                       gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        # Allow multiple selection
        dialog.set_select_multiple(True)

        # Creat a file filter for our default file mask, jpeg files
        filter = gtk.FileFilter()
        filter.set_name("JPEG Images")
        filter.add_mime_type("image/jpeg")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.Jpeg")
        dialog.add_filter(filter)

        # All files
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)

        # Run the dialog
        response = dialog.run()
        files = []

        # Grab our response
        if response == gtk.RESPONSE_OK:
            files = dialog.get_filenames()
        elif response == gtk.RESPONSE_CANCEL:
            pass

        # Once the response is grabbed, destroy the window
        dialog.destroy()

        # Grab the TreeModel so we can work with the data
        liststore = list.get_model()

        list.set_model(None)

        # Grab the first element in the TreeModel
        iter = liststore.get_iter_first()

        # Each time iter is initialized, it points to a valid row in the
        # TreeModel. Each row has data we need to check against. In this case,
        # column 1 contains the image path. We are preventing the same image
        # from being inserted into the list twice.
        while iter:
            # The actual data
            imagepath = liststore.get_value(iter, 0)

            # We don't first check then remove because then that would mean we
            # were searching the list twice. Just go ahead and try to remove.
            try:
                files.remove(imagepath)
            except:
                pass

            # Grab next row. If no row, None is returned
            iter = liststore.iter_next(iter)

        # After the list has been trimmed (or not), append each element in the
        # files list to the ListStore (TreeStore, technically)
        for file in files:
            name = os.path.basename(file)
            size = os.path.getsize(file)
            oldsize = int(size)

            res = 0
            while 1:
                newsize = size/1000.0
                if newsize > 1:
                    size = newsize
                    res+=1
                else:
                    break

            suffix = " B"
            if res == 1:
                suffix = " KB"
            elif res == 2:
                suffix = " MB"
            elif res == 3:
                suffix = " GB"
            elif res == 4:
                suffix = " TB"
            elif res == 5:
                suffix = " PB"
            else:
                suffix = " ?"

            date_mod = os.stat(file).st_mtime
            t = datetime.datetime.fromtimestamp(date_mod).timetuple()
            date_view = "%s-%s-%s %s:%s:%s" % \
                        (t[0], t[1], t[2], t[3], t[4], t[5])
            liststore.append([file,
                              name,
                              oldsize,
                              str(str("%.2f" % round(size,2)) + suffix),
                              date_mod,
                              date_view
                              ])
            
            if not liststore.exif_dict.has_key(file):
                status, output = commands.getstatusoutput("jhead -v %s" % file)

                if status == 0:
                    # exif dict
                    liststore.exif_dict[file] = output

                    # info dict
                    parser = images2cot.JheadParser()
                    parser.parse_block(liststore.exif_dict[file])

                    info = """Filename: %s

GPS Info
=============
GPS Latitude: %s
GPS Longitude: %s
GPS Altitude: %s
GPS Date and Time: %s %s

Misc
=============
Camera Make: %s
Camera Model: %s
Exposure Time: %s""" % (parser.Filename,
                        parser.GPSLatitude,
                        parser.GPSLongitude,
                        parser.GPSAltitude,
                        parser.GPSDateStamp, parser.GPSTimeStamp,
                        
                        parser.CameraMake,
                        parser.CameraModel,
                        parser.ExposureTime,
                        )
                    liststore.info_dict[file] = info
 
                else:
                    liststore.exif_dict[file] = 'Error.'
                    liststore.info_dict[file] = 'Error.'

            list.set_model(liststore)
