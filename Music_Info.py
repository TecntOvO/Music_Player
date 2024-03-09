import os
import math
import librosa
import mutagen
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Music_Info:
    def __init__(self, body, Music_Path, Lyric_Path, Lyric_Source):
        self.body = tk.Toplevel(body)
        self.ww, self.wh = 600, 800
        self.sw, self.sh = self.body.winfo_screenwidth(), self.body.winfo_screenheight()
        self.body.geometry(f"{self.ww}x{self.wh}+{int((self.sw - self.ww) / 2)}+{int((self.sh - self.wh) / 2)}")
        self.body.resizable(width=False, height=False)
        self.body.transient(body)  # 置顶
        self.body.title('歌曲信息')
        self.BT_font = '微软雅黑'
        self.Music_Path = Music_Path
        self.Lyric_Path = Lyric_Path
        self.Lyric_Source = Lyric_Source
        self.Music_info = mutagen.File(self.Music_Path)
        self.Filename = tk.Variable(value=os.path.basename(self.Music_Path))
        self.Path = tk.Variable(value=os.path.dirname(self.Music_Path))
        self.Path_Ly = tk.Variable()
        self.Music_Type = None
        self.a, self.b = None, None
        self.Bitrate = f'码率/比特率: {self.Music_info.info.bitrate // 1000}kbps' if self.Music_info.info.bitrate > 1000 else f'码率/比特率: {self.Music_info.info.bitrate}bps'
        self.__photo_Open = tk.PhotoImage(file="./image/open.png")

        # 图标替换
        self.__photo_About_icon = tk.PhotoImage(file="./image/about_icon.png")
        self.body.iconphoto(False,self.__photo_About_icon)

        # 提取歌曲信息
        for key in self.Music_info.tags.keys():
            if key == 'TIT2':
                self.Songname = tk.Variable(value=self.Music_info.tags['TIT2'].text[0])
                self.Singername = tk.Variable(value=self.Music_info.tags['TPE1'].text[0])
                self.Albumname = tk.Variable(value=self.Music_info.tags['TALB'].text[0])
                self.Music_Type = 'MP3'
                break
            elif key == 'title':
                self.Songname = tk.Variable(value=self.Music_info.tags['title'][0])
                self.Singername = tk.Variable(value=self.Music_info.tags['artist'][0])
                self.Albumname = tk.Variable(value=self.Music_info.tags['album'][0])
                self.Music_Type = 'OGG'
                break

        # 选项卡
        self.Tab_Main = ttk.Notebook(self.body)
        self.Tab_Main.place(relx=0.02, rely=0.01, relwidth=0.887, relheight=0.876, width=48, height=80)
        self.Info_Tab = tk.Frame(self.Tab_Main, relief='flat')
        self.Wave_Tab = tk.Frame(self.Tab_Main, relief='flat')
        self.Info_Tab.place(x=0, y=30)
        self.Tab_Main.add(self.Info_Tab, text='歌曲信息')
        self.Wave_Tab.place(x=0, y=30, height=500)
        self.Tab_Main.add(self.Wave_Tab, text='歌曲波形')
        self.Tab_Main.bind('<<NotebookTabChanged>>', lambda event: self.Windows_change())

        # 歌曲详情显示头
        title1 = tk.Label(self.Info_Tab, font=('微软雅黑', '10'), text='文件名：', justify='left')
        self.FireName_Show = tk.Entry(self.Info_Tab, font=('微软雅黑', '10'), justify='left',
                                      textvariable=self.Filename, width=40, state='readonly', relief='flat')

        title2 = tk.Label(self.Info_Tab, font=('微软雅黑', '10'), text='歌曲名：', justify='left')
        self.SongName_Show = tk.Entry(self.Info_Tab, font=('微软雅黑', '10'), textvariable=self.Songname,
                                      justify='left', width=35)

        title3 = tk.Label(self.Info_Tab, font=('微软雅黑', '10'), text='歌手：', justify='left')
        self.SingerName_Show = tk.Entry(self.Info_Tab, font=('微软雅黑', '10'), textvariable=self.Singername,
                                        justify='left', width=37)

        title4 = tk.Label(self.Info_Tab, font=('微软雅黑', '10'), text='专辑：', justify='left')
        self.AlbumName_Show = tk.Entry(self.Info_Tab, font=('微软雅黑', '10'), textvariable=self.Albumname,
                                       justify='left', width=37)

        self.Type_Show = tk.Label(self.Info_Tab, font=('微软雅黑', '10'), text=f'类型: {self.Music_Type}文件',
                                  justify='left')
        self.CodeRate_Show = tk.Label(self.Info_Tab, font=('微软雅黑', '10'), text=self.Bitrate, justify='left')
        self.Time_Show = tk.Label(self.Info_Tab, font=('微软雅黑', '10'),
                                  text=f'时长: {int(self.Music_info.info.length // 60)}:{int(self.Music_info.info.length - (self.Music_info.info.length // 60) * 60):02d}',
                                  justify='left')
        self.Frequency_Show = tk.Label(self.Info_Tab, font=('微软雅黑', '10'),
                                       text=f'频率: {self.Music_info.info.sample_rate}Hz', justify='left')
        self.Size_Show = tk.Label(self.Info_Tab, font=('微软雅黑', '10'),
                                  text=f'大小: {os.stat(self.Music_Path).st_size / math.pow(2, 20):0.2f}MB',
                                  justify='left')
        self.LyricSource_Show = tk.Label(self.Info_Tab, font=('微软雅黑', '10'), justify='left')
        title5 = tk.Label(self.Info_Tab, font=('微软雅黑', '10'), text='歌词文件位置: ', justify='left')
        self.LyricPath_Show = tk.Entry(self.Info_Tab, font=('微软雅黑', '10'), justify='left',
                                       textvariable=self.Path_Ly, width=35, state='readonly', relief='flat')
        self.Channels_Show = tk.Label(self.Info_Tab, font=('微软雅黑', '10'),
                                      text=f'声道数: {self.Music_info.info.channels}', justify='left')
        title6 = tk.Label(self.Info_Tab, font=('微软雅黑', '10'), text='音乐文件位置: ', justify='left')
        self.Path_Show = tk.Entry(self.Info_Tab, font=('微软雅黑', '10'), textvariable=self.Path, justify='left',
                                  width=45, state='readonly', relief='flat')
        self.OpenLyricFB = tk.Button(self.Info_Tab, font=(self.BT_font, 10), bg='#FFFFFF', image=self.__photo_Open,
                                     activebackground='#dff5f4', relief='flat', bd=0, highlightcolor='#f0f0f0',
                                     command=lambda: self.Open_File('Lyric'))
        self.OpenMusicFB = tk.Button(self.Info_Tab, font=(self.BT_font, 10), bg='#FFFFFF', image=self.__photo_Open,
                                     activebackground='#dff5f4', relief='flat', bd=0, highlightcolor='#f0f0f0',
                                     command=lambda: self.Open_File('Music'))

        title1.place(x=20, y=20)
        self.FireName_Show.place(x=95, y=22)
        title2.place(x=20, y=100)
        self.SongName_Show.place(x=95, y=102)
        title3.place(x=20, y=160)
        self.SingerName_Show.place(x=75, y=162)
        title4.place(x=20, y=220)
        self.AlbumName_Show.place(x=75, y=222)
        self.Type_Show.place(x=20, y=280)
        self.CodeRate_Show.place(x=320, y=280)
        self.Time_Show.place(x=20, y=340)
        self.Frequency_Show.place(x=320, y=340)
        self.Size_Show.place(x=20, y=400)
        self.Channels_Show.place(x=320, y=400)
        self.LyricSource_Show.place(x=20, y=460)
        title5.place(x=20, y=520)
        self.LyricPath_Show.place(x=155, y=522)
        title6.place(x=20, y=585)
        self.Path_Show.place(x=150, y=587)

        self.OpenLyricFB.place(x=23, y=555)
        self.OpenMusicFB.place(x=23, y=620)

        # 寻找歌词来源
        if self.Lyric_Source == 'I':
            self.LyricSource_Show.config(text='歌词来源: 本地文件')
            self.Path_Ly.set(self.Lyric_Path)
        elif self.Lyric_Source == 'S':
            self.LyricSource_Show.config(text='歌词来源: 歌词获取')
            self.Path_Ly.set(self.Lyric_Path)
        else:
            self.LyricSource_Show.config(text='歌词来源: 无')
            self.Path_Ly.set('无')
            self.OpenLyricFB.config(state='disabled')

        # 歌曲曲线
        self.GenerateB = tk.Button(self.Wave_Tab, text='生成', font=(self.BT_font, 10), bg='#FFFFFF',
                                   activebackground='#dff5f4', width=5, relief='groove',
                                   command=lambda: self.Generate_Wave('View'))
        self.Curve_Frame = tk.LabelFrame(self.Wave_Tab, text='波形图')
        self.ExportB = tk.Button(self.Wave_Tab, text='保存图像', font=(self.BT_font, 10), bg='#FFFFFF',
                                 activebackground='#dff5f4', width=7, relief='groove',
                                 command=lambda: self.Generate_Wave('Export'), state='disabled')

        self.Curve_Frame.place(x=20, y=20, width=800, height=450)
        self.GenerateB.place(x=20, y=500)
        self.ExportB.place(x=720, y=500)

    def Open_File(self, Fire_Type):
        if Fire_Type == "Lyric":
            os.system(f'explorer /select, {os.path.realpath(self.Lyric_Path)}')
        elif Fire_Type == "Music":
            os.system(f'explorer /select, {os.path.realpath(self.Music_Path)}')

    def Windows_change(self):
        self.body.title(f"{self.Tab_Main.tab(self.Tab_Main.select(), 'text')}")
        if self.Tab_Main.index(self.Tab_Main.select()) == 0:
            self.body.geometry('600x800')
        else:
            self.body.geometry('900x600')

    def Generate_Wave(self, function):
        self.GenerateB.config(state='disabled')
        self.a, self.b = librosa.load(self.Music_Path)
        if function == 'View':
            fig = plt.figure(figsize=(10, 5), dpi=51, facecolor='#f0f0f0')
            plt.rcParams['axes.facecolor'] = '#f0f0f0'
            plt.subplots_adjust(left=0.05, right=1, top=0.95, bottom=0.05)
            axes = plt.gca()
            axes.spines['right'].set_color('none')
            axes.spines['top'].set_color('none')
            plt.margins(x=0, y=0)
            librosa.display.waveshow(self.a, sr=self.b, color='green', alpha=0.5)
            canvas = FigureCanvasTkAgg(fig, master=self.Curve_Frame)
            canvas.draw()
            canvas.get_tk_widget().place(x=1, y=1)
            self.GenerateB.config(state='normal')
            self.ExportB.config(state='normal')
        elif function == 'Export':
            path = tkfd.asksaveasfilename(title='图片保存至', defaultextension='.jpg',
                                          filetypes=[('JPG图像文件', '*jpg')])
            if path:
                fig = plt.figure(figsize=(10, 5), dpi=500, facecolor='#ffffff')
                plt.rcParams['axes.facecolor'] = '#ffffff'
                plt.subplots_adjust(left=0.05, right=1, top=0.95, bottom=0.05)
                axes = plt.gca()
                axes.spines['right'].set_color('none')
                axes.spines['top'].set_color('none')
                plt.margins(x=0, y=0)
                librosa.display.waveshow(self.a, sr=self.b, color='green', alpha=0.5)
                canvas = FigureCanvasTkAgg(fig, master=self.Curve_Frame)
                canvas.print_jpg(path)
                tkmb.showinfo('提示', '保存成功！')
                self.ExportB.config(state='normal')
