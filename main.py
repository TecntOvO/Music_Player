import re
import os
import json
import time
import ctypes
import random
import mutagen
import numpy as np
import tkinter as tk
from pygame import mixer as mx
import tkinter.messagebox as tkmb
import tkinter.filedialog as tkfd
from Get_Lyrics import Get_Lyric
from Mythreading import myThread
from Music_Info import Music_Info


class MusicPlayer:
    def __init__(self, Body):

        # 初始化变量
        self.body = Body  # 窗口实例
        self.GetLyric_windows = None  # 歌词获取窗口实例
        self.Music_Info_Windows = None  # 歌词详情窗口实例
        self.body.title("音乐播放器")
        self.body.protocol("WM_DELETE_WINDOW", self.Quit)

        # 窗口大小与窗口位置居中设置
        self.ww, self.wh = 1000, 800  # 600 400
        self.sw, self.sh = self.body.winfo_screenwidth(), self.body.winfo_screenheight()
        self.body.geometry(f"{self.ww}x{self.wh}+{int((self.sw - self.ww) / 2)}+{int((self.sh - self.wh) / 2)}")
        self.body.resizable(width=False, height=False)

        self.Music_File = list()  # 保存所有在列表中音乐的路径，顺序一致
        self.Music_Playing = ('direction', 'number')  # 保存当前正在播放音乐文件的路径与序号
        self.Music_Pause = False  # 音乐是否正在暂停
        self.PlayMode = 'list-Circle'  # 记录音乐播放方式，list-Circle为列表循环，single-Circle为单曲循环,Random-circle为随机播放
        self.IfTime_Counting = True
        self.IfLyric_Playing = True
        self.Music_Time = tk.StringVar()  # 记录音乐播放时间进度
        self.Music_Time.set('0:00')  # 初始化播放进度0:00
        self.Previous_Time = None  # 函数临时变量，记录在编辑时间前的时间
        self.Time_Offset = 0  # 时间偏移量
        self.Volume_Show = True  # 是否显示音量条
        self.Music_Info = None  # 当前播放音乐信息对象
        self.Lyric_source = None  # 记录歌词来源
        self.Lyric_Path = None  # 记录歌词所在路径
        self.Lyric_data = dict()  # 歌词数据
        self.Previous_lyric_index = np.array([])  # 临时记录前一时间高亮歌词索引
        self.Lyric_TimeList = np.array([])  # 每句歌词时间的列表，单位为秒，供播放时匹配时间用
        self.Color_LyricPlaying = 'orange'  # 高亮歌词颜色
        self.BT_text = ['退出', '关于', '添加', '删除', '歌曲详情', '歌词获取']
        self.BT_font = '微软雅黑'  # 主界面按钮字体
        self.info = "作者:许栋凯\n学号:202234610121"  # 版权信息

        # 图片
        self.__photo_Icon = tk.PhotoImage(file="./image/icon.png")
        self.__photo_Play = tk.PhotoImage(file="./image/play.png")
        self.__photo_Stop = tk.PhotoImage(file="./image/stop.png")
        self.__photo_Last = tk.PhotoImage(file="./image/last.png")
        self.__photo_Next = tk.PhotoImage(file="./image/next.png")
        self.__photo_volume = tk.PhotoImage(file="./image/volume.png")
        self.__photo_list_circle = tk.PhotoImage(file="./image/list_circle.png")
        self.__photo_single_circle = tk.PhotoImage(file="./image/single_circle.png")
        self.__photo_random_circle = tk.PhotoImage(file="./image/random_circle.png")

        # 窗口图标替换
        self.body.iconphoto(False, self.__photo_Icon)

        # 音乐播放列表相关组件
        self.PlayList_Box = tk.Listbox(self.body, width=21, bg='#f9fff0', selectbackground='#cffa8e', selectforeground='#000000',
                             activestyle='dotbox', cursor='hand2', relief='flat')
        Sl1 = tk.Scrollbar(self.body, width=20)
        Sl2 = tk.Scrollbar(self.body, orient='horizontal')
        self.PlayList_Box.config(xscrollcommand=Sl2.set, yscrollcommand=Sl1.set)
        Sl1.config(command=self.PlayList_Box.yview)
        Sl2.config(command=self.PlayList_Box.xview)
        Sl1.place(x=980, y=70, height=510)
        Sl2.place(x=744, y=50, height=20, width=240)
        self.PlayList_Box.bind("<Double-Button-1>", self.Music_play)
        self.PlayList_Box.focus_set()
        self.PlayList_Box.place(x=744, y=70, height=500)

        # 按钮组件
        self.QuitB = tk.Button(self.body, text=self.BT_text[0], font=(self.BT_font, 10), bg='#FFFFFF',
                               activebackground='#dff5f4',
                               width=5, relief='groove', command=self.Quit)
        self.AboutB = tk.Button(self.body, text=self.BT_text[1], font=(self.BT_font, 10), bg='#FFFFFF',
                                activebackground='#dff5f4',
                                width=5, relief='groove', command=self.Info_show)
        self.AddB = tk.Button(self.body, text=self.BT_text[2], font=(self.BT_font, 10), bg='#FFFFFF',
                              activebackground='#dff5f4',
                              width=5, relief='groove', command=self.MusicList_Import)
        self.DeleteB = tk.Button(self.body, text=self.BT_text[3], font=(self.BT_font, 10), bg='#FFFFFF',
                                 activebackground='#dff5f4',
                                 width=5, relief='groove', command=self.MusicList_Delete, state="disabled")
        self.Music_InfoB = tk.Button(self.body, text=self.BT_text[4], font=(self.BT_font, 10), bg='#FFFFFF',
                                     activebackground='#dff5f4',
                                     width=7, relief='groove', command=self.Music_Info_Show, state='disabled')
        self.PlayB = tk.Button(self.body, bg='#FFFFFF', activebackground='#dff5f4', relief='flat', bd=0,
                               image=self.__photo_Play, command=self.Music_play)
        self.LastB = tk.Button(self.body, bg='#FFFFFF', activebackground='#dff5f4', relief='flat', bd=0,
                               image=self.__photo_Last, command=lambda: self.Change_Music('Last'))
        self.NextB = tk.Button(self.body, bg='#FFFFFF', activebackground='#dff5f4', relief='flat', bd=0,
                               image=self.__photo_Next, command=lambda: self.Change_Music('Next'))
        self.VolumeB = tk.Button(self.body, bg='#FFFFFF', activebackground='#dff5f4', relief='flat', bd=0,
                                 image=self.__photo_volume, command=self.VolumeScale_Show)
        self.PlayModeB = tk.Button(self.body, bg='#FFFFFF', activebackground='#dff5f4', relief='flat', bd=0,
                                   image=self.__photo_list_circle, command=self.Play_Mode)
        self.LyricGetB = tk.Button(self.body, text=self.BT_text[5], font=(self.BT_font, 10), bg='#FFFFFF',
                                   activebackground='#dff5f4',
                                   width=7, relief='groove', command=self.Lyric_Get_Windows)

        self.QuitB.place(x=910, y=740, height=40)
        self.AboutB.place(x=20, y=740, height=40)
        self.AddB.place(x=750, y=5, height=40)
        self.DeleteB.place(x=860, y=5, height=40)
        self.Music_InfoB.place(x=100, y=740, height=40)
        self.PlayB.place(x=320, y=600)
        self.LastB.place(x=200, y=610)
        self.NextB.place(x=450, y=610)
        self.VolumeB.place(x=580, y=620)
        self.PlayModeB.place(x=80, y=620)
        self.LyricGetB.place(x=200, y=740, height=40)

        # 时间显示组件
        self.TotalTime_Show = tk.Label(self.body, text='0:00')
        self.Playing_TimeST = tk.Entry(self.body, bg='#f0f0f0', bd=0, textvariable=self.Music_Time, width=4,
                                       state='disabled')
        self.Playing_TimeST.bind('<Button-1>', lambda event: self.Time_Edit('Edit'))
        self.Playing_TimeST.bind('<Return>', lambda event: self.Time_Edit('Confirm'))
        self.TotalTime_Show.place(x=630, y=510)
        self.Playing_TimeST.place(x=53, y=510)

        # 进度条组件
        self.Schedule_Bar = tk.Scale(self.body, orient='horizontal', width=30, length=620, resolution=1,
                                     showvalue=False, state='disabled', from_=0,
                                     command=lambda event: self.Time_Edit('Scrollbar Edit'))
        self.Schedule_Bar.bind('<Button-1>', lambda event: self.Time_Edit('Edit'))
        self.Schedule_Bar.bind('<ButtonRelease-1>', lambda event: self.Time_Edit('Confirm'))
        self.Schedule_Bar.place(x=50, y=540)

        # 音量滚动条组件
        self.SoundS = tk.Scale(self.body, width=20, sliderlength=15, length=150, font='宋体', troughcolor='#dff5f4',
                               activebackground='#a7aafa', borderwidth=3, relief='flat', command=self.Music_VolumeSet,
                               from_=0, to=100, showvalue=False, orient='horizontal')
        self.SoundS.set(40)
        self.Music_VolumeSet(40)

        # 歌词框组件
        Sl3 = tk.Scrollbar(self.body, orient='horizontal')
        self.Lyric_Box = tk.Listbox(self.body, bg='#ffffff', selectbackground='#cffa8e', selectforeground='#000000',
                                    activestyle='dotbox', cursor='hand2', relief='flat', font=('微软雅黑', 10),
                                    selectmode='single', justify='center')
        self.Lyric_Box.config(xscrollcommand=Sl3.set)
        Sl3.config(command=self.Lyric_Box.xview)
        self.Lyric_Box.place(x=40, y=40, height=420, width=650)
        Sl3.place(x=40, y=15, width=650)
        self.Lyric_Box.bind('<Control-MouseWheel>', self.Lyric_FontChange)

        # 歌曲名称显示组件
        self.MusicName_Show = tk.Label(self.body, justify='center')
        self.MusicName_Show.place(x=62, y=480, width=600)

    def MusicList_Import(self):

        # 准备工作
        Import_File = tkfd.askopenfilenames(
            filetypes=[('MP3/OGG媒体文件', ['*.mp3', '*.ogg'])])  # 调出文件载入窗口
        ExistList = list()  # 临时变量，保存那些已经存在与列表中的文件名

        # 正则化处理与筛查环节，原理即为遍历寻找重复，不存在着保存到self.Music_File中并插入列表
        for fire_directory in Import_File:
            IsExist = False
            for Music_File in self.Music_File:
                # 判断是否导入的音乐已经在列表中了
                if fire_directory == Music_File:
                    IsExist = True
                    ExistList.append(re.findall(r"^[^.]+", re.findall(r'[^\\/:*?"<>|\r\n]+$', fire_directory)[0])[0])
                    break
            if not IsExist:
                self.Music_File.append(fire_directory)
                self.PlayList_Box.insert(tk.END,
                               re.findall(r"^[^\\.]+", re.findall(r'[^\\/:*?"<>|\r\n]+$', fire_directory)[0])[0])

        # 如果该变量中有数据，说明有重复文件存在
        if ExistList:
            temp_str = "，".join(ExistList)  # 将列表中每个文件名用逗号分隔
            tkmb.showinfo("提示", f"歌曲 {temp_str} 已经存在于播放列表中，请勿重复添加")  # 再以提示弹窗进行说明并显示重复文件名

        # 如果文件库里面有数据说明列表中有歌曲，可以开启删除键
        if self.Music_File:
            self.DeleteB.config(state="normal")

        # 为列表提供交错着色
        for j in range(len(self.Music_File)):
            if j % 2:
                self.PlayList_Box.itemconfig(j, bg='#d2e8f7')

    def MusicList_Delete(self):
        # 如果列表中有选中项，且选中项恰好为播放的歌曲，如果歌曲正在播放中，不允许删除
        if self.PlayList_Box.curselection() and self.Music_Playing[1] == self.PlayList_Box.curselection()[0] and mx.music.get_busy():
            tkmb.showerror('错误', "当前歌曲正在播放中!")  # 以弹窗形式说明

        # 但是歌曲不在播放，那么可以删除
        elif self.PlayList_Box.curselection() and self.Music_Playing[1] == self.PlayList_Box.curselection()[0] and not mx.music.get_busy():
            mx.music.stop()  # 停止音乐使其不能再通过播放函数播放

            # 删除相关数据
            temp_data = self.PlayList_Box.curselection()[0]
            self.PlayList_Box.delete(temp_data)
            self.Music_File.pop(temp_data)

            # 由于是对当前播放音乐删除，故没有播放的音乐，需要对播放器进行初始化
            self.Music_Time.set('0:00')
            self.TotalTime_Show.config(text='0:00')
            self.Schedule_Bar.set(0)
            self.Schedule_Bar.config(state='disabled')
            self.Playing_TimeST.config(state='disabled')
            self.Music_InfoB.config(state='disabled')
            self.Music_Playing = ('direction', 'number')
            self.Lyric_Box.delete(0, 'end')
            self.MusicName_Show.config(text='')

        # 如果不是当前播放音乐且在列表中选中其中一项，进入常规删除环节
        elif self.PlayList_Box.curselection():
            # 删除对应歌曲数据
            temp_data = self.PlayList_Box.curselection()[0]
            self.PlayList_Box.delete(temp_data)
            self.Music_File.pop(temp_data)

        # 上述情况都不满足，只能说明没有选中列表佛任何一项，弹窗警告
        else:
            tkmb.showerror('错误', "请选择要从列表中删除的音乐")

        # 进行完上面任何代码后对列表进行一次检查，如果为空，则停用删除键
        if not self.Music_File:
            self.DeleteB.config(state="disabled")
            self.Playing_TimeST.config(state='disabled')
            self.Schedule_Bar.config(state='disabled')

        # 为列表提供交错着色
        for j in range(len(self.Music_File)):
            if j % 2:
                self.PlayList_Box.itemconfig(j, bg='#d2e8f7')

    def VolumeScale_Show(self):

        # 如果当前音量条正在隐藏，显示即可
        if self.Volume_Show:
            self.SoundS.place(x=622, y=620)
            self.Volume_Show = False

        # 反之隐藏即可
        else:
            self.SoundS.place_forget()
            self.Volume_Show = True

    @staticmethod
    def Music_VolumeSet(volume):

        # 将进度条0~100分度值转化为0.0~1.0之间并设置
        mx.music.set_volume(int(volume) / 100)

    def Music_play(self, If_FromList=None, If_Play=None, Replay: bool = False):
        # 只有在音乐播放时，并且只能通过点击暂停按钮暂停
        if mx.music.get_busy() and not If_FromList and not If_Play:

            mx.music.pause()

            self.IfTime_Counting = False  # 让线程停止
            self.IfLyric_Playing = False
            self.PlayB.config(image=self.__photo_Play)  # 将图标改为暂停图标
            self.Music_Pause = True  # 置音乐暂停播放状态为真

        # 先确保列表中有音乐（可能删除了）并且是暂停过的，并且是点击了暂停键的才可以恢复播放
        elif self.Music_File and self.Music_Pause and not If_FromList and not If_Play:
            # 确保音乐不在播放
            if not mx.music.get_busy():
                mx.music.unpause()

                self.IfTime_Counting = True
                self.IfLyric_Playing = True
                myThread(self.Auto_play, 'Second', True).perform()  # 重新创建计时线程并运行
                myThread(self.Auto_Lyric_Play, 'Lyric', True).perform(False)
                self.PlayB.config(image=self.__photo_Stop)  # 将图标改为播放图标

        # 为支持单曲播放而写，要求播放模式为单曲循环或者列表中只有一首歌，虽然可在play中置-1实现，但是不方便中断
        elif Replay or self.PlayMode == 'single_Circle' and not If_FromList:
            # 此处代表当前正在播放音乐文件的路径与序号(后者)为初始化状态，为首次播放，既之前没有音乐播放
            if self.Music_Playing[1] == 'number':

                # 音乐首次播放准备，与上面相同
                self.Music_Playing = (
                    self.Music_File[self.PlayList_Box.curselection()[0]], self.PlayList_Box.curselection()[0])  # 设置当前播放音乐路径与序号
                mx.music.load(self.Music_Playing[0])  # 载入音乐
                self.Lyric_Show()  #
                self.Music_Info = mutagen.File(self.Music_Playing[0])  # 载入播放音乐信息
                self.Music_InfoB.config(state='normal')
                self.Schedule_Bar.config(to=int(self.Music_Info.info.length))  # 设置进度条分值
                self.TotalTime_Show.config(
                    text=f"{int(self.Music_Info.info.length // 60)}:{int(self.Music_Info.info.length - (self.Music_Info.info.length // 60) * 60):02d}")  # 设置右上角音乐播放总时间

            # 否则说明此前有播放过或正在播放歌曲,中止音乐播放即可
            else:
                mx.music.stop()

            # 进入播放处理环节，与上面相同
            self.Time_Offset = 0
            self.Lyric_Box.yview_moveto(0)
            mx.music.play()
            self.IfTime_Counting = True  # 让计时循环得以进行
            self.IfLyric_Playing = True
            myThread(self.Auto_play, 'Second', True).perform()  # 创建计时线程并运行
            myThread(self.Auto_Lyric_Play, 'Lyric', True).perform(False)  # 创建歌词录播线程并运行，同时不清空历史高亮歌词索引
            self.Playing_TimeST.config(state='normal', bg='#f0f0f0')  # 开启时间编辑框功能
            self.Schedule_Bar.config(state='normal')  # 开启进度条拖拽功能
            self.PlayB.config(image=self.__photo_Stop)  # 更改图标为暂停图标

        # 用于对要切换播放歌曲提供支持，要求列表选择项与正在播放项目不同，并不处于单曲循环或者列表一首歌的情况
        elif self.PlayList_Box.curselection() and self.PlayList_Box.curselection()[0] != self.Music_Playing[1] and If_FromList or If_Play:
            # 预处理环节
            mx.music.stop()
            self.IfLyric_Playing = False
            time.sleep(0.2)
            self.Music_Playing = (
                self.Music_File[self.PlayList_Box.curselection()[0]], self.PlayList_Box.curselection()[0])  # 设置当前播放音乐路径与序号

            # 音乐准备环节
            mx.music.load(self.Music_Playing[0])  # 载入音乐
            self.Lyric_Show()
            self.Music_Info = mutagen.File(self.Music_Playing[0])  # 载入播放音乐信息
            self.Music_InfoB.config(state='normal')  # 开启获取歌曲详情按钮
            self.Schedule_Bar.config(to=int(self.Music_Info.info.length))  # 设置进度条分值
            self.TotalTime_Show.config(
                text=f"{int(self.Music_Info.info.length // 60)}:{int(self.Music_Info.info.length - (self.Music_Info.info.length // 60) * 60):02d}")  # 设置右上角音乐播放总时间

            # 通过读取歌曲标签文件获取歌名
            for key in self.Music_Info.tags.keys():
                if key == 'TIT2':
                    self.MusicName_Show.config(text=self.Music_Info.tags['TIT2'].text[0])
                    break
                elif key == 'title':
                    self.MusicName_Show.config(text=self.Music_Info.tags['title'][0])
                    break

            self.Time_Offset = 0  # 设置音乐时长位移为0
            self.Lyric_Box.yview_moveto(0)  # 将歌词滚动至顶部

            # 音乐播放与信息处理环节
            mx.music.play()
            self.IfTime_Counting = True
            self.IfLyric_Playing = True
            myThread(self.Auto_play, 'Second', True).perform()  # 创建计时线程并运行
            myThread(self.Auto_Lyric_Play, 'Lyric', True).perform(True)  # 创建歌词轮播线程并运行
            self.Playing_TimeST.config(state='normal', bg='#f0f0f0')  # 开启时间编辑框功能
            self.Schedule_Bar.config(state='normal')  # 开启进度条拖拽功能
            self.PlayB.config(image=self.__photo_Stop)  # 更改图标为暂停图标

    def Change_Music(self, order: str):

        # 当且仅当音乐数目大于1，已经播放过音乐并且播放模式为列表循环才进入一般切换播放歌曲模式
        if len(self.Music_File) > 1 and self.Music_Playing[1] != 'number' and self.PlayMode == 'list-Circle':

            # 按的是下一首按钮
            if order == 'Next':
                self.PlayList_Box.selection_clear(0, len(self.Music_File))  # 清空列表选项

                # 如果切换前的歌曲不是列表中最后一首
                if self.Music_Playing[1] != len(self.Music_File) - 1:

                    self.PlayList_Box.selection_set(self.Music_Playing[1] + 1)  # 基于前一播放音乐序号决定下一首歌而非所选项，避免不必要的麻烦
                    self.Music_play(If_Play=True)  # 播放音乐

                # 否则直接切换到列表中的第一首
                else:
                    self.PlayList_Box.selection_set(0)
                    self.Music_play(If_Play=True)

            # 按的是上一首按钮
            if order == 'Last':
                self.PlayList_Box.selection_clear(0, len(self.Music_File))  # 清空列表选项

                # 如果切换前的歌曲不是列表中第一首
                if self.Music_Playing[1]:
                    self.PlayList_Box.selection_set(self.Music_Playing[1] - 1)  # 基于前一播放音乐序号决定下一首歌而非所选项，避免不必要的麻烦
                    self.Music_play(If_Play=True)  # 播放音乐

                # 否则直接切换到列表最后一首
                else:
                    self.PlayList_Box.selection_set(len(self.Music_File) - 1)
                    self.Music_play(If_Play=True)

        # 如果列表音乐个数大于1并且有播放过音乐，同时播放模式为随机模式
        elif len(self.Music_File) > 1 and self.Music_Playing[1] != 'number' and self.PlayMode == 'random-Circle':

            # 此处是为循环产生一个不等于上一首歌序号的随机整数
            while True:
                random_order = random.randint(0, len(self.Music_File) - 1)
                if random_order != self.Music_Playing[1]:
                    break

            self.PlayList_Box.selection_clear(0, len(self.Music_File))  # 清空列表选项
            self.PlayList_Box.selection_set(random_order)  # 设置播放音乐序号为所给随机数
            self.Music_play(If_Play=True)  # 播放音乐

        # 如果音乐播放列表中只有一首歌，播放过音乐并且播放模式为单曲循环
        elif self.Music_Playing[1] != 'number' and len(self.Music_File) == 1 or self.PlayMode == 'single_Circle':
            self.Music_play(If_Play=True, Replay=True)  # 直接告诉播放音乐方法单曲循环即可

    def Play_Mode(self):
        # 切换播放模式
        if self.PlayMode == 'single_Circle':
            self.PlayMode = 'random-Circle'
            self.PlayModeB.config(image=self.__photo_random_circle)
        elif self.PlayMode == 'list-Circle':
            self.PlayMode = 'single_Circle'
            self.PlayModeB.config(image=self.__photo_single_circle)
        elif self.PlayMode == 'random-Circle':
            self.PlayMode = 'list-Circle'
            self.PlayModeB.config(image=self.__photo_list_circle)

    def Time_Edit(self, state: str):

        # 如果为进度条拖动，直接相当于对时间的编辑
        # 对滚动条调节时间提供支持，同时其就是另外一种编辑时间方式，很好的避免了自动移动也会执行该命令的问题，因为时间与改变时一致则无效
        if state == 'Scrollbar Edit':
            self.Music_Time.set(
                f"{int(self.Schedule_Bar.get() // 60)}:{int(self.Schedule_Bar.get() % 60):02d}")

        # 如果为点击时间编辑处编辑，并且有播放过音乐
        elif state == 'Edit' and self.Music_Playing[1] != 'number':
            self.Previous_Time = self.Music_Time.get()  # 先保存点击时显示的时间，用来判断有没有修改时间
            self.IfTime_Counting = False  # 让计时线程中断
            self.Playing_TimeST.config(bg='#ffffff')  # 将编辑框背景改为白色

        # 如果回车确认编辑框中可能修改过的时间
        elif state == 'Confirm' and self.Music_Playing[1] != 'number':

            # 如果音乐当前没有在播放，则让音乐进行重新播放
            # 这样如果是在暂停播放时编辑时间可以直接跳到对应时间点播放。如果编辑时间时音乐播放完毕（此时不会跳到下一首）,确认编辑后可以跳到对应时间点播放
            if not mx.music.get_busy():
                self.Music_play(If_Play=True, Replay=True)

            self.PlayList_Box.focus_set()  # 在确认后让焦点回到播放列表上
            self.Playing_TimeST.config(bg='#f0f0f0')  # 将编辑框背景颜色恢复

            Time_Whole = None  # 如果输入时间是符合格式的，则将原封不动放入该变量中
            Time_Second = None  # 如果输入时间是符合格式的，其秒位上的数字会被放入该变量中

            # 判断输入数据是否符合格式
            if re.findall(r"^\d+:\d{1,2}$", self.Music_Time.get()):
                Time_Whole = re.findall(r"^\d+:\d{1,2}$", self.Music_Time.get())[0]  # 保存输入数据
                Time_Second = int(re.findall(r"\d{1,2}$", self.Music_Time.get())[0])  # 保存秒数

            # 如果符合输入格式
            if Time_Whole:

                # 同时输入的秒数必须小于60
                if Time_Second < 60:
                    set_time = int(re.findall(r"^\d{1,2}", self.Music_Time.get())[0]) * 60 + int(
                        re.findall(r"\d{1,2}$", self.Music_Time.get())[0])  # 将输入的时间转化为对应的秒数

                    # 如果音乐播放总时长大于设置的秒数，并且不等于在输入编辑时保存的时间(重要！！！！)，则有效
                    if int(self.Music_Info.info.length) >= set_time and self.Music_Time.get() != self.Previous_Time:
                        mx.music.set_pos(set_time)  # 将时间跳转到设置的时间点
                        # 计算偏移量，实际时间为设置的时间减去pygame已经记录的播放时长,+200是为了弥补误差，单位为毫秒
                        self.Time_Offset = set_time * 1000 - mx.music.get_pos() + 100

            self.IfTime_Counting = True
            myThread(self.Auto_play, 'Second', True).perform()  # 恢复计时线程

    def Auto_play(self):  # 自动播放功能中嵌入计时功能

        # 由于线程不能强制中断，故用self.IfTime_Counting来充当开关
        while self.IfTime_Counting:

            # 每循环一次就让self.Music_Time设置为pygame记录到的播放时间加上偏移值再换算成对应格式

            self.Music_Time.set(
                f"{int((mx.music.get_pos() + self.Time_Offset) / 1000 // 60)}:{int((mx.music.get_pos() + self.Time_Offset) / 1000 % 60):02d}")

            # 每循环一次同时也让进度条位置设置为pygame记录到的播放时间加上偏移值
            self.Schedule_Bar.set(int((mx.music.get_pos() + self.Time_Offset) / 1000))

            time.sleep(0.5)  # 减少循环对性能的损耗，故延迟0.5s

            # 音乐播放完毕后时间会为-1，此时触发切换下一首音乐命令
            if int((mx.music.get_pos() + self.Time_Offset) / 1000) >= int(
                    self.Music_Info.info.length) or mx.music.get_pos() == -1:
                self.Change_Music('Next')

    def Auto_Lyric_Play(self, If_ContinuePlay: bool):  # 歌词轮播功能
        # 清空历史高亮歌词索引
        if If_ContinuePlay:
            self.Previous_lyric_index = np.array([])

        # 如果歌词时间数列中有时间数据
        if np.any(self.Lyric_TimeList):
            self.Lyric_Box.config(state='normal')

            while self.IfLyric_Playing:

                # 寻找数组中与当前播放时间一致的时间的索引，返回值是一个数组
                index = np.where(self.Lyric_TimeList == int((mx.music.get_pos() + self.Time_Offset) / 1000))[0]
                if np.any(index >= 0):

                    # 分歌词为外来歌词还是通过内部爬虫获取的歌词显示，两者处理方式不同
                    if self.Lyric_source == 'I':

                        # 恢复着色
                        if np.size(self.Previous_lyric_index) > 0:
                            if np.size(self.Previous_lyric_index) != np.size(index):
                                for item_1 in self.Previous_lyric_index:
                                    self.Lyric_Box.itemconfig(item_1, fg='black')
                            elif np.all(index != self.Previous_lyric_index):
                                # 由于当index元素个数与后者元素个数不同使用该方法时会发生错误，故有上面if的情况
                                for item_1 in self.Previous_lyric_index:
                                    self.Lyric_Box.itemconfig(item_1, fg='black')

                        # 对应歌词高亮着色
                        for item in index:
                            self.Lyric_Box.itemconfig(item, fg=self.Color_LyricPlaying)

                    elif self.Lyric_source == 'S':

                        if np.size(self.Previous_lyric_index) > 0:
                            if np.size(self.Previous_lyric_index) != np.size(index):
                                for item_1 in self.Previous_lyric_index:
                                    self.Lyric_Box.itemconfig(item_1 + 1, fg='black')
                            elif np.all(index != self.Previous_lyric_index):
                                # 由于当index元素个数与后者元素个数不同使用该方法时会发生错误，故有上面if的情况
                                for item_1 in self.Previous_lyric_index:
                                    self.Lyric_Box.itemconfig(item_1 + 1, fg='black')

                        for item in index:
                            if len(index) == 2:
                                if self.Lyric_TimeList[index[0]] == self.Lyric_TimeList[index[1]]:
                                    self.Lyric_Box.itemconfig(item + 2, fg=self.Color_LyricPlaying)
                                    break
                                else:
                                    self.Lyric_Box.itemconfig(item + 1, fg=self.Color_LyricPlaying)
                            else:
                                self.Lyric_Box.itemconfig(item + 1, fg=self.Color_LyricPlaying)

                    self.Previous_lyric_index = index

                    # 滚动功能
                    data = (np.min(index) - (15 - int(self.Lyric_Box.cget('font')[-2:]))) / len(self.Lyric_data)
                    data = data if data >= 0 else 0
                    self.Lyric_Box.yview_moveto(data)

            # 否则直接停止线程
            else:
                self.IfLyric_Playing = False
            time.sleep(0.5)

    def Lyric_Get_Windows(self):  # 获取歌词窗口进入与预处理
        def Quit():
            self.LyricGetB.config(state='normal')
            self.GetLyric_windows.body.destroy()

        self.LyricGetB.config(state='disabled')
        self.GetLyric_windows = Get_Lyric(self.body)
        if self.Music_Playing[0] != 'direction':
            for key in self.Music_Info.tags.keys():
                if key == 'TIT2':
                    self.GetLyric_windows.Enter_data.set(value=self.Music_Info.tags['TIT2'].text[0])
                    break
                elif key == 'title':
                    self.GetLyric_windows.Enter_data.set(value=self.Music_Info.tags['title'][0])
                    break
        self.GetLyric_windows.body.protocol("WM_DELETE_WINDOW", Quit)
        self.GetLyric_windows.ConfirmB.config(command=self.Lyric_Get)

    def Lyric_Get(self):  # 歌词获取处理
        if self.GetLyric_windows.Search_Lyric and self.Music_Playing[0] != 'direction':

            if not os.path.exists('lyric'):
                os.makedirs('lyric')

            file_name = re.findall(r"^[^.]+", re.findall(r'[^\\/:*?"<>|\r\n]+$', self.Music_Playing[0])[0])[0]
            with open(f'./lyric/{file_name}.dictrc', 'w') as DF:
                json.dump(self.GetLyric_windows.Search_Lyric, DF)
            self.GetLyric_windows.body.destroy()
            self.LyricGetB.config(state='normal')
            self.Lyric_Show()
        elif self.Music_Playing[0] == 'direction':
            tkmb.showerror('错误', '无法获取歌曲名，确认歌词前请确保播放过音乐！')
        elif not self.GetLyric_windows.Search_Lyric:
            tkmb.showerror('错误', '确认前请先预览歌词！')

    def Lyric_Show(self):
        self.Lyric_data = dict()
        file_name = re.findall(r"^[^.]+", re.findall(r'[^\\/:*?"<>|\r\n]+$', self.Music_Playing[0])[0])[0]
        if self.Music_Playing[0] != 'direction' and os.path.exists(f'{self.Music_Playing[0][0:-4]}.lrc'):
            self.Lyric_Path = f'{self.Music_Playing[0][0:-4]}.lrc'
            try:
                with open(f'{self.Music_Playing[0][0:-4]}.lrc', 'r', encoding='utf-8') as IF:
                    for item in IF.readlines():
                        time_1 = re.findall(r'^\[\d+:\d+.\d{2}]', item)
                        time_2 = re.findall(r'^\[\d+:\d+.\d{3}]', item)
                        time_3 = re.findall(r'^\[\d+:\d+]', item)
                        if time_1:
                            while self.Lyric_data.get(time_1[0]):
                                time_1[0] = f'{time_1[0]}P'
                            if item[10:]:
                                self.Lyric_data[time_1[0]] = item[10:]
                        elif time_2:
                            while self.Lyric_data.get(time_2[0]):
                                time_2[0] = f'{time_2[0]}P'
                            if item[11:]:
                                self.Lyric_data[time_2[0]] = item[11:]
                        elif time_3:
                            while self.Lyric_data.get(time_3[0]):
                                time_3[0] = f'{time_3[0]}P'
                            if item[7:]:
                                self.Lyric_data[time_3[0]] = item[7:]
                    self.Lyric_source = 'I'
            except UnicodeDecodeError:
                with open(f'{self.Music_Playing[0][0:-4]}.lrc', 'r') as IF:
                    for item in IF.readlines():
                        time_1 = re.findall(r'^\[\d+:\d+.\d{2}]', item)
                        time_2 = re.findall(r'^\[\d+:\d+.\d{3}]', item)
                        time_3 = re.findall(r'^\[\d+:\d+]', item)
                        if time_1:
                            while self.Lyric_data.get(time_1[0]):
                                time_1[0] = f'{time_1[0]}P'
                            if item[10:]:
                                self.Lyric_data[time_1[0]] = item[10:]
                        elif time_2:
                            while self.Lyric_data.get(time_2[0]):
                                time_2[0] = f'{time_2[0]}P'
                            if item[11:]:
                                self.Lyric_data[time_2[0]] = item[11:]
                        elif time_3:
                            while self.Lyric_data.get(time_3[0]):
                                time_3[0] = f'{time_3[0]}P'
                            if item[7:]:
                                self.Lyric_data[time_3[0]] = item[7:]
                    self.Lyric_source = 'I'
        elif os.path.exists(f'./lyric/{file_name}.dictrc'):
            self.Lyric_Path = os.path.realpath(f'./lyric/{file_name}.dictrc')
            with open(f'./lyric/{file_name}.dictrc', 'r') as DF:
                self.Lyric_data = json.load(DF)
            self.Lyric_source = 'S'

        self.Lyric_TimeList = np.array([])
        for item in self.Lyric_data.keys():
            time_format1 = re.findall(r'^\[\d+:\d+.\d{2}]', item)
            time_format2 = re.findall(r'^\[\d+:\d+.\d{3}]', item)
            time_format3 = re.findall(r'^\[\d+:\d+]', item)
            if time_format1 or time_format2:
                self.Lyric_TimeList = np.append(self.Lyric_TimeList,
                                                (int(re.findall(r'\[\d+:', item)[0][1:-1]) * 6000 + int(
                                                    re.findall(r':\d+.', item)[0][1:-1]) * 100 + int(
                                                    re.findall(r'.\d+]', item)[0][1:-1])) // 100)
            elif time_format3:
                self.Lyric_TimeList = np.append(self.Lyric_TimeList, int(re.findall(r'\[\d+:', item)[0][1:-1]) * 60 +
                                                int(re.findall(r':\d+]', item)[0][1:-1]))

        self.Lyric_Box.delete(0, 'end')
        for item in list(self.Lyric_data.values()):
            self.Lyric_Box.insert(tk.END, item)
        self.Lyric_Box.config(font=('微软雅黑', 11))
        while self.Lyric_Box.xview()[1] != 1.0:
            self.Lyric_Box.config(font=('微软雅黑', int(self.Lyric_Box.cget('font')[-2:]) - 1))
            if int(self.Lyric_Box.cget('font')[-2:]) == 8:
                break
        if mx.music.get_busy() and not self.IfLyric_Playing:
            self.IfLyric_Playing = True
            myThread(self.Auto_Lyric_Play, 'Lyric', True).perform(True)

    def Lyric_FontChange(self, event):
        if self.Lyric_Box.index(tk.END):
            if event.delta > 0 and int(self.Lyric_Box.cget('font')[-2:]) < 20:
                self.Lyric_Box.config(font=('微软雅黑', int(self.Lyric_Box.cget('font')[-2:]) + 1))
            elif event.delta < 0 and 5 < int(self.Lyric_Box.cget('font')[-2:]):
                self.Lyric_Box.config(font=('微软雅黑', int(self.Lyric_Box.cget('font')[-2:]) - 1))

    # def Lyric_Setting(self):
    #     temp_W = tk.Toplevel(self.body)
    #     ww, wh = 600, 400  # 600 400
    #     sw, sh = temp_W.winfo_screenwidth(), temp_W.winfo_screenheight()
    #     temp_W.geometry(f"{ww}x{wh}+{int((sw - ww) / 2)}+{int((sh - wh) / 2)}")
    #     temp_W.resizable(width=False, height=False)
    #     temp_W.transient(self.body)  # 置顶
    #     temp_W.title('歌词设置')

    def Music_Info_Show(self):
        def Quit():
            self.Music_InfoB.config(state='normal')
            self.Music_Info_Windows.body.destroy()

        self.Music_Info_Windows = Music_Info(self.body, self.Music_Playing[0], self.Lyric_Path, self.Lyric_source)
        self.Music_InfoB.config(state='disabled')
        self.Music_Info_Windows.body.protocol("WM_DELETE_WINDOW", Quit)

    def Info_show(self):
        tkmb.showinfo('关于', self.info)

    def Quit(self):
        if tkmb.askquestion("警告", "你确定要退出吗？") == "yes":
            self.body.quit()


if __name__ == "__main__":
    # 主线程T1：界面本体与音乐播放功能
    # 线程T2：计时与音乐播放结束事件处理功能
    # 解决高分辨率显示器高DPI导致TK字体模糊问题
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    SF = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    random.seed(time.time())
    root = tk.Tk()
    mx.init()
    root.tk.call('tk', 'scaling', SF / 75)
    windows1 = MusicPlayer(root)
    T1 = myThread(lambda: windows1, 'Main')
    T1.perform()
    root.mainloop()
