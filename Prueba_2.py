import wx
import wx.tools

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(400,200))
        wx.InitAllImageHandlers
        self.Show(True)

app = wx.App(False)
frame = MyFrame(None, 'Small editor')
app.MainLoop()
