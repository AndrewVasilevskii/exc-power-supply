import wx
from mainframe import MainFrame
import multiprocessing
from config import GetConfigurations, APP_NAME


if __name__ == '__main__':
    # list = [1, 3]
    # list2 = [2, 4, 7, 9, 11, 22]
    # li = merge(list, list2)
    # tuple_1 = (1, 3)
    # tuple_2 = (2, 4, 7, 9, 11, 22)
    # tu = merge(tuple_1, tuple_2)\
    # begin = 0
    # print(bin(1))
    # print(bin())
    # number = int(input("input number "))
    # flag = 0
    # while flag != number:
    #     if flag == 0:
    #         begin = -~begin
    #         flag += 1
    #     else:
    #         print('=================')
    #         print(bin(begin))
    #         print(bin(begin << 2**flag))
    #         print(bin(begin^b))
    #         print(bin(begin << 2**flag ^ 0^~begin ))
    #         begin = begin << 2**flag ^ 0^-~begin
    #
    #         flag+=1
    #
    # print(bin(begin))


    # while summ_list.__len__() != len:

    #     print(summ_list)
    #     if item < item_2:
    #
    #         summ_list.append(item)
    #         if list.__len__() != 0:
    #             item = list.pop(0)
    #         else:
    #             print(item, item_2)
    #             print(list)
    #             print(list2)
    #             merge(item_2, list2)
    #             break
    #     elif item_2 < item:
    #         summ_list.append(item_2)
    #         item_2 = list2.pop(0)
    #         if list2.__len__() != 0:
    #             item_2 = list2.pop(0)
    #         else:
    #               print(item, item_2)
    #             print(list)
    #             print(list2)
    #             merge(item, list)
    #             break


    multiprocessing.freeze_support()
    pos, size, style = GetConfigurations()
    app = wx.App()
    frm = MainFrame(None, title=APP_NAME, size=size, pos=pos, style=style)
    # frm.Show()
    app.MainLoop()


# import wx
#
# class MyFrame(wx.Frame):
#     def __init__(self, parent, ID, title):
#         wx.Frame.__init__(self, parent, ID, title)
#
#         self.timer = wx.Timer(self, 1)
#         self.count = 0
#
#         self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
#
#         panel = wx.Panel(self, -1)
#         vbox = wx.BoxSizer(wx.VERTICAL)
#         hbox1 = wx.BoxSizer(wx.HORIZONTAL)
#         hbox2 = wx.BoxSizer(wx.HORIZONTAL)
#         hbox3 = wx.BoxSizer(wx.HORIZONTAL)
#
#         self.gauge = wx.Gauge(panel, -1, 50, size=(250, 25))
#         self.btn1 = wx.Button(panel, wx.ID_OK)
#         self.btn2 = wx.Button(panel, wx.ID_STOP)
#         self.text = wx.StaticText(panel, -1, "Task to be done")
#
#         self.Bind(wx.EVT_BUTTON, self.OnOk, self.btn1)
#         self.Bind(wx.EVT_BUTTON, self.OnStop, self.btn2)
#
#         hbox1.Add(self.gauge, 1, wx.ALIGN_CENTRE)
#         hbox2.Add(self.btn1, 1, wx.RIGHT, 10)
#         hbox2.Add(self.btn2, 1)
#         hbox3.Add(self.text, 1)
#         vbox.Add((0, 50), 0)
#         vbox.Add(hbox1, 0, wx.ALIGN_CENTRE)
#         vbox.Add((0, 30), 0)
#         vbox.Add(hbox2, 1, wx.ALIGN_CENTRE)
#         vbox.Add(hbox3, 1, wx.ALIGN_CENTRE)
#
#         panel.SetSizer(vbox)
#         self.Centre()
#
#     def OnOk(self, event):
#         if self.count >= 50:
#             return
#         self.timer.Start(100)
#         self.text.SetLabel("Task in Progress")
#
#     def OnStop(self, event):
#         if self.count == 0 or self.count >= 50 or not self.timer.IsRunning():
#             return
#         self.timer.Stop()
#         self.text.SetLabel("Task Interrupted")
#         wx.Bell()
#
#     def OnTimer(self, event):
#         self.count = self.count +1
#         self.gauge.SetValue(self.count)
#         if self.count == 50:
#             self.timer.Stop()
#             self.text.SetLabel("Task Completed")
#
# class MyApp(wx.App):
#     def OnInit(self):
#         frame = MyFrame(None, -1, "gauge.py")
#         frame.Show(True)
#         return True
#
#
# app = MyApp(0)
# app.MainLoop()
# import time
# import wx
# from wx.lib.pubsub import pub
#
#
# class Window(wx.Frame):
#     def __init__(self):
#         wx.Frame.__init__(self, None, title="wxGauge")
#         self.sizer = wx.BoxSizer(wx.VERTICAL)
#         self.gauge = wx.Gauge(self, range=10)
#         self.btn = wx.Button(self, label="Start process")
#         self.sizer.Add(self.gauge)
#         self.sizer.Add(self.btn)
#         self.SetSizerAndFit(self.sizer)
#         pub.subscribe(self.update, "update")
#         self.btn.Bind(wx.EVT_BUTTON, self.OnClick)
#
#         self.Bind(wx.EVT_TIMER, self.TimerHandler)
#         self.timer = wx.Timer(self)
#         self.gaugeIndex = 0
#         self.Show()
#
#     def TimerHandler(self, event):
#         self.gaugeIndex += 1
#         pub.sendMessage("update", msg=self.gaugeIndex)
#         if self.gaugeIndex == 10:
#             self.timer.Stop()
#
#     def update(self, msg):
#         self.gauge.SetValue(msg)
#
#     def OnClick(self, evt):
#         self.timer.Start(1000)
#
#
# if __name__ == '__main__':
#     app = wx.App(redirect=False)
#     Window()
#     app.MainLoop()