#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.6.8 on Wed Sep  2 21:24:17 2015
#

import wx
from pprint import pprint
# begin wxGlade: dependencies
import gettext
# end wxGlade

class MyFrame(wx.Frame):
  def __init__(self, *args, **kwds):  
    kwds["style"] = wx.DEFAULT_FRAME_STYLE
    wx.Frame.__init__(self, *args, **kwds)

  def create(self, levels, entities, a_levels, add_exc):
    # begin wxGlade: MyFrame.__init__
    self.combo_box = list()
    self.label = list()
    self.level_method = dict()
    self.a_levels = a_levels
    self.add_exc = add_exc
    self.amount_entitites = len(entities)
    i = 0
    for entity in entities:
      self.label.append(wx.StaticText(self, i, _(entity), size = wx.Size (-1, 30)))
      combo_box = wx.ComboBox(self, i, size = wx.Size(-1, 30),choices=[level for level in levels], style=wx.CB_READONLY)
      combo_box.Bind(wx.EVT_COMBOBOX, self.OnSelection)
      self.combo_box.append(combo_box)
      self.level_method [i] = (entity, None)
      i += 1

    self.button_1 = wx.Button(self, wx.ID_ANY, _("Run"))
    self.button_1.Bind(wx.EVT_BUTTON, self.OnRun)
    self.button_2 = wx.Button(self, wx.ID_ANY, _("Close"))
    self.button_2.Bind(wx.EVT_BUTTON, self.OnClose)
    self.button_3 = wx.Button(self, wx.ID_ANY, _("Add Exception"))
    self.button_3.Bind(wx.EVT_BUTTON, self.OnException)
    
    self.__set_properties()
    self.__do_layout()
    # end wxGlade

  def __set_properties(self):
    # begin wxGlade: MyFrame.__set_properties
    self.SetTitle(_("Didfail with security levels"))
    # end wxGlade

  def OnException(self, event):
    self.child = ChildFrame(self)
    self.child.Show()

  def OnClose(self, event):
    dlg = wx.MessageDialog(self, "Do you really want to close this application?","Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
    result = dlg.ShowModal()
    dlg.Destroy()
    if result == wx.ID_OK:
      self.Destroy()
 
  def OnSelection(self, event):
    i = event.GetId()
    level = event.GetString() 
    entity = self.level_method [i] [0]
    self.level_method [i] = (entity, level.encode('ascii'))

  def OnRun(self, event):
    # Obtain selected levels
    tuples = set()
    i = 0
    while (i < self.amount_entitites):
      tuples.add(self.level_method [i])
      i += 1
    self.Destroy()
    self.a_levels(tuples)
    # Create result window 

  def __do_layout(self):
    # begin wxGlade: MyFrame.__do_layout
    sizer_1 = wx.BoxSizer(wx.VERTICAL)
    sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
    sizer_4 = wx.BoxSizer(wx.VERTICAL)
    sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
    sizer_3 = wx.BoxSizer(wx.VERTICAL)

    for label in self.label:
      sizer_3.Add(label, 0, 0, 0)
    for cb in self.combo_box:
      sizer_4.Add(cb, 0, 0, 0)

    sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
    sizer_3.Add(self.button_2, 0, 0, 0)
    sizer_5.Add(self.button_1, 0, 0, 0)
    sizer_5.Add(self.button_3, 0, 0, 0)
    sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)
    sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)
    sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
    self.SetSizer(sizer_1)
    sizer_1.Fit(self)
    self.Layout()
    # end wxGlade

# end of class Main_frame

class ChildFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, None, title='ChildFrame')
        self.parent = parent
        pan = wx.Panel(self)

        self.text_ctrl_3 = wx.TextCtrl(self, wx.ID_ANY, "")
        self.label_1 = wx.StaticText(self, wx.ID_ANY, _("-->"))
        self.text_ctrl_4 = wx.TextCtrl(self, wx.ID_ANY, "")
        self.button_2 = wx.Button(self, wx.ID_ANY, _("Close"))
        self.button_2.Bind(wx.EVT_BUTTON, self.OnClose)
        self.button_3 = wx.Button(self, wx.ID_ANY, _("Close and Save"))
        self.button_3.Bind(wx.EVT_BUTTON, self.OnAdd)
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle(_("Exceptions"))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.GridSizer(2, 3, 0, 0)
        grid_sizer_1.Add(self.text_ctrl_3, 0, 0, 0)
        grid_sizer_1.Add(self.label_1, 0, 0, 0)
        grid_sizer_1.Add(self.text_ctrl_4, 0, 0, 0)
        grid_sizer_1.Add(self.button_2, 0, 0, 0)
        grid_sizer_1.Add(self.button_3, 0, 0, 0)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade
 
    def OnClose(self, event):
        self.Destroy()

    def OnAdd(self, event):
        exc_tuple = self.text_ctrl_3.GetValue(), self.text_ctrl_4.GetValue()
        if self.parent.add_exc(exc_tuple) and (exc_tuple[0] != "") and (exc_tuple[1] != ""):
            self.Destroy()
        else:
            dlg = wx.MessageDialog(self, "Method in exception not found","Error", wx.OK|wx.ICON_ERROR)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                self.Destroy()