#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.6.8 on Mon Sep 14 16:04:36 2015
#

import wx
import gettext

class MyDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        # end wxGlade
  
    def create(self, security_probl):
        self.label_1 = wx.StaticText(self, wx.ID_ANY, _(security_probl))
        self.button_1 = wx.Button(self, wx.ID_ANY, _("Ok"))
        self.button_1.Bind(wx.EVT_BUTTON, self.OnOk)
        self.Bind(wx.EVT_CLOSE, self.OnOk) 
        self.__set_properties()
        self.__do_layout()

    def OnOk(self, event):
        self.Destroy()

    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        self.SetTitle(_("Result"))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.label_1, 0, 0, 0)
        sizer_1.Add(self.button_1, 0, 0, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade
