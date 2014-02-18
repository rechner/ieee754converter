#!/usr/bin/env python

"""
Simple app for converting between float, double, and IEEE754 binary
representations.
"""

__author__ = "Zachary Sturgeon <zws258@email.vccs.edu>"

import struct
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Canvas
from kivy.graphics import Color, Rectangle

class ToggleBar(BoxLayout):  
  """
  A widget to generate a large switch bank for manipulating binary values.
    :param n: Length of the switchbank to create.
    :type n: int
  """
  def __init__(self, **kwargs):
    barsize = kwargs.pop('n', 1)
    self.value = "0" * barsize
    self.orientation = 'vertical'
    self.color = kwargs.pop('color', (0.2, 0.2, 0.2, 0.5))
    self.callback = kwargs.pop('callback', lambda: None)
    self.height = 70
    self.padding = 10
    self.spacing = 10
    self.size_hint = (1, None)
    super(ToggleBar, self).__init__(**kwargs)
    self.checkboxes = []
    box = BoxLayout(orientation='horizontal')
    box.size_hint = (1, 0.6)
    
    for n in range(barsize):
      checkbox = CheckBox(size_hint=(1.0/barsize, 0.70))
      checkbox.bind(active=self.checkbox_toggle)
      box.add_widget(checkbox)
      self.checkboxes.append(checkbox)
    
    if 'label' in kwargs:
      self.label = Label(text=kwargs['label'], markup=True, size_hint=(1, 0.3))
      self.add_widget(self.label)
    
    self.add_widget(box)
    self.value_label = Label(text="0"*barsize)
    self.value_label.size_hint = (1, 0.3)
    self.add_widget(self.value_label)  
    
  def set_value(self, binstring):
    #Truncate to beginning of string
    if len(binstring) > len(self.checkboxes):
      binstring = binstring[0:len(self.checkboxes)]
      
    for index, bit in enumerate(binstring):
      if bit == '1':
        self.checkboxes[index].active = True
      else:
        self.checkboxes[index].active = False
    self.value_label.text = binstring
    self.value = binstring
    
  def checkbox_toggle(self, checkbox, value):
    binstring = ""
    for checkbox in self.checkboxes:
      if checkbox.active:
        binstring += "1"
      else:
        binstring += "0"
    
    #Update the label:
    self.value_label.text = binstring
    self.value = binstring
    self.callback()

class ToggleBarBlock(ToggleBar):
  """
  Same as ToggleBar, but arranged in a grid for better presentation of 
  particularly long binary strings.  Takes n and breakpoint arguments.

    :param n: Length of the switchbank to generate.
    :type n: int
    :param breakpoint: A new row is created after this point.
    :type breakpoint: int
  """
  def __init__(self, **kwargs):
    barsize = kwargs.pop('n', 1)
    self.value = "0" * barsize
    self.orientation = 'vertical'
    self.color = kwargs.pop('color', (0.2, 0.2, 0.2, 0.5))
    self.callback = kwargs.pop('callback', lambda: None)
    self.height = 70
    self.padding = 10
    self.spacing = 10
    self.size_hint = (1, None)
    super(ToggleBar, self).__init__(**kwargs)
    self.checkboxes = []
    
    master_box = BoxLayout(orientation='vertical')
    box = BoxLayout(orientation='horizontal')
    box.size_hint = (1, 0.6)
    for n in range(barsize):
      checkbox = CheckBox(size_hint=(1.0/barsize, 0.70))
      checkbox.bind(active=self.checkbox_toggle)
      self.checkboxes.append(checkbox)
      
      #If bit position is divisible by the breaking point, add a new row:
      if ((n + 1) % kwargs['breakpoint']) == 0:
        box.add_widget(checkbox)
        master_box.add_widget(box)
        box = BoxLayout(orientation='horizontal')
        box.size_hint = (1, 0.6)
      else:
        box.add_widget(checkbox)
    
    if 'label' in kwargs:
      self.label = Label(text=kwargs['label'], markup=True, size_hint=(1, 0.3))
      self.add_widget(self.label)
    
    self.add_widget(master_box)
    self.value_label = Label(text="0"*barsize)
    self.value_label.size_hint = (1, 0.3)
    self.add_widget(self.value_label)  

class RootWidget(BoxLayout):
  """
  Root frame for the application.  This contains callback bindings for the
  button actions and is accessible from the named context inside the kv layout.
  """
  def __init__(self, **kwargs):
    super(RootWidget, self).__init__(**kwargs)
    
  def convert_float(self, textbox, hex_textbox):
    if textbox.text == "":
      return
      
    #Convert float to binary string and set checkboxes:
    try:
      binary_string = float_to_binary(float(textbox.text))
    except ValueError:
      return
    self.sign.set_value(binary_string[0])
    self.exponent.set_value(binary_string[1:9])
    self.mantissa.set_value(binary_string[9:])
    
    #Coerce the input value:
    self.bin_to_float()

    #Convert float to hex and display in text input:
    hex_textbox.text = hex(int(binary_string, 2))
    
  def convert_hex_float(self):
    if self.float_hex == "":
      return
      
    try:
      binary_string = hex_to_bin(self.float_hex.text)
    except ValueError:
      return
    self.sign.set_value(binary_string[0])
    self.exponent.set_value(binary_string[1:9])
    self.mantissa.set_value(binary_string[9:32])
    
    #Convert to float:
    self.bin_to_float()
    
  def convert_hex_double(self):
    if self.double_hex == "":
      return
      
    try:
      binary_string = hex_to_bin64(self.double_hex.text)
    except ValueError:
      return
    self.sign_double.set_value(binary_string[0])
    self.exponent_double.set_value(binary_string[1:12])
    self.mantissa_double.set_value(binary_string[12:64])
    
    #Convert to float:
    #~ self.float_decimal.text = str(float.fromhex(self.float_hex.text))

    #~ self.bin_to_double()
    
  def convert_double(self, textbox, hex_textbox):
    if textbox.text == "":
      return
      
    try:
      binary_string = double_to_binary(float(textbox.text))
    except ValueError:
      return
    
    self.sign_double.set_value(binary_string[0])
    
    
    self.exponent_double.set_value(binary_string[1:12])
    self.mantissa_double.set_value(binary_string[12:])
    
    hex_textbox.text = hex(int(binary_string, 2))
    
    #Coerce the input value
    self.bin_to_double()
    
  def bin_to_float(self):
    self.binary_string = "{}{}{}".format(self.sign.value,
      self.exponent.value, self.mantissa.value)
    bfloat = binary_to_float(self.binary_string)
    self.float_decimal.text = bfloat
    self.float_hex.text = hex(int(self.binary_string, 2))
    
  def bin_to_double(self):
    self.binary_string = "{}{}{}".format(self.sign_double.value,
      self.exponent_double.value, self.mantissa_double.value)
    bdouble = binary_to_double(self.binary_string)
    #~ import pdb; pdb.set_trace()
    
    self.double_hex.text = hex(int(self.binary_string, 2))
    self.double_decimal.text = bdouble

class IEEEApp(App):
  """
  Application build logic.  Builds the accordion frames and switch banks.
  """
  def build(self):
    tw = RootWidget(orientation='vertical')
    
    # Set up 32-bit accordion tab:
    tw.sign = ToggleBar(n=1, label="[b]Sign[/b]", callback=tw.bin_to_float, \
                        color=(0.8, 0.2, 0.2, 0.5))
    tw.exponent = ToggleBar(n=8, label="[b]Exponent[/b]", \
                            callback=tw.bin_to_float, \
                            color=(0.2, 0.8, 0.2, 0.5))
    tw.mantissa = ToggleBar(n=23, label="[b]Mantissa[/b]", \
                            callback=tw.bin_to_float)
    
    tw.sign.size_hint = (0.1, None)
    tw.exponent.size_hint = (0.4, None)
    tw.mantissa.size_hint = (1, None)
      
    box32 = BoxLayout(orientation='horizontal')
    box32.add_widget(tw.sign)
    box32.add_widget(tw.exponent)
    box32.add_widget(tw.mantissa)
    
    # Set up 64-bit accordion tab:
    tw.sign_double = ToggleBar(n=1, color=(0.8, 0.2, 0.2, 0.5),
                               label="[b]Sign[/b]", callback=tw.bin_to_double)
    tw.exponent_double = ToggleBar(n=11, color=(0.2, 0.8, 0.2, 0.5),
                                   label="[b]Exponent[/b]",
                                   callback=tw.bin_to_double)
    tw.mantissa_double = ToggleBarBlock(n=52, breakpoint=26, 
                                        label="[b]Mantissa[/b]",
                                        callback=tw.bin_to_double)
    
    box64 = BoxLayout(orientation='horizontal', size_hint=(1, 0.4))
    box64.add_widget(tw.sign_double)
    box64.add_widget(tw.exponent_double)
    tw.mantissa_double.size_hint = (1, 0.5)
    
    tw.toggle32.add_widget(box32)  
    tw.toggle64.add_widget(box64)
    tw.toggle64.add_widget(tw.mantissa_double)
    #tw.toggle64.add_widget(ToggleBar(n=64))
    return tw
  
#Functions for converting between IEEE754 binary 32/64-bit representations: 
def float_to_binary(num):
  """
  Converts a python float to a 32-bit single precision IEEE754 binary string.
  """
  try:
	return ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!f', num))
  except OverflowError:
		if str(num)[0] == '-':
			return float_to_binary(float('-inf'))
		else:
			return float_to_binary(float('inf'))
  
def binary_to_float(binstring):
  """
  Converts a 32-bit single precision binary string to a float.
  Raises a ValueError if the input is not 32 characters long.
  """
  if len(binstring) != 32:
    raise ValueError("Binary number must be 32 bits long")
  chars = "".join(chr(int(binstring[i:i+8], 2)) for i in xrange(0, len(binstring), 8))
  return str(struct.unpack('!f', chars)[0])
  
def double_to_binary(num):
  """
  Converts a python float to a 64-bit double precision IEEE754 binary string.
  """
  return bin(struct.unpack('!Q', struct.pack('!d', num))[0])[2:].zfill(64)
  
def binary_to_double(binstring):
  """
  Converts a 64-bit double precision binary string to a float.
  Raises a ValueError if the input is not 64 characters long.
  """
  if len(binstring) != 64:
    raise ValueError("Binary number must be 64 bits long")
  chars = "".join(chr(int(binstring[i:i+8], 2)) for i in xrange(0, len(binstring), 8))
  return str(struct.unpack('!d', chars)[0])

def hex_to_bin(hexstring):
  return bin(int(hexstring, 16))[2:].zfill(32)
  
def hex_to_bin64(hexstring):
  return bin(int(hexstring, 16))[2:].zfill(64)
  

if __name__ == '__main__':
  IEEEApp().run()
