from __future__ import print_function # For py 2.7 compat

from IPython.display import display, Javascript
#from IPython.html import widgets
import ipywidgets as widgets
from traitlets import Unicode, Float, List, Dict
import json
import os
import pprint

# XXXX I initially had difficulties directly passing
# complex structures like lists and dicts from the
# Python side to the javascript side.  To work around
# these difficulties the current implementation uses
# JSON encoded string encoding to pass values between
# the two interpreters.  It may be possible to remove
# this approach now or later.

def load_javascript_support(verbose=False):
    """
    Install javascript support required for this module into the notebook.
    """
    my_dir = os.path.dirname(__file__)
    js_filename = os.path.join(my_dir, "canvas.js")
    assert os.path.exists(js_filename)
    if verbose:
        print("loading javascript from", repr(js_filename))
    display(Javascript(js_filename))


class SVGCanvasWidget(widgets.DOMWidget):
    """
    Jupyter notebook widget which presents an SVG canvas.
    """
    
    # The javascript view name.
    _view_name = Unicode('SVGCanvasView', sync=True)
    
    # SVG viewBox
    viewBox = Unicode("0 0 500 500", sync=True)
    view_minx = 0
    view_miny = 0
    view_width = 500
    view_height = 500

    # The bounding box set in response to "fit" command.
    boundingBox = Dict({}, sync=True)
    
    # Canvas width
    width = Float(500, sync=True)
    
    # Canvas height
    height = Float(500, sync=True)
    
    # SVG styling, JSON encoded dictionary
    style = Unicode("{}", sync=True)
    
    # JSON encoded sequence of dictionaries describing actions.
    commands = Unicode("[]", sync=True)
    
    # White separated names of event to watch
    watch_event = Unicode("", sync=True)
    
    # White separated names of event to unwatch
    unwatch_event = Unicode("", sync=True)
    
    # Event captured (sent from js, jason encoded).
    event = Unicode("{}", sync=True)
    
    # Buffered commands, list of dictionary (or None)
    buffered_commands = None
    
    # use this style dictionary if not provided
    default_style = {}
    
    # Set True to enable localized event callbacks
    # If set False then event callbacks attached to descendent elements to
    # the SVG canvas will not fire -- only the global default callback will fire.
    local_events = True
    
    def __init__(self, *pargs, **kwargs):
        super(SVGCanvasWidget, self).__init__(*pargs, **kwargs)
        self.on_trait_change(self.handle_event_change, "event")
        self.name_counter = 0
        self.verbose = False
        self.default_event_callback = None
        self.name_to_callback = {}
        
    def set_event_callback(self, callback):
        "Set the default callback to use if not handled by local callback."
        self.default_event_callback = callback
        
    def handle_event_change(self, att_name, old, new):
        "Dispatch an event sent from javascript to a registered callback."
        if new:
            info = json.loads(new)
            name = info.get("name")
            if self.verbose:
                print ("got event", name)
                print (pprint.pformat(info))
            callback = self.default_event_callback
            if self.local_events:
                callback = self.name_to_callback.get(name, callback)
            if callback is not None:
                callback(info)
    
    def add_command(self, dictionary):
        "Append a command to the command buffer."
        if self.buffered_commands is None:
            self.buffered_commands = []
        self.buffered_commands.append(dictionary)
        
    def send_commands(self):
        "Send all commands in the command buffer to the JS interpreter."
        bc = self.buffered_commands
        if bc:
            self.commands = json.dumps(bc)
        self.buffered_commands = None
        
    def add_element(self, name, tagname, attribute_dict, style_dict=None, text=None, event_callback=None):
        "Add an 'add_element' to the command buffer."
        if name is None:
            # Invent a name if None given.
            self.name_counter += 1
            name = str(tagname) + "_" + str(self.name_counter)
        if style_dict is None:
            style_dict = self.default_style
        command = {
            "command": "add_element",
            "name": name,
            "tag": tagname,
            "atts": attribute_dict,
            "style": style_dict,
            "text": text,
        }
        self.add_command(command)
        if event_callback:
            self.name_to_callback[name] = event_callback
        
    def change_element(self, name, attribute_dict, style_dict=None, text=None):
        "Add a 'change_element' to the command buffer for a named object."
        if style_dict is None:
            style_dict = self.default_style
        command = {
            "command": "change_element",
            "name": name,
            "atts": attribute_dict,
            "style": style_dict,
            "text": text,
        }
        self.add_command(command)
        
    def empty(self):
        "Add a command to empty the canvas to the command buffer."
        command = {"command": "empty"}
        self.add_command(command)
        self.name_to_callback = {}
        
    def delete_names(self, names):
        "Add a command to remove named objects to the command buffer."
        command = {"command": "delete", "names": names}
        self.add_command(command)
        n2c = self.name_to_callback
        for name in names:
            if name in n2c:
                del n2c[name]

    def fit(self, changeView=True):
        "add a 'fit' command to the command buffer (fit to bounding box)"
        command = {"command": "fit", "changeView": changeView}
        self.add_command(command)

    def get_style(self):
        "Get the current SVG style."
        return json.loads(self.style)
    
    def set_style(self, style_dict):
        "Set the current SVG style."
        self.style = json.dumps(style_dict)
        
    def add_style(self, key, value):
        "Add an entry to the SVG style."
        style_dict = self.get_style()
        style_dict[key] = value
        self.set_style(style_dict)

    def set_view_box(self, minx, miny, width, height):
        "Change the SVG view box."
        assert width != 0
        assert height != 0
        self.view_minx = minx
        self.view_miny = miny
        self.view_width = width
        self.view_height = height
        self.viewBox = "%s %s %s %s" % (minx, miny, width, height)
        
    def text(self, name, x, y, text, fill="black", event_cb= None, style_dict=None, **other_attributes):
        "Add command to create a text element to the command buffer."
        tag = "text"
        atts = other_attributes.copy()
        atts["fill"] = fill
        atts["x"] = x
        atts["y"] = y
        self.add_element(name, tag, atts, style_dict, text=text, event_callback=event_cb)

    def line(self, name, x1, y1, x2, y2, color="black", width=None, 
             event_cb=None, style_dict=None, **other_attributes):
        "Add a command to create a line element ot the command buffer."
        tag = "line"
        atts = other_attributes.copy()
        atts["x1"] = x1
        atts["y1"] = y1
        atts["x2"] = x2
        atts["y2"] = y2
        if width:
            atts["stroke-width"] = width
        atts["stroke"] = color
        self.add_element(name, tag, atts, style_dict, event_callback=event_cb)
        
    def circle(self, name, cx, cy, r, fill="black", event_cb=None, style_dict=None,
              **other_attributes):
        "Add a command to create a circle element to the command buffer."
        tag = "circle"
        atts = other_attributes.copy()
        atts["cx"] = cx
        atts["cy"] = cy
        atts["r"] = r
        atts["fill"] = fill
        self.add_element(name, tag, atts, style_dict, event_callback=event_cb)

    def rect(self, name, x, y, width, height, fill="black", event_cb=None, style_dict=None,
            **other_attributes):
        "Add a command to create a rectangle element to the command buffer."
        tag = "rect"
        atts = other_attributes.copy()
        atts["x"] = x
        atts["y"] = y
        atts["width"] = width
        atts["height"] = height
        atts["fill"] = fill
        self.add_element(name, tag, atts, style_dict, event_callback=event_cb)
