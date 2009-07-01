#!/usr/bin/env python2.5
import sys
import types
import traceback
import marshal
import pygtk
import hildon
pygtk.require('2.0')
import gobject
import gtk
import pango


#######################    RESOURCES    #######################


### A 24x24 left-arrow icon that's different from the standard arrow.
### This icon is meant to imply "decrease value", but not necessarily
### "subtract value" as a minus-icon would imply.
_leftArrow = [
"24 24 3 1",
"A s bg c None",
"B c #777777777777",
"C c #000000000000",
"AAAAAAAAAAAAAAAAAAAAAAAB",
"AAAAAAAAAAAAAAAAAAAAABCB",
"AAAAAAAAAAAAAAAAAAABCCCA",
"AAAAAAAAAAAAAAAAABCCCCBA",
"AAAAAAAAAAAAAAABCCCCCCAA",
"AAAAAAAAAAAAABCCCCCCCBAA",
"AAAAAAAAAAABCCCCCCCCCAAA",
"AAAAAAAAABCCCCCCCCCCBAAA",
"AAAAAAABCCCCCCCCCCCCAAAA",
"AAAAABCCCCCCCCCCCCCBAAAA",
"AAABCCCCCCCCCCCCCCCAAAAA",
"ABCCCCCCCCCCCCCCCCBAAAAA",
"ABCCCCCCCCCCCCCCCCBAAAAA",
"AAABCCCCCCCCCCCCCCCAAAAA",
"AAAAABCCCCCCCCCCCCCBAAAA",
"AAAAAAABCCCCCCCCCCCCAAAA",
"AAAAAAAAABCCCCCCCCCCBAAA",
"AAAAAAAAAAABCCCCCCCCCAAA",
"AAAAAAAAAAAAABCCCCCCCBAA",
"AAAAAAAAAAAAAAABCCCCCCAA",
"AAAAAAAAAAAAAAAAABCCCCBA",
"AAAAAAAAAAAAAAAAAAABCCCA",
"AAAAAAAAAAAAAAAAAAAAABCB",
"AAAAAAAAAAAAAAAAAAAAAAAB"]



### A 24x24 right-arrow icon that's different from the standard arrow.
### This icon is meant to imply "increase value", but not necessarily
### "add value" as a plus-icon would imply.
_rightArrow = [
"24 24 3 1",
"A s bg c None",
"B c #777777777777",
"C c #000000000000",
"BAAAAAAAAAAAAAAAAAAAAAAA",
"BCBAAAAAAAAAAAAAAAAAAAAA",
"ACCCBAAAAAAAAAAAAAAAAAAA",
"ABCCCCBAAAAAAAAAAAAAAAAA",
"AACCCCCCBAAAAAAAAAAAAAAA",
"AABCCCCCCCBAAAAAAAAAAAAA",
"AAACCCCCCCCCBAAAAAAAAAAA",
"AAABCCCCCCCCCCBAAAAAAAAA",
"AAAACCCCCCCCCCCCBAAAAAAA",
"AAAABCCCCCCCCCCCCCBAAAAA",
"AAAAACCCCCCCCCCCCCCCBAAA",
"AAAAABCCCCCCCCCCCCCCCCBA",
"AAAAABCCCCCCCCCCCCCCCCBA",
"AAAAACCCCCCCCCCCCCCCBAAA",
"AAAABCCCCCCCCCCCCCBAAAAA",
"AAAACCCCCCCCCCCCBAAAAAAA",
"AAABCCCCCCCCCCBAAAAAAAAA",
"AAACCCCCCCCCBAAAAAAAAAAA",
"AABCCCCCCCBAAAAAAAAAAAAA",
"AACCCCCCBAAAAAAAAAAAAAAA",
"ABCCCCBAAAAAAAAAAAAAAAAA",
"ACCCBAAAAAAAAAAAAAAAAAAA",
"BCBAAAAAAAAAAAAAAAAAAAAA",
"BAAAAAAAAAAAAAAAAAAAAAAA"]



### A 24x24 "reset" icon.  This icon is meant to imply "reset value".
_bellyButton = [
"24 24 6 1",
"A s bg c None",
"B c #AAAAAAAAAAAA",
"C c #777777777777",
"D c #666666666666",
"E c #333333333333",
"F c #000000000000",
"AAAAAAAAAAAAAAAAAAAAAAAA",
"AAAAAAAAAAAAAAAAAAAAAAAA",
"AAAAAAAADCFFFFCDAAAAAAAA",
"AAAAAABFFFFFFFFFFBAAAAAA",
"AAAAAEFFFFFFFFFFFFEAAAAA",
"AAAAEFFFFFFFFFFFFFFEAAAA",
"AAABFFFFFFFFFFFFFFFFBAAA",
"AAAFFFFFFFFFFFFFFFFFFAAA",
"AADFFFFFFFFFFFFFFFFFFDAA",
"AACFFFFFFFFFFFFFFFFFFCAA",
"AAFFFFFFFFFFFFFFFFFFFFAA",
"AAFFFFFFFFFFFFFFFFFFFFAA",
"AAFFFFFFFFFFFFFFFFFFFFAA",
"AAFFFFFFFFFFFFFFFFFFFFAA",
"AACFFFFFFFFFFFFFFFFFFCAA",
"AADFFFFFFFFFFFFFFFFFFDAA",
"AAAFFFFFFFFFFFFFFFFFFAAA",
"AAABFFFFFFFFFFFFFFFFBAAA",
"AAAAEFFFFFFFFFFFFFFEAAAA",
"AAAAAEFFFFFFFFFFFFEAAAAA",
"AAAAAABFFFFFFFFFFBAAAAAA",
"AAAAAAAADCFFFFCDAAAAAAAA",
"AAAAAAAAAAAAAAAAAAAAAAAA",
"AAAAAAAAAAAAAAAAAAAAAAAA"]




#######################    STYLE FIXES    #######################

# 1. Nokia stupidly removed expander triangles, making it impossible to tell the difference
#    between a leaf node and an unexpanded nonleaf node.  I add them back in.
# 2. Sliders are not particularly thick in the standard Nokia style.  
#    It appears 22 is the maximum slider width given the bitmaps.
#    Note that there are style bugs in Sliders in some styles -- the bitmaps for the thumbs
#    are shifted one pixel down incorrectly.
# 3. Pane handles are not particularly thick either.  Sadly they cannot be thickened much.
#    And thickening them like I'm doing creates two bitmap pictures next to each other; not
#    terrible looking, but perhaps confusing.  Sure is a lot easier to hit tho.

gtk.rc_parse_string('''style "ToolkitGTKTreeView"
{
        GtkTreeView::expander-size = 14
}

class "GtkTreeView" style "ToolkitGTKTreeView"

style "ToolkitScale"
{
    GtkRange::slider-width = 22
}

class "GtkRange" style "ToolkitScale"


style "ToolkitPaned"
{
    GtkPaned::handle-size = 20
}

class "GtkPaned" style "ToolkitPaned"
''')






#######################    PROGRAM INITIALIZATION    #######################


### We begin by firing up a hildon application.  Why this isn't done
### for you in pygtk I will never know.
_hildonApplication = hildon.Program()

def getHildonApplication():
    """Returns the hildon.Program used by the toolkit"""
    return _hildonApplication

# My version numbers tend to be single integers.  Yes, I'm eccentric.  :-)
_version = 0

def getVersion():
    """Returns the toolkit's version"""
    global _version
    return _version

_verbose = False
def setVerbose(val=True):
    """Prints verbose errors"""
    global _verbose
    _verbose = val


def handleError(error):
    "Prints the error if verbose is true"
    global _verbose
    if _verbose:
        traceback.print_exc(file=sys.stdout)


def _print(thing):
    "Print the thing"
    print "%s" % thing






#######################    PERSISTENCE SYSTEM    #######################

## Global persistence data and filename
_persistenceData = { }
_persistenceFilename = None



def loadPersistenceData(filename):
    """Loads persistence data from a file at the given filename.  If there is no such file, then no persistence data is loaded and this function will fail silently.  The data is stored in a global variable, and so is the filename (even if no data is loaded).  These global variables are used by save_persistanceData() to write out the data the same file.

Persistence data is state data provided by widgets so that, on next execution of the program, the widgets will set themselves up in the same state as before.  For example, a split pane's divider bar might store where the user last moved it, so it stays there across application executions.  Widgets store this information by providing a name (a string), which is stored with the information as its value.  The data is thus a simple dictionary of the form {name:val, name:val, ...}.  The vals may be anything.  The persistence data file format is the binary representation of this dictionary as saved out using the marshal.dump(...) function."""
    global _persistenceData
    global _persistenceFilename
    global _verbose
    persistenceData = { }
    f = None
    try:
        _persistenceFilename = filename
        f = open(_persistenceFilename, mode='rb')
        _persistenceData = marshal.load(f)
    except IOError, error: handleError(error)
    except EOFError, error: handleError(error)
    try:
        if (f!=None): f.close()
    except Exception, error: handleError(error)
    if _verbose:
        for k, v in _persistenceData.items():
            print "Loaded: ", k, "=", v




def savePersistenceData():
    """Saves the current persistence data (a private global) to the filename previously given to loadPersistenceData(...) (another private global).  If there is a file error, this function will fail silently.

Persistence data is state data provided by widgets so that, on next execution of the program, the widgets will set themselves up in the same state as before.  For example, a split pane's divider bar might store where the user last moved it, so it stays there across application executions.  Widgets store this information by providing a name (a string), which is stored with the information as its value.  The data is thus a simple dictionary of the form {name:val, name:val, ...}.  The vals may be anything.  The persistence data file format is the binary representation of this dictionary as saved out using the marshal.dump(...) function."""
    
    global _persistenceData
    global _persistenceFilename
    global _verbose
    if _verbose:
        for k, v in _persistenceData.items():
            print "Saving: ", k, "=", v
    f = None
    if (_persistenceFilename != None):
        try:
            f = open(_persistenceFilename, mode='wb')
            marshal.dump(_persistenceData, f)
            if _verbose: print "Saved"
        except IOError, error: handleError(error)
        except EOFError, error: handleError(error)
    try:
        if (f!=None): f.close()
    except Exception, error: handleError(error)


# Used internally by getPersistenceData
def _compatableType(subtype, supertype):
    if (supertype == type(None)): return True
    elif (subtype == bool and supertype == bool): return True
    elif (subtype == types.IntType and (supertype == types.IntType or supertype == types.FloatType)): return True
    elif (subtype == types.FloatType and (supertype == types.IntType or supertype == types.FloatType)): return True # we assume compatable!  Such as a slider
    elif subtype == supertype: return True
    else: return False


def getPersistenceData(key, defaultVal=None, minVal=None, maxVal=None):
    """Returns the value for a given key (typically keys are strings) in the current persistence data.  If there is no such key, then defaultVal is returned.  If the returned value has a different type than defaultVal has, then defaultVal is returned instead (a safety measure).  If minVal and/or maxVal are provided, and the returned value is either an int or a float, and it exceeds those values, then it is bounded to be within them (another safety measure).

Persistence data is state data provided by widgets so that, on next execution of the program, the widgets will set themselves up in the same state as before.  For example, a split pane's divider bar might store where the user last moved it, so it stays there across application executions.  Widgets store this information by providing a name (a string), which is stored with the information as its value.  The data is thus a simple dictionary of the form {name:val, name:val, ...}.  The vals may be anything.  The persistence data file format is the binary representation of this dictionary as saved out using the marshal.dump(...) function.

The safety measures are provided because the database could be corrupted, causing unsuspecting widgets to set themselves to invalid things, possibly crashing your program."""
    
    global _persistenceData
    if _persistenceData.has_key(key):
        p = _persistenceData[key]
        try:
            if not _compatableType(type(p), type(defaultVal)):
                return defaultVal
            elif minVal != None and (type(p) == types.FloatType or type(p) == types.IntType) and p < minVal:
                return minVal
            elif maxVal != None and (type(p) == types.FloatType or type(p) == types.IntType) and p > maxVal:
                return maxVal
            else:
                return _persistenceData[key]
        except Exception, error: handleError(error)
    return defaultVal




def setPersistenceData(key, val):
    """Adds a key:value pair to the current persistence data.  The key probably should be a string.

Persistence data is state data provided by widgets so that, on next execution of the program, the widgets will set themselves up in the same state as before.  For example, a split pane's divider bar might store where the user last moved it, so it stays there across application executions.  Widgets store this information by providing a name (a string), which is stored with the information as its value.  The data is thus a simple dictionary of the form {name:val, name:val, ...}.  The vals may be anything.  The persistence data file format is the binary representation of this dictionary as saved out using the marshal.dump(...) function."""
    
    global _persistenceData
    if (key != None):
        _persistenceData[key] = val






#######################    CLASSES    #######################

_widgetSpacing = 16


class Wrap:
    """A generic holder for a gtk Widget, automatically showing it."""
    outer = None
    
    def __init__(self, widget):
        self.outer = widget
        widget.show()
    
    def getBasicComponent(self):
        return self.outer


class Strut:
    """An empty widget which exists solely to enforce a minimum width or height.  The defaults are all 0.

GTK IMPLEMENTATION: Strut is implemented with an empty gtk.Image.  This may change in the future, do not rely on it."""
    strut = None
    
    def __init__(self, width=0, height=0):
        self.strut = gtk.Alignment()
        self.strut.set_size_request(width, height)
        self.strut.show()
    
    def setSize(self, width=None, height=None):
        "Changes the given size parameters.  If a parameter is None, it is not changed."
        size = self.strut.get_size_request()
        if width==None: width=size[0]
        if height==None: height=size[1]
        self.strut.set_size_request(width, height)
    
    def getBasicComponent(self):
        return self.strut


## Annoying GTK bug: gtk.Frame.set_property("label_yalign", ...) has no effect.

class Pack:
    """A container widget which stretches and moves its subsidiary widget in the X and/or Y directions.  If xPack is None, then the widget is stretched fully in the X direction.  Otherwise xPack -1, 0, or 1, in which case the widget is not stretched at all, but instead is placed at the far-left, center, or far-right of the container.  Likewise, yPack may be None, -1, 0, or 1 (top, center, bottom).  You can specify the subsidiary widget with 'child'.  Pack can also take a text string which appears as the label of a frame around the Pack.  

GTK IMPLEMENTATION: Pack is implemented either as a gtk.Alignment, or as a gtk.Alignment wrapped in a gtk.Frame (providing the text)."""
    alignment = None
    outer = None
    
    def __init__(self, text=None, xPack=None, yPack=None, child=None):
        xalign = 0
        yalign = 0
        xscale = 0
        yscale = 0
        if xPack==None:
            xscale = 1
        elif xPack==0:
            xalign=0.5
        elif xPack==1:
            xalign=1
        if yPack==None:
            yscale = 1
        elif yPack==0:
            yalign=0.5
        elif yPack==1:
            yalign=1
        self.alignment = gtk.Alignment(xalign,yalign,xscale,yscale)
        self.alignment.show()
        if text==None:
            self.outer = self.alignment
        else:
            self.outer = gtk.Frame(label=text)
            self.outer.add(self.alignment)
            self.outer.show()
        if child != None:
            self.add(child)
    
    def add(self, component=None):
        "Adds a component, or None, in which an empty Strut is added."
        if component == None:
            component = gtk.Strut()
        self.alignment.add(component.getBasicComponent())
    
    def getUnderlyingAlignment(self):
        return self.alignment
    
    def getBasicComponent(self):
        return self.outer


class MainWindow:
    """A container widget which represents the primary window of an application.  In Hildon this by necessity must be fully streched to fill the maximum available area.  MainWindow contains a built-in Pack and so has the same features as a Pack; however the text will be displayed in MainWindow's menu bar.  You can specify the subsidiary widget with 'child'.

HOOKS:
    allowToClose(self):     The user has just pressed the close box.  Return True if the MainWindow should be permitted to close, else False.    Returns true by default.
    willClose(self):        The window will close.

GTK IMPLEMENTATION: MainWindow is implemented as a hildon.Window which stores (through the Pack) a gtk.Alignment."""
    window = None
    pack = None
    
    def __init__(self, text=None, xPack=None, yPack=None, child=None):
        """text: The window title.  The Hildon menu actually displays two strings: first, the application string.Second, the window title.  To set the window application title,
        xPack: a value from 0.0 to 1.0 implying"""
        
        self.window = hildon.Window()
        _hildonApplication.add_window(self.window)
        self.setText(text)
        self.window.connect("destroy", lambda widget, data=None: self._willClose()) # no return
        self.window.connect("delete_event", lambda widget, event, data=None: not self.allowToClose()) # returns boolean
        self.pack = Pack(xPack=xPack, yPack=yPack, child=child)
        self.window.add(self.pack.getBasicComponent())
    
    def _willClose(self):
        "Internal hook for when the window will close.  Do not override."
        self.willClose()
        gtk.main_quit()
    
    def add(self, component=None):
        "Adds a component, or None, in which an empty Strut is added."
        self.pack.add(component)
    
    def show(self):
        "Shows the window."
        self.window.show()
    
    def setText(self,text=None):
        "Sets the text of the window title.  The Hildon menu actually displays two strings: first, the application string.Second, the window title.  To set the window application title,"
        if text == None:
            text = ""
        self.window.set_title(text)
    
    def getUnderlyingPack(self):
        "Returns the Pack used by the MainWindow."
        return self.pack
    
    def getUnderlyingAlignment(self):
        "Returns the gtk.Alignment store in the Pack used by the MainWindow."
        return self.pack.getUnderlyingAlignment()
    
    def getBasicComponent(self):
        "Returns the hildon.Window"
        return self.window
    
    def allowToClose(self):
        "Hook.  The user has just pressed the close box.  Return True if the MainWindow should be permitted to close, else False.  Returns true by default."
        return True
    
    def willClose(self):
        "Hook.  The window will close."
        pass
    
    def addMenu(self, menu):
        "Adds the given menu to the window, discarding the previous menu."
        window.hildon_set_menu(menu.buildMenuBar())



class Box:
    """A container widget into which you can add many widgets in either a horizontal (default) or vertical row.  Ordinarily the widgets are added left-to-right starting at the left edge of the container (or if it's a vertical row, added top-to-bottom starting at the top edge).  If rightJustified is set to True, then they are instead added right-to-left starting at the right edge (or if vertical, then bottom-to-top starting on the bottom edge).  The value of spacing indicates the amount of space naturally added between widgets.  As widgets are added you may specify, for each widget, if it is to be its preferred size or if it is to be expanded to fill as much space as possible.  A Box may also have a text string, which appears as the label of a frame around the box.

GTK IMPLEMENTATION: Box is implemented with either a gtk.VBox or a gtk.HBox, or if the text string is provided, then as a gtk.Frame holding either a gtk.VBox or gtk.HBox."""
    
    box = None
    outer = None
    rightJustified = False
    
    def __init__(self, text=None, vertical=False, children=[], spacing=_widgetSpacing, rightJustified=False):
        self.rightJustified = rightJustified
        if vertical:
            self.box = gtk.VBox(homogeneous=False, spacing=spacing)
        else:
            self.box = gtk.HBox(homogeneous=False, spacing=spacing)
        self.box.show()
        if text == None:
            self.outer = self.box
        else:
            self.outer = gtk.Frame(label=text)
            self.outer.add(self.box)
            self.outer.show()
        if type(children) != list or len(children) > 0:
            self.add(children)
    
    def add(self, component=None, expand=False):   # padding not included, it's stupid
        "Adds a component, or None, in which case a Strut is added.  Or you can provide multiple components as a list or tuple."
        if type(component) == types.ListType or type(component) == types.TupleType:
            for child in children:
                self.add(child, expand)
        else:
            if component == None:
                component = Strut()
                expand = True
            component = component.getBasicComponent()
            if self.rightJustified:
                self.box.pack_end(component, expand=expand, fill=True, padding=0)
            else:
                self.box.pack_start(component, expand=expand, fill=True, padding=0)
    
    def getUnderlyingBox(self):
        return self.box
    
    def getBasicComponent(self):
        return self.outer


class Split:
    """A container widget into which you can add two widgets in either a horizontal (default) or vertical row, with a divider-bar between them.  Each widget expands to fill as much space as possible; the user may move the divider bar to specify the division of space between the two widgets.  On construction you can provide both widgets, with the left and right parameters, or you can add them in turn with the add(...) method (the left/top widget is added first, then the right/bottom widget).  You can also set a currentValue, in pixels, of the bar location.

PERSISTENCE: Split takes a unique name, which it uses to store its divider bar location in the application's persistence database, so the bar put the next time application is started.

GTK IMPLEMENTATION: Split is implemented with either a gtk.VPaned or a gtk.HPaned."""
    # Split uses an ugly hack to get around huge massive set_position bugs in gtk.Paned.  If you set_position
    # before the first size allocation immediately after the first realization, then either nothing happens, or a crazy
    # value is used (perhaps 10x the request +/- weird amounts), even though get_position returns the amount you had set.
    # Grrr, GTK is horrifingly bad.  Also add1 and add2 do NOT operate as specified -- they are NOT the same as pack1 and
    # pack2 with resize=False and shrink=True.  Grrrr again.  So anyway, my hack is as follows.  I tap into realize and when
    # it occurs I set realized=True.  Then I tap into size-allocate and when it occurs, IF realized=True, THEN I set realized=False
    # and then procede the set the position.  This will in turn trigger further size-allocation hooks, but I ignore those because
    # realized is now false again.  This seems to allow me to set the position of the bar.   It also allows me to give the user
    # the option of setting a currentValue in pixels.
    name = None
    split = None
    added = 0
    realized = False
    outer = None
    allocated = False
    position = None
    
    def __init__(self, text=None, vertical=False, children=[], currentValue=None, name=None):
        if vertical:
            self.split = gtk.VPaned()
        else:
            self.split = gtk.HPaned()
        self.name = name
        self.position = getPersistenceData(name, currentValue)
        self.split.connect_after("realize", lambda widget : self._realized())
        self.split.connect_after("size-allocate", lambda widget, size : self._sizeAllocated())
        self.split.connect("destroy", lambda widget, data=None : setPersistenceData(name, self.split.get_position()))
        self.split.show()
        if text == None:
            self.outer = self.split
        else:
            self.outer = gtk.Frame(label=text)
            self.outer.add(self.split)
            self.outer.show()
        if type(children) != list or len(children) > 0:
            self.add(children)
    
    # sometimes we can must set the position immediately after realization (as is the case when the
    # Split is inside a Notebook.
    def _realized(self):
        if not self.realized:
            self.realized = True
            if self.position != None: self.split.set_position(self.position)
    
    # sometimes we must set the position immediately after the first allocation AFTER realization (as is the case when the
    # Split is inside a Window.
    def _sizeAllocated(self):
        if self.realized and not self.allocated:
            self.allocated = True
            if self.position != None: self.split.set_position(self.position)
    
    def add(self, component=None):
        "Adds the left/top component first, then the right/bottom component.  If you provide None, a Strut is added.  Or you can provide both components as a list or tuple.  Providing more than two components, in a single add call or through multiple add calls, raises an exception."
        if type(component) == types.ListType or type(component) == types.TupleType:
            for child in component:
                self.add(child)
        else:
            if self.added == 0:
                self.split.pack1(component.getBasicComponent(), resize=True, shrink=True)
                self.added = 1
            elif self.added == 1:
                self.split.pack2(component.getBasicComponent(), resize=True, shrink=True)
                self.added = 2
            else:
                raise Exception("Too many items (>2) added to a Split.  Attempted to add: %s" % component)
    
    def getUnderlyingPaned(self):
        return self.split
    
    def getBasicComponent(self):
        return self.outer


class Image:
    """A widget which displays an image.  The image may be specified as another Image, a gtk Stock image (one of the constants in http://www.pygtk.org/docs/pygtk/gtk-stock-items.html ), or loaded from a file with the given fileName, or given as an array of Strings representing XPM Image data.  Order of precedence is: stock, filename, xpm data, Image. 

GTK IMPLEMENTATION: Image is implemented with a gtk.Image."""
    image = None
    
    def __init__(self, image=None, stock=None, fileName=None, xpmData=None):
        self.image = gtk.Image()
        self.setImage(image=image, stock=stock, fileName=fileName, xpmData=xpmData)
        self.image.show()
        
    def setImage(self, image=None, stock=None, fileName=None, xpmData=None):
        if stock != None:
            self.image.set_from_stock(stock, gtk.ICON_SIZE_BUTTON)
        elif fileName != None:
            self.image.set_from_file(fileName)
        elif xpmData != None:
            self.image.set_from_pixbuf(gtk.gdk.pixbuf_new_from_xpm_data(xpmData))
        elif image != None:
            # arg, GTK doesn't have a consistent image mechanism(!!) you have to wander
            # through multiple options, grrr
            im = image.getBasicComponent()
            typ = im.get_storage_type()
            if typ == gtk.IMAGE_STOCK:
                stock = im.get_stock()
                self.image.set_from_stock(stock[0], stock[1])
            elif typ == gtk.IMAGE_PIXBUF:  # Assume that files load pixbufs too, docs suggest but do not state this
                self.image.set_from_pixbuf(im.get_pixbuf())
            elif type==gtk.IMAGE_EMPTY:
                self.image.set_from_pixbuf(None)
            else:
                raise Exception("Strange Image, Unknown Type, couldn't set to it: %s" % type)
        else: self.image.set_from_pixbuf(None)
    
    def isEmpty(self):
        return self.getBasicComponent().get_storage_type() == gtk.IMAGE_EMPTY
    
    def getBasicComponent(self):
        return self.image


class Label:
    """A widget which displays a read-only textual label with an optional Image.  The label is by default left-justified, with the optional Image to its left.  Optionally the label may be right-justified with the optional Image to its right.  The text can take up mutiple lines and may be specified as wrappable to the label width. 

GTK IMPLEMENTATION: Label is implemented (through Box) as a gtk.HBox, holding (through Image) a gtk.Image, a Strut(), and a gtk.Label."""
    box = None
    label = None
    image = None
    strut = None
    spacing = None
    
    def __init__(self, text=None, image=None, spacing=_widgetSpacing, rightJustified=False, wrappable=False, name=None):
        self.label = gtk.Label()
        if image==None: image = Image()
        self.image = image
        self.spacing = spacing
        yalign = self.label.get_alignment()[1]
        if wrappable:
            self.label.set_line_wrap(True)
        self.label.show()
        self.box = Box(spacing=0)
        #b = self.box.getUnderlyingBox()
        self.strut = Strut(width=spacing)
        if rightJustified:
            self.label.set_justify(gtk.JUSTIFY_RIGHT) # Has no effect on one-line labels
            self.label.set_alignment(1.0, yalign)
            #b.pack_end(image.getBasicComponent(), expand=False, padding=0)
            #b.pack_end(self.strut.getBasicComponent(), expand=False, padding=0)
            #b.pack_end(self.label, expand=True, fill=True, padding=0)
            self.box.getUnderlyingBox().pack_start(self.label, expand=True)
            self.box.add(self.strut)
            self.box.add(image)
        else:
            self.label.set_justify(gtk.JUSTIFY_LEFT) # Has no effect on one-line labels
            self.label.set_alignment(0.0, yalign)
            #b.pack_start(image.getBasicComponent(), expand=False, padding=0)
            #b.pack_start(self.strut.getBasicComponent(), expand=False, padding=0)
            #b.pack_start(self.label, expand=True, fill=True padding=0)
            self.box.add(image)
            self.box.add(self.strut)
            self.box.getUnderlyingBox().pack_start(self.label, expand=True)
        self.setText(getPersistenceData(name, text))  # resets border
        self.label.connect("destroy", lambda widget, data=None : setPersistenceData(name, self.getText()))
    
    def _resetBorder(self):
        if self.image.isEmpty() or self.getText()==None or len(self.getText())==0:
            self.strut.setSize(0, None)  # get rid of border
        else:
            self.strut.setSize(self.spacing, None)
    
    def setText(self, text=None):
        if text == None:
            text = ""
        self.label.set_text(text)
        self._resetBorder()
    
    def getText(self):
        return self.label.get_text()
    
    def setImage(self, image=None, stock=None, fileName=None, xpmData=None):
        self.image.setImage(stock=stock, fileName=fileName, image=image, xpmData=xpmData)
        self._resetBorder()
    
    def getImage(self):
        "Do not add/remove the image through label.getImage().setImage(...), because the Label won't be able to add/remove padding between the image and text.  Instead, add/remove the image with label.setImage()"
        return self.image
    
    def getBasicComponent(self):
        return self.box.getBasicComponent()





class Text:
    """A widget which displays read/write multiple-line, scrollable text. and may wrap around if so specified.

PERSISTENCE: Text takes a unique name, which it uses to store its text information and scroll position in the application's persistence database.

GTK IMPLEMENTATION: Text is implemented with a gtk.ScrolledWindow holding a gtk.TextView."""
    textview = None
    outer = None
    
    def __init__(self, text=None, wrappable=True, persistentText=True, persistentScroll=True, name=None):
        self.textview = gtk.TextView()
        if wrappable: 
            self.textview.set_wrap_mode(gtk.WRAP_WORD)
        else:
            self.textview.set_wrap_mode(gtk.WRAP_NONE)
        t = text
        s = 0
        p = getPersistenceData(name, None)
        if type(p) == dict:
            try: 
                if persistentText and type(p['text']) == types.StringType: t = p['text']
            except: pass
            try: 
                if persistentScroll and type(p['scroll']) == types.IntType or type(p['scroll']) == types.FloatType: s = p['scroll']
            except: pass
        self.setText(t)
        self.outer = gtk.ScrolledWindow()
        self.outer.add_with_viewport(self.textview)
        self.outer.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.outer.get_vadjustment().set_value(s)
        self.textview.show()
        self.outer.show()
        self.textview.connect("destroy", lambda widget, data=None : setPersistenceData(name, {'text':self.getText(), 'scroll':self.outer.get_vadjustment().get_value() }))
        
    def setText(self, text=None):
        if text == None:
            text = ""
        self.textview.get_buffer().set_text(text)
        
    def getText(self):
        b = self.textview.get_buffer()
        return b.get_text(b.get_start_iter(), b.get_end_iter())
    
    def getUnderlyingTextView(self):
        return self.textview
    
    def getBasicComponent(self):
        return self.outer






def _truncatedValueString(value, precision):
    #### ARGH, python's stupid "%.f*f" ROUNDS rather than TRUNCATES.  Thus people expecting 
    #### that 0.9996 will be 0.99 will find that it instead is being printed to the
    #### user as 1.0.  CRAP.  So I have to write my own truncation function here.
    pvalue = "%s" % value
    periodindex = pvalue.rfind(".")  # where's the period?
    if periodindex + precision < len(pvalue):
        pvalue = pvalue[0:periodindex+precision+1].rstrip("0").rstrip(".")
    return pvalue



class Slider:
    """A horizontal or vertical sliding widget which permits the user to choose from a set of numerical or other values.  You can specify the precision of the number being displayed (note that, unlike gtk.Scale, this does not affect the user's settable choices).  You can add a label in one of three ways: first, you may provide a Label directly, which Slider will update for you.  Second, you can override the didChangeValue method to update a Label (or other widget) as you like when the slider is modified; you can call provideFormat to give you a formatted String given the current value.  Third, you can tell the Slider to provide a topLabel which floats with the widget (this is equivalent to gtk.POS_TOP).  This only really makes sense for horizontal sliders.  Last, you can specify if the slider is enabled or not.

The widget has three basic modes: first, it can slide smoothly among floating-point values from a minimum to a maximum; second, it can move by increments between a minimum and a maximum (known as 'ticks'); third, it can slide from choice to choice in a provided list.  For the first case, set minValue and maxValue to your desired values (defaults are 0 and 1).  For the second choice, set minValue and maxValue to your desired values, and set the number of ticks.  For example, if you wish to go from 0 to 10, inclusive, by increments of 2, that's 6 ticks.  For the third choice, minimum and maximum values are set for you (to 0 and length(list)-1).  The elements in the list are displayed to the user, and you determine programmatically which one is chosen by the index of the item.  You may also override the provideFormat(...) method, if you feel so inclined, to further customize display of information -- perhaps to create a logarithmic scale.

PERSISTENCE:  Slider takes a unique name, which it uses to store its numerical position in the application's persistence database.

HOOKS:
    didChangeValue(self, value):     The user has just changed the slider's value.
    provideFormat(self, value):      The slider needs a textual representation of the provided value.  Return a String.  There is a default version of this method which handles most cases, so you needn't override this unless you feel so inclined.

GTK IMPLEMENTATION: Slider is implemented with either an gtk.HScale or a gtk.VScale."""
    slider = None
    minValue = 0
    maxValue = 1
    ticks = None
    precision = None
    name = None
    label = None
    action = None
    outer = None
    drawNothing = False
    
    def __init__(self, text=None, ticks=None, minValue=0, maxValue=1, currentValue=0, precision=3, floatingLabel=False, vertical=False, label=None, labelWidth=64, enabled=True, action=None, name=None):
        global _widgetSpacing
        self.ticks = ticks
        self.precision = precision
        self.name = name
        self.action = action
        
        if vertical==True: self.slider = gtk.VScale()
        elif ticks==None: self.slider = gtk.HScale()
        else: self.slider = gtk.HScale() #shildon.Controlbar()  
        
        self.slider.set_digits(0)
        top = 0
        if ticks==None:
            # use the actual values, adjusted to zero
            top = maxValue - minValue
            current = currentValue - minValue
            self.slider.set_digits(100)  # beyond the precision of a float.  gtk is dumb.
        elif type(ticks) == types.ListType: # it's an array of items
            # use the number of ticks minus one, so we jump by tick
            minValue = 0
            maxValue = len(ticks) - 1
            current = currentValue
            top = maxValue
        else: # we presume it's an integer
            # use the number of ticks minus one, so we jump by tick
            top = ticks - 1
            if (ticks == 1): ticks = 2 # avoid divide by zero
            current = (currentValue - minValue) / (ticks - 1)
        self.slider.set_adjustment(gtk.Adjustment(value=current, lower = 0, upper= top))
        presize = self.slider.get_size_request()
        if floatingLabel:
            self.outer = self.slider
            if vertical: 
                self.slider.set_value_pos(gtk.POS_RIGHT)
                self.slider.set_size_request(presize[0] + labelWidth + 4, presize[1]) # gutter needs to be about 4 or so
            else: self.slider.set_value_pos(gtk.POS_TOP)
        elif label==None:
            if vertical:
                self.outer = self.slider
                self.slider.set_value_pos(gtk.POS_TOP)
                self.slider.set_size_request(max(presize[0], labelWidth), presize[1])
            else:
                self.drawNothing = True
                self.slider.set_value_pos(gtk.POS_RIGHT)
                self.label = Label()
                l = self.label.getBasicComponent()
                l.set_size_request(labelWidth, l.get_size_request()[1])
                self.outer = gtk.HBox(homogeneous=False, spacing=_widgetSpacing)
                self.outer.pack_start(self.slider, expand=True, fill=True)
                self.outer.pack_start(self.label.getBasicComponent(), expand=False, fill=True)
                self.outer.show()
        else:
            self.outer = self.slider
            self.drawNothing = True
            self.slider.set_value_pos(gtk.POS_RIGHT)
            self.label = label
        self.setEnabled(enabled)
        self.minValue = minValue  # now that max and min values have been changed
        self.maxValue = maxValue
        
        self.setValue(getPersistenceData(name, (self.getValue())))
        self.slider.connect("destroy", lambda widget, data=None : setPersistenceData(name, self.getValue()))
        self.slider.get_adjustment().connect("value_changed", lambda adjustment: self._update(adjustment))
        self.slider.connect("format_value", lambda scale, value: self._provideFormat(value)) # returns a string
        self.slider.show()
    
    def _update(self, adjustment):
        value = self.getValue(adjustment)
        self.didChangeValue(value)
        self._valueChanged(value)
    
    def _valueChanged(self, value):
        if self.label != None:
            self.label.setText(self.provideFormat(value))
    
    def setValue(self, value):
        adjustment = self.slider.get_adjustment()
        if value < self.minValue:
            value = self.minValue
        if value > self.maxValue:
            value = self.maxValue
        self.slider.set_value((value - self.minValue) * adjustment.upper / (self.maxValue - self.minValue))
        self._valueChanged(value)
    
    def getValue(self, adjustment=None):
        if adjustment==None:
            adjustment=self.slider.get_adjustment()
        return (adjustment.value / (adjustment.upper * 1.0)) * (self.maxValue - self.minValue) + self.minValue
    
    def didChangeValue(self, value):
        "By default, calls the action provided in the constructor, passing the value."
        if self.action != None:
            self.action(value)
    
    def setLabel(self, label):
        self.label = label
    
    def _provideFormat(self, value):
        # Overcomes a bug in GTK: if set_draw_value(False), then set_digits has no effect at all.
        # Grrrrrrrrrrrrrrrr.   Stupid GTK.  This means I can't have a slider which has ticks unless
        # I let it draw some text on the screen.  The way I get around this is by letting it "draw" text
        # but literally draw an empty string.  Stupid.
        if self.drawNothing: return ""
        else: return self.provideFormat(value)
    
    def provideFormat(self, value):
        if type(self.ticks) == types.ListType:
            return "%s" % self.ticks[int(value)]
        elif value == int(value):
            return "%s" % int(value)
        elif self.precision==None:
            return "%s" % value
        else:
            return _truncatedValueString(value, self.precision)
    
    def getUnderlyingSlider(self):
        return self.slider
    
    def getBasicComponent(self):
        return self.outer
    
    def setEnabled(self, enabled):
        self.slider.set_sensitive(enabled)



class Button:
    """A pushbutton with text and/or icon images.  You can provide text to the Button in two forms: either as a string or as a list of strings.  Likewise, you can also provide an image either as an Image or as a list of Images.  The Button has some N number of states, which it calculates from the minimum length among these two lists.  The Button starts in state 0.  After you press and release the Button it shifts to the next state and displays the appropriate text and image.  When all states have been exhausted, the Button reverts to state 0 again.  Typically you'd have only one or two states.
     
You can also specify text and images to display when the button is being pressed while in a certain state.  Likewise you can specify the border width and whether or not the border (and background) is to be shown.  You can also stipulate whether or not the Button is enabled.  The lists provided for the pressed situations do not contribute to the calculation of the number of states.
     
PERSISTENCE:  Button takes a unique name, which it uses to store its current state in the application's persistence database.

HOOKS:
    didClick(self, state):      The user has just pressed and released the button, and it has transitioned to a new state.
    didPress(self):             The user has just pressed the button or has reenterred the button still holding the stylus down.
    didRelease(self):           The user has just released the button or has left the button still holding the stylus down.

GTK IMPLEMENTATION: Button is implemented with a gtk.Button holding a Label containing the image and text."""
    button = None
    state = 0
    text = None
    image = None
    label = None
    pressedText = None
    pressedImage = None
    numStates = 0
    pressed = False
    inside = False
    lastText = False  # Intentionally not 'None'
    lastImage = False # Intentionally not 'None'
    action = None
    lab = None
    
    # Standard width for most Nokia buttons is 110.  But perhaps we should define the width to be -1
    # MOST irritating: I can't turn off displacement because it's in a style property, grrr....
    def __init__(self, text=None, image=None, pressedText=None, pressedImage=None, showBorder=True, currentValue=0, enabled=True, minimumWidth=110, minimumHeight=48, action=None, name=None):  # vertical=False,  -- presently can't use because gtk version too old
        if type(text) != list: text = [text]
        if type(image) != list: image = [image]
        if type(pressedText) != list: pressedText = [pressedText]
        if type(pressedImage) != list: pressedImage = [pressedImage]
        self.numStates = len(text)
        if len(image) > self.numStates: self.numStates = len(image)
        
        self.action = action
        self.text = text
        self.image = image
        self.pressedText = pressedText
        self.pressedImage = pressedImage
        #self.label = gtk.Label()
        #self.label.show()
        self.button = gtk.Button()
        #self.button.set_focus_on_click(False)  # Has no effect :-(
        b = Pack(xPack=0,yPack=0)
        self.lab = Label()
        b.add(self.lab)
        self.button.add(b.getBasicComponent())
        #self.button.add(self.label)
        #if vertical:
        #    self.button.set_property("image-position", gtk.POS_TOP)  # else POS_LEFT by default
        if not showBorder:
            self.button.set_relief(gtk.RELIEF_NONE)  # no difference between RELIEF_NORMAL and RELIEF_HALF btw
        self.setEnabled(enabled)
        if minimumWidth==None: minimumWidth = -1
        if minimumHeight==None: minimumHeight = -1
        self.button.set_size_request(minimumWidth, minimumHeight)
        self.setState(getPersistenceData(name, currentValue))
        self.button.connect("destroy", lambda widget, data=None : setPersistenceData(name, self.getState()))
        self.button.connect("pressed", lambda widget, data=None: self._didPress())  # No return
        self.button.connect("released", lambda widget, data=None: self._didRelease())  # No return
        self.button.connect("enter", lambda widget, data=None: self._didEnter())  # No return
        self.button.connect("leave", lambda widget, data=None: self._didLeave())  # No return
        self.button.show()
    
    def _didPress(self):
        self.didPress()
        self.pressed = True
        self.setState(self.state)
        
    def _didEnter(self):
        self.didPress()
        self.inside = True
    
    def _didLeave(self):
        self.didRelease()
        self.inside = False
    
    def _didRelease(self):
        self.didRelease()
        if (self.inside and self.pressed):
            self.pressed = False
            self.setState(self.state + 1)
            self.didClick(self.state)
        else: self.pressed = False
        # Sadly, we still remain in prelight stage because of a dumb Nokia bug.  :-(  They seem to think that styli can "hover" like mice.
        
    def didRelease(self): pass
    def didPress(self): pass
    def didClick(self, value):
        "By default, calls the action provided in the constructor, passing in the state."
        if self.action != None:
            self.action(value)
    
    def getState(self):
        return self.state
        
    def setState(self, state):
        if (state < 0): state = 0
        state = state % self.numStates
        self.state = state
        
        t = None
        i = None
        if (self.pressed):
            t = (self.pressedText[self.state % len(self.pressedText)])
            if t == None: t = (self.text[self.state % len(self.text)])
            if t == None: t = ""
            i = (self.pressedImage[self.state % len(self.pressedImage)])
            if i == None: i = (self.image[self.state % len(self.image)])
        else:
            t = (self.text[self.state % len(self.text)])
            if t == None: t = ""
            i = (self.image[self.state % len(self.image)])
        
        # we add the lastText and lastImage gunk to avoid setting tons of stuff
        # in GTK when we don't have to
        if (t != self.lastText):
            self.lastText = t
            #self.label.set_text(t)
            self.lab.setText(t)
        if (i != self.lastImage):
            self.lastImage = i
            if (i==None):
                self.lab.setImage(None)
                #self.button.set_property("image", None) # stupid, no clean way to clear images
            else:
                self.lab.setImage(Image(i))
                #self.button.set_image(Image(i).getBasicComponent())   # Have to make a copy, grrrr
    
    def setEnabled(self, enabled):
        self.button.set_sensitive(enabled)
    
    def getBasicComponent(self):
        return self.button





_leftArrowImage = False
_rightArrowImage = False
_bellyButtonImage = False
def _buildSpinnerImages():
    global _leftArrowImage
    global _rightArrowImage
    global _bellyButtonImage
    global _leftArrow
    global _rightArrow
    global _bellyButton
    
    if _leftArrowImage == False:
        _leftArrowImage = Image(xpmData=_leftArrow)
        _rightArrowImage = Image(xpmData=_rightArrow)
        _bellyButtonImage = Image(xpmData=_bellyButton)


class Spinner:
    label = None
    minValue = None
    maxValue = None
    add = None
    multiply = None
    precision = None
    reset = None
    currentValue = None
    ticks = None
    box = None
    name = None
    action = None
    
    def __init__(self, add=1, multiply=1, minValue=None, maxValue=None, currentValue=0, precision=3, noReset=False, buttonsRight=False, ticks=None, action=None, name=None):
        global _leftArrowImage
        global _rightArrowImage
        global _bellyButtonImage
        global _leftArrow
        global _rightArrow
        global _bellyButton
        
        self.action = action
        self.name = name
        self.label = Label(_truncatedValueString(currentValue, precision))
        self.box = Box(spacing=0)
        if buttonsRight:
            self.box.add(self.label)
            self.box.add(Strut(width=16))
        _buildSpinnerImages()
        leftButton = Button(image=_leftArrowImage, minimumWidth=None, minimumHeight=24)
        leftButton.didClick = lambda widget: self.didLeftClick()
        self.box.add(leftButton)
        if not noReset:
            resetButton = Button(image=_bellyButtonImage, minimumWidth=None, minimumHeight=24)
            resetButton.didClick = lambda widget: self.didResetClick()
            self.box.add(resetButton)
        rightButton = Button(image=_rightArrowImage, minimumWidth=None, minimumHeight=24)
        rightButton.didClick = lambda widget: self.didRightClick()
        self.box.add(rightButton)
        if not buttonsRight:
            self.box.add(Strut(width=16))
            self.box.add(self.label)
        self.add = add
        self.multiply = multiply
        if ticks == None:
            self.minValue = minValue
            self.maxValue = maxValue
        else:
            self.minValue = 0
            self.maxValue = len(ticks) - 1
        self.reset = currentValue
        self.precision = precision
        self.ticks = ticks
        self.currentValue = currentValue
        self.setValue(getPersistenceData(name, self.getValue()))
        self.getBasicComponent().connect("destroy", lambda widget, data=None : setPersistenceData(name, self.getValue()))
    
    def setValue(self, value):
        if (self.minValue != None and value < self.minValue):
            value = self.minValue
        if (self.maxValue != None and value > self.maxValue):
            value = self.maxValue
        self.currentValue = value
        self.label.setText(self.provideFormat(value))
        
    def getValue(self):
        return self.currentValue
    
    def provideFormat(self, value):
        if type(self.ticks) == types.ListType:
            return "%s" % self.ticks[int(value)]
        elif value == int(value):
            return "%s" % int(value)
        elif self.precision==None:
            return "%s" % value
        else:
            return _truncatedValueString(value, self.precision)
    
    def didLeftClick(self):
        a = self.currentValue
        self.setValue((self.currentValue - self.add) / (1.0 * self.multiply))  # 1.0 forces floating point division
        if (a != self.currentValue):
            self.didChangeValue(self.currentValue)
    
    def didRightClick(self):
        a = self.currentValue
        self.setValue((self.currentValue * self.multiply) + self.add)
        if (a != self.currentValue):
            self.didChangeValue(self.currentValue)
    
    def didResetClick(self):
        a = self.currentValue
        self.setValue(self.reset)
        if (a != self.currentValue):
            self.didChangeValue(self.currentValue)
    
    def didChangeValue(self, value):
        "By default, calls the action provided in the constructor, passing in the value."
        if self.action != None:
            self.action(value)
    
    def getBasicComponent(self):
        return self.box.getBasicComponent()


##### BAD GTK BUG: Notebook does not propagate the destroy signal to its children!
class Notebook:
    outer = None
    notebook = None
    name = None
    
    def __init__(self, text=None, children=[], tabs=[], currentValue=0, tabsOnBottom=False, name=None):
        self.name = name
        self.notebook = gtk.Notebook()
        if tabsOnBottom:
            self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        self.setValue(getPersistenceData(name, currentValue))
        self.notebook.connect("destroy", lambda widget, data=None : self._destroy())
        self.notebook.set_show_tabs(True)
        self.notebook.set_scrollable(True)
        if type(children) != list or len(children) > 0:
            self.add(children, tabs)
        self.setValue(0)
        self.notebook.show()
        if text == None: 
            self.outer = self.notebook
        else:
            self.outer = gtk.Frame(label=text)
            self.outer.add(self.notebook)
            self.outer.show()
    
    def _destroy(self):
        "Gaggggh, Notebook does not propagate the destroy signal, screwing up our persistence.  We force propagation here"
        setPersistenceData(self.name, self.getValue())
        for i in self.notebook.get_children():
            i.destroy()
    
    def getValue(self):
        return self.notebook.get_current_page()
    
    def setValue(self, value):
        return self.notebook.set_current_page(value)
    
    def add(self, component=None, tab=None):
        if type(component) == types.ListType or type(component) == types.TupleType:
            if (type(tab) != list and type(tab) != tuple) or length(tab) != length(component):
                raise Exception("Mismatch between component list and text while adding to a Notebook: %s vs %s" % component, text)
            i = 0
            while i < len(component):
                self.add(component[i], tab[i])
                i = i + 1
        elif type(tab)==list or type(tab)==tuple:
            raise Exception("Mismatch between component list and tab while adding to a Notebook: %s vs %s" % component, tab)
        else:
            if component==None: component=Strut()
            if type(tab) == types.StringType or type(tab)== types.IntType or type(tab)== types.FloatType:
                t = "%s" % tab
                tab = Label(text=t)
            self.notebook.append_page(component.getBasicComponent(), tab.getBasicComponent())
    
    def getUnderlyingNotebook(self):
        return self.notebook
    
    def getBasicComponent(self):
        return self.outer




class Table:
    outer = None
    table = None
    row = -1
    column = -1
    columns = 0
    
    def __init__(self, text=None, children=[], columns=2, rowSpacing=4, columnSpacing=_widgetSpacing):
        self.table = gtk.Table(rows=1,columns=columns,homogeneous=False)
        self.columns = columns
        self.column=columns-1
        if type(children) != list or len(children) > 0:
            self.add(children)
        self.table.set_row_spacings(rowSpacing)
        self.table.set_col_spacings(columnSpacing)
        self.table.show()
        if text == None:
            self.outer = self.table
        else:
            self.outer = gtk.Frame(label=text)
            self.outer.add(self.table)
            self.outer.show()
    
    def add(self, component=None, expand=False, columns=1):
        if type(component) == types.ListType or type(component) == types.TupleType:
            for child in component:
                self.add(child, expand)
        else:
            if type(component) == types.StringType or type(component)== types.IntType or type(component)== types.FloatType:
                t = "%s" % component
                component = Label(text=t, rightJustified=True)
           # increase rows
            self.column = self.column + 1
            if self.column >= self.columns:
                self.column = 0
                self.row = self.row + 1
                self.table.resize(self.row+1, self.columns)  # this better not be O(n), or I'm gonna be mad
            # We expand on the last column always
            if (self.column == self.columns-1):
                xoptions = gtk.FILL | gtk.EXPAND
                if not expand:
                    b = Box(spacing=0)
                    b.add(component)
                    component=b
            else:
                xoptions = gtk.FILL
            self.table.attach(component.getBasicComponent(), 
                self.column, self.column+columns, self.row, self.row+1, xoptions, 0, 0,0)
            self.column = self.column + columns - 1  # In case we had spanned multiple columns
    
    def getUnderlyingTable(self):
        return self.table
    
    def getBasicComponent(self):
        return self.outer


class Menu:
    children=None
    menu = None
    
    def __init__(self, children=[]):
        self.children = children
        self.menu = gtk.Menu()
        for i in children:
            self.add(i)
    
    def add(self, item=None):
        self.children.append(item)
        men.append(item.getBasicComponent())
    
    def getChildren():
        return children[:]    # make a copy
    
    def getBasicComponent(self):
        return self.menu



class MenuItem:
    menu = None
    submenu = None
    state = None
    action = None
    image = None
    
    def __init__(self, text=None, image=None, action=None, checked=None, line=False, submenu=None, enabled=True, name=None):
        self.image = image
        self.action = action
        if line:
            self.menu = gtk.SeparatorMenuItem()
        elif checked != None:
            self.menu = gtk.CheckMenuItem(label=text)
            self.state = checked
            self.menu.set_active(checked)
        else:
            menu = gtk.MenuItem(label=text)
        self.setEnabled(enabled)  # Doesn't matter for separator -- I hope!
        self.setValue(getPersistenceData(name, (self.getValue())))
        if submenu != None:
            self.setSubmenu(submenu)
        self.menu.connect("destroy", lambda widget, data=None : setPersistenceData(name, self.getValue()))
        self.menu.connect("activate", lambda widget, data=None : self._didClick())
    
    def setValue(self, value):
        if self.state != None and type(value) == bool:  # make sure it's a checkbox
            self.state = value
            self.menu.set_active(state)  # it's a checkbox
    
    def getValue(self):
        return self.state
    
    def setEnabled(self, enabled):
        self.menu.set_sensitive(enabled)
    
    def _didClick(self):
        self.didClick(self.state)
    
    def didClick(self, value=state):
        "By default, calls the action provided in the constructor, passing the value."
        if self.action != None:
            self.action(state)
    
    def setSubmenu(self, submenu):
        "Submenu must be a list, tuple, None, or Menu"
        if type(submenu) == types.ListType or type(submenu) == types.TupleType:  # first convert to a Menu
            self.submenu = Menu(submenu)
            self.menu.set_submenu(self.submenu.getBasicComponent())
        elif (submenu == None):              # possibly remove
            self.menu.remove_submenu()
            self.submenu = None
        else:
            self.submenu = submenu
            self.menu.set_submenu(self.submenu.getBasicComponent())
    
    def getSubmenu(self):
        "Returns None if no submenu, else returns a Menu"
        return self.submenu
    
    def setImage(self, image):
        self.image = image
    
    def getImage(self):
        return image
    
    def popup(self, widget=None, x=None, y=None):
        "Pops up the menu attached to the top-right side of a widget, or to the provided <x,y> coordinates"
        if x != None:
            self.submenu
        
    def getBasicComponent(self):
        return self.menu




class TextField:
    entry = None
    image = None
    strut = None
    spacing = None
    history = None
    values = None
    persistentHistory = True
    persistentText = True
    includeSpace = True
    historyLength = 8
    
    def __init__(self, text=None, image=None, spacing=_widgetSpacing, values=[], persistentText=True, persistentHistory=True, historyLength=8, includeSpace=True, name=None):
        self.entry = gtk.combo_box_entry_new_text()
        self.entry.child.add_events(gtk.gdk.FOCUS_CHANGE_MASK)
        self.entry.child.add_events(gtk.gdk.VISIBILITY_NOTIFY_MASK)
        if image==None: image = Image()
        self.image = image
        self.spacing = spacing
        self.entry.show()
        self.box = Box(spacing=0)
        self.strut = Strut(width=spacing)
        self.box.add(image)
        self.box.add(self.strut)
        self.box.getUnderlyingBox().pack_start(self.entry, expand=True)
        p = getPersistenceData(name, None)
        self.values = values
        self.history = []
        self.includeSpace = includeSpace
        self.historyLength = historyLength
        self.persistentHistory = persistentHistory
        self.persistentText = persistentText
        if type(p) == dict:
            try: 
                if persistentHistory and type(p['history']) == types.ListType:
                    self.history = p['history']
            except: pass
            try: 
                if persistentText and type(p['text']) == types.StringType:
                    text = p['text']
            except: pass
        self.setText(text)
        self._buildHistory()
        self.entry.connect("destroy", lambda widget, data=None : self._destroy(name))
        self.entry.child.connect("focus-out-event", lambda widget, event, data=None : self._buildHistory())
    
    def _destroy(self, name):
        self._buildHistory() # so we got the last item just in case
        if self.persistentHistory or self.persistentText:
            p = {}
            if self.persistentText: p['text'] = self.getText()
            if self.persistentHistory: p['history'] = self.history
            setPersistenceData(name, p)
        
    def _buildHistory(self):
        # Reset the list with basic values
        self.entry.set_model(gtk.ListStore(gobject.TYPE_STRING))  # reset model
        for i in self.values:
            self.entry.append_text(i)
        if self.includeSpace:
            self.entry.append_text("")
        text = self.getText()
        if text.strip() != "" and text not in self.history and text not in self.values and self.historyLength > 0:
            # Delete the bottom one, insert at the top
            self.history = self.history[:self.historyLength]
            # Insert at front
            self.history.insert(0, text)
        for i in self.history:
            self.entry.append_text(i)
    
    def _resetBorder(self):
        if self.image.isEmpty():
            self.strut.setSize(0, None)  # get rid of border
        else:
            self.strut.setSize(self.spacing, None)
    
    def setText(self, text=None):
        if text == None:
            text = ""
        self.entry.child.set_text(text)
    
    def getText(self):
        return self.entry.child.get_text()
    
    def setImage(self, image=None, stock=None, fileName=None, xpmData=None):
        self.image.setImage(stock=stock, fileName=fileName, image=image, xpmData=xpmData)
        self._resetBorder()
    
    def getImage(self):
        "Do not add/remove the image through label.getImage().setImage(...), because the Label won't be able to add/remove padding between the image and text.  Instead, add/remove the image with label.setImage()"
        return self.image
    
    def getBasicComponent(self):
        return self.box.getBasicComponent()



class TreeView:
    view = None
    columnTypes = None
    outer = None
    model = None
    
    def __init__(self, text=None, columns=1, reorderable=False, name=None):
        # build array of columns.  For now we assume they're all strings with a basic cell renderer.  
        # We start by creating the types of the columns
        if (type(columns)== types.IntType):
            self.columnTypes = [types.StringType for i in range(0,columns)]
        else:
            self.columnTypes = [types.StringType for i in len(columns)]
        # Now we build the model and view
        self.model = apply(gtk.TreeStore, self.columnTypes)
        self.view = gtk.TreeView(self.model)
        # Set the visibility of the headers
        self.view.set_headers_visible(type(columns) != types.IntType)
        self.view.show()
        # Now we load the columns
        for typ in self.columnTypes:
            self.view.append_column(gtk.TreeViewColumn(self.columnTypes[typ], gtk.CellRendererText()))
        if (text==None):
            self.outer = self.view
        else:
            self.outer = gtk.Frame(label=text)
            self.outer.add(self.view)
            self.outer.show()
        self.view.get_selection().connect("changed", lambda widget, data=None: self.selectionChanged(apply(self.model.get_iter, self.view.get_selected_rows()[1])))
        self.view.set_reorderable(reorderable)
    
    def selectionChanged(self, iters): pass
    
    def append(self, listOrTuple, parentRow=None):
        "Returns an iter of the row"
        return model.append(parentRow, listOrTuple)
        
    def getUnderlyingTreeView(self):
        return self.view
    
    def getModel(self):
        return self.model
    
    def getBasicComponent(self):
        return self.outer





def testLibrary():
    print "I've turned on verbose persistence messages so we can see what gets read/written."
    print "The persistence database is called 'testPersistenceData' in the Documents folder."
    print "Feel free to delete it after quitting the program."
    print ""
    setVerbose(True)
    loadPersistenceData("/home/user/MyDocs/.documents/testPersistenceData")
    n = Notebook(name="notebook0")
    w = MainWindow("Test", child=n)
    
    # add some sliders
    b = Box()
    n.add(b, tab="Sliders")
    attachedSlider1 = Slider(vertical=True, name="slider0")
    b.add(attachedSlider1)
    b.add(Slider(vertical=True, ticks=["Lions", "Tigers", "Bears", "Oh My!"], floatingLabel=True, labelWidth=80, name="slider1"))
    b.add(Slider(vertical=True, ticks=["Lions", "Tigers", "Bears", "Oh My!"], name="sliderq"))
    sliderLabel = Label(rightJustified=True)
    b.add(Slider(vertical=True, minValue=0, maxValue=10, ticks=11, label=sliderLabel, name="slider2"))
    
    b2 = Box(vertical=True)
    b.add(b2, expand=True)
    attachedSlider2 = Slider(floatingLabel=True, currentValue=1, name="slider3")
    b2.add(attachedSlider2)
    attachedSlider2.didChangeValue = lambda value : attachedSlider1.setValue(1.0 - value)
    attachedSlider1.didChangeValue = lambda value : attachedSlider2.setValue(1.0 - value)
    
    b2.add(Slider(minValue=3, maxValue=9, ticks=3, currentValue=6, precision=0, name="slider4"))
    b2.add(Label("Disabled:"))
    b2.add(Slider(minValue=3, maxValue=9, ticks=3, currentValue=6, precision=0, enabled=False, name="slider5"))
    b2.add(Label("Remote label for slider at left:"))
    b2.add(sliderLabel)
    b2.add(None, expand=True)
    
    # add some text and splitpanes
    text0 = """As you can see at right, GTK's TextViews have weird, slow resizing bugs when inside HPane sliders and ScrolledWindows.  Strange that: it's the MOST COMMON THING one would put them in!"""
    text1 = """PERSISTENCE.  Many of the widgets here are persistent, meaning that they stay the way you set them even after you quit and restart.  This is an optional behavior for the programmer, but it's easy to implement.  Persistence is stored in a database file called 'testPersistenceData' in your Documents folder -- quitting the program and THEN deleting that file will cause the widgets to reset next time.
    
    Persistent widgets include: the Notebook's tabs above; all text in text views like this one; the location of the split-pane bars containing these text views; the positions of sliders; the states of multi-state buttons and certain text labels; etc."""
    
    text2 = "BUGS.  There are an awful lot of bugs in GTK.  It's terrible.  For example: the Notebook doesn't propagate the 'destroy' signal; slider's set_digits method has no effect if set_draw_value is False; slider's set_digits method dictates both the text size and the number of ticks, but forces the only tick options to be powers of 10; Frame's 'label_yalign' property does nothing (grrrr); Paned.set_position does nothing until after gtk.main() has been called; Paned.add1 and add2 do not operate as documented; if you set Button's image, it erases its text; if you remove Button's border, it comes back if you press it (grrr); many properties listed in the documentation do not exist; hildon.Window's menu title is split into two subtitles, only one of which you can control; hildon.Controlbar freaks out if it's too small relative to its number of ticks (argh); hildon.Controlbar is a Scale subclass but doesn't operate like a Scale;  if you call set_size_request on a Button, it sets not only its minimum size but also its MAXIMUM size even if an underlying label is longer than the window; SpinButton is totally, completely worthless; on don't get me started on the huge number of TreeView bugs!"
    
    s = Split(children=[Text(name="text1", text=text1), Text(name="text2", text=text2)], name="split1", vertical=True)
    s0 = Split(name="split0")
    s0.add(Text(name="text0", text=text0))
    s0.add(s)
    n.add(s0, tab="Text")
    
    # add some buttons
    t = Table(columns=4)
    n.add(t, tab="Buttons")
    t.add("w/Side Icon")
    t.add(Button(text="Yo", image=Image(xpmData=_leftArrow)))
    t.add("Bigger")
    t.add(Button(text="Yo", image=Image(xpmData=_leftArrow), minimumWidth=200, minimumHeight=80))
    t.add("No Icon")
    t.add(Button(text="Yo"))
    t.add("w/ Icon")
    t.add(Button(image=Image(xpmData=_leftArrow)))
    t.add("No Background")
    t.add(Button(text="Press Me", showBorder=False))
    t.add("Disabled")
    t.add(Button(text="Press Me", enabled=False))
    t.add("Three States")
    t.add(Button(text=["Press Me", "Hey!", "Whoa!"]))
    t.add("w/Icons")
    t.add(Button(text=["Press Me", "Hey!", "Whoa!"], minimumWidth=200,
        image=[Image(xpmData=_leftArrow), Image(xpmData=_rightArrow), Image(xpmData=_bellyButton)]))
    t.add("2 State, Pressed Text")
    t.add(Button(text=["Press Me", "Hey!"], pressedText=["Thanks", "Yeesh"]))
    t.add("w/icons")
    t.add(Button(text=["Press Me", "Hey!", "Whoa!"], pressedText=["Thanks", "Yeesh"], minimumWidth=200,
            image=[Image(xpmData=_leftArrow), Image(xpmData=_rightArrow)],
            pressedImage=Image(xpmData=_bellyButton)))
    t.add("Action")
    l = Label("0", name="label0")
    t.add(Button(text="++", action=lambda state:l.setText("%s" % (int(l.getText()) + 1))))
    t.add(l)
    t.add("<- label is persistent")
    
    # add some miscellaneous
    b = Box(vertical=True)
    n.add(b, tab="Misc")
    
    b2 = Box("SpinButton and its Experimental Replacement", vertical=True)
    g = gtk.SpinButton()
    g.set_range(0,10)
    b2.add(Wrap(g)) # the old
    b2.add(Spinner(minValue=0, maxValue=10, name="spin0"))
    b4 = Box()
    b4.add(Spinner(ticks=["Four", "Score", "And", "Seven", "Years"], noReset=True, name="spin1"))
    b4.add(None, expand=True)
    b4.add(Spinner(add=0, multiply=2, currentValue=1, buttonsRight=True, precision=20, name="spin2"))
    b2.add(b4)
    b.add(b2)
    
    b3 = Box(text="Containers Can Sprout Frames -- but Frame's valign doesn't work", vertical=True)
    b5 = Box()
    b5.add(Label("Labels can have images", image=Image(xpmData=_leftArrow)))
    b5.add(None, expand=True)
    b5.add(Label("Labels can be right justified", image=Image(xpmData=_rightArrow), rightJustified=True))
    b3.add(b5)
    b3.add(Label("Multi-Line labels can have an image. Also note that the SpinButton, a pure gtk widget, interoperates nicely with the toolkit as shown above.", wrappable=True, image=Image(xpmData=_rightArrow)))
    b.add(b3)
    b.add(None, expand=True)
    
    # add some entries
    b = Box(vertical=True)
    n.add(b, tab="Entries")
    b.add(TextField("Hello There", values=["One", "Two", "Three"], name="entry1"))
    b.add(TextField(name="entry2"))
    b.add(TextField(values=["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"], name="entry3"))
    b.add(TextField(persistentHistory=False, name="entry4", includeSpace=False, historyLength=0))
    
    w.show()
    gtk.main()
    savePersistenceData()

print "Call the toolkit's testLibrary() function for a demonstration."
