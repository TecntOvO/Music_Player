import re
import time
import requests
import tkinter as tk
from tkinter import ttk
from bs4 import BeautifulSoup
from Mythreading import myThread


class Get_Lyric:
    def __init__(self, body):
        """
        简介：本爬虫是对网站https://www.musicenc.com进行歌词爬取,主要是通过歌名得到搜索目录以及对应项的token后，根据token进入对应歌词网站
        爬取歌词数据。

        警告：最后得到的歌词数据是以字典的形式保存在self.Search_Lyric中，key为时间value为歌词，但是由于网站特殊性，key并非要跳转到对应后面
        跟着的value的歌词时间而是下一句歌词的时间，加上存在中英同时存在会比较混乱的情况，故需要进行进一步处理，本人已在main.py的Auto_Lyric_
        Play方法中，在判断条件elif self.Lyric_source == 'S'后撰写了针对本播放器歌词显示特点的处理方法，仅供参考。

        作者：许栋凯
        时间: 2023年6月22号
        """
        self.body = tk.Toplevel(body)
        self.ww, self.wh = 800, 600  # 600 400
        self.sw, self.sh = self.body.winfo_screenwidth(), self.body.winfo_screenheight()
        self.body.geometry(f"{self.ww}x{self.wh}+{int((self.sw - self.ww) / 2)}+{int((self.sh - self.wh) / 2)}")
        self.body.resizable(width=False, height=False)
        self.body.transient(body)  # 置顶
        self.body.title('获取歌词')
        self.Bt_font = '微软雅黑'
        self.State_SV = tk.StringVar()  # 用于存放显示在界面左下角的状态信息
        self.Enter_data = tk.Variable()  # 存放搜索框输入歌名数据
        self.Enter_Singer_data = tk.Variable()  # 存放搜索框输入的歌手数据
        self.Search_time_count = 10  # 单位秒，规定搜索中断倒计时
        self.Generate_time_count = 15  # 单位秒，规定提取歌词中断倒计时
        self.time_count_leave = None
        self.links = None
        self.TokenBackup = None  # Token留底
        self.Enter_dataBackup = None  # 数据留底
        self.search_list = None  # 为元组，元组内每一个元素为一条搜索结果，搜索结果包含歌名，歌手以及token
        self.search_error = False  # 记录是否搜索失败
        self.Search_lyric_data = None  # 当前搜索获取歌词数据
        self.Search_Lyric = dict()  # 存放获取到的歌词
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43',
        }  # 主机信息

        # 图标替换
        self.__photo_icon = tk.PhotoImage(file="./image/search_icon.png")
        self.body.iconphoto(False, self.__photo_icon)

        # 框架组件
        self.F = tk.Frame(self.body, bd=1, bg='#ffffff', relief='groove')
        self.F_1 = tk.Frame(self.body, bd=1, bg='#ebf7ff', relief='groove')
        self.F_2 = tk.LabelFrame(self.body, bd=1, bg='#ffffff', relief='groove', text='歌词预览', padx=16, pady=20)
        self.F.grid(column=1, row=1, ipadx=160, sticky='w')
        self.F_1.grid(column=1, row=2, sticky='WN')
        self.F_2.grid(column=1, row=2, sticky='WN', padx=475)

        # 文本信息组件
        self.label1 = tk.Label(self.F, text='歌曲：', bg='#ffffff')
        self.label2 = tk.Label(self.F, text='歌手：', bg='#ffffff')
        self.label3 = tk.Label(self.body, textvariable=self.State_SV)
        self.label1.grid(column=1, row=1, padx=10, pady=15)
        self.label2.grid(column=3, row=1, padx=10)
        self.label3.grid(column=1, row=2, sticky='NW', pady=510)

        # 歌词预览相关组件
        Sl2 = tk.Scrollbar(self.F_2, orient='horizontal', width=20)
        self.Preview_Lyric = tk.Listbox(self.F_2, width=32, bg='#ffffff', selectbackground='#cffa8e',
                                        selectforeground='#000000',
                                        activestyle='dotbox', cursor='hand2', relief='flat', height=25,
                                        font=('宋体', 8), justify='center')
        self.Preview_Lyric.config(xscrollcommand=Sl2.set)
        Sl2.config(command=self.Preview_Lyric.xview)
        Sl2.pack(side='bottom', padx=10, expand=True, fill='x')
        self.Preview_Lyric.pack(fill='both', padx=10)

        # 按钮组件
        self.SearchB = tk.Button(self.F, text='搜索', font=(self.Bt_font, 10), bg='#FFFFFF', activebackground='#dff5f4',
                                 width=4, relief='groove', command=self.get_token_threading)
        self.PreviewB = tk.Button(self.F, text='预览', font=(self.Bt_font, 10), bg='#FFFFFF',
                                  activebackground='#dff5f4',
                                  width=4, relief='groove', command=self.Preview_threading)
        self.ConfirmB = tk.Button(self.F, text='确认', font=(self.Bt_font, 10), bg='#FFFFFF',
                                  activebackground='#dff5f4',
                                  width=4, relief='groove')
        self.SearchB.grid(column=5, row=1, padx=10, sticky='W')
        # self.ImportB.grid(column=6, row=1, padx=10, sticky='W')
        self.PreviewB.grid(column=6, row=1, padx=10, sticky='W')
        self.ConfirmB.grid(column=7, row=1, padx=10, sticky='W')

        # 搜索输入框组件
        self.name_Enter = tk.Entry(self.F, bg='#ffffff', textvariable=self.Enter_data, width=15)
        self.singer_Enter = tk.Entry(self.F, bg='#ffffff', textvariable=self.Enter_Singer_data, width=10)
        self.name_Enter.grid(column=2, row=1, padx=5, pady=10)
        self.singer_Enter.grid(column=4, row=1, padx=5, pady=10)

        # 搜索结果列表组件
        Sl1 = tk.Scrollbar(self.F_1, width=20)
        self.tree = ttk.Treeview(self.F_1, columns=('1', '2', '3', '4'), selectmode='browse', show='headings',
                                 height=24)
        self.tree.column('1', minwidth=50, width=70, anchor='center')
        self.tree.column('2', minwidth=80, width=270)
        self.tree.column('3', minwidth=60, width=110)
        self.tree.column('4', minwidth=0, width=0)
        self.tree.heading('1', text='序号')
        self.tree.heading('2', text='歌曲名称')
        self.tree.heading('3', text='歌手')
        Sl1.config(command=self.tree.yview)
        self.tree.config(yscrollcommand=Sl1.set)
        Sl1.grid(column=2, row=1, sticky='ns')
        self.tree.grid(column=1, row=1, sticky='WN')

    def Button_state(self, Preview, Confirm, Search):  # 统一管理按钮开关方法
        self.PreviewB.config(state='normal') if Preview else self.PreviewB.config(state='disabled')
        self.ConfirmB.config(state='normal') if Confirm else self.ConfirmB.config(state='disabled')
        self.SearchB.config(state='normal') if Search else self.SearchB.config(state='disabled')

    # 原本的获取歌词处理方法，已经移植到main.py中处理
    # def Import_Lyric_(self):
    #     self.Button_state(0, 0, 0, 0)
    #     self.Import_Lyric = dict()
    #     Import_File = tkfd.askopenfilename(filetypes=[('Lrc歌词文件', '*.lrc')])
    #     if Import_File:
    #         try:
    #             with open(Import_File, 'r', encoding='utf-8') as IF:
    #                 for item in IF.readlines():
    #                     time_1 = re.findall(r'^\[\d+:\d+.\d{2}]', item)
    #                     time_2 = re.findall(r'^\[\d+:\d+.\d{3}]', item)
    #                     time_3 = re.findall(r'^\[\d+:\d+]', item)
    #                     if time_1:
    #                         while self.Import_Lyric.get(time_1[0]):
    #                             time_1[0] = f'{time_1[0]}P'
    #                         if item[10:]:
    #                             self.Import_Lyric[time_1[0]] = item[10:]
    #                     elif time_2:
    #                         while self.Import_Lyric.get(time_2[0]):
    #                             time_2[0] = f'{time_2[0]}P'
    #                         if item[11:]:
    #                             self.Import_Lyric[time_2[0]] = item[11:]
    #                     elif time_3:
    #                         while self.Import_Lyric.get(time_3[0]):
    #                             time_3[0] = f'{time_3[0]}P'
    #                         if item[7:]:
    #                             self.Import_Lyric[time_3[0]] = item[7:]
    #         except UnicodeDecodeError:
    #             with open(Import_File, 'r') as IF:
    #                 for item in IF.readlines():
    #                     time_1 = re.findall(r'^\[\d+:\d+.\d{2}]', item)
    #                     time_2 = re.findall(r'^\[\d+:\d+.\d{3}]', item)
    #                     time_3 = re.findall(r'^\[\d+:\d+]', item)
    #                     if time_1:
    #                         while self.Import_Lyric.get(time_1[0]):
    #                             time_1[0] = f'{time_1[0]}P'
    #                         if item[10:]:
    #                             self.Import_Lyric[time_1[0]] = item[10:]
    #                     elif time_2:
    #                         while self.Import_Lyric.get(time_2[0]):
    #                             time_2[0] = f'{time_2[0]}P'
    #                         if item[11:]:
    #                             self.Import_Lyric[time_2[0]] = item[11:]
    #                     elif time_3:
    #                         while self.Import_Lyric.get(time_3[0]):
    #                             time_3[0] = f'{time_3[0]}P'
    #                         if item[7:]:
    #                             self.Import_Lyric[time_3[0]] = item[7:]
    #         self.Preview_Lyric.delete(0, 'end')
    #         for item in self.Import_Lyric.values():
    #             self.Preview_Lyric.insert(tk.END, item)
    #     self.Button_state(1, 1, 1, 1)

    def get_token_threading(self):  # 获取歌曲token线程方法
        if self.Enter_data.get():
            myThread(self.get_token, 'get_token').perform()
            myThread(self.Prevent_Overtime, 'prevent-overtime').perform()

    def Preview_threading(self):  # 预览歌词线程方法
        if self.tree.selection():
            self.Search_Lyric = dict()
            myThread(self.get_lyric, 'get_lyric', True).perform(list(self.tree.item(self.tree.focus()).values())[2][3])
            myThread(self.Generate_info, 'Generate_info', True).perform()
            myThread(self.Preview_lyric, 'Preview_lyric', True).perform()

    def get_token(self):  # 获取token方法
        if self.Enter_data.get() != self.Enter_dataBackup or self.search_error:
            #  如果搜索歌名于前一次相同，直接使用本地缓存
            self.links = None
            self.search_error = False
            self.Enter_dataBackup = self.Enter_data.get()  # 本地缓存

            try:
                # 爬取html文件
                response = requests.get(f'https://www.musicenc.com/?search={self.Enter_data.get()}',
                                        headers=self.header, timeout=self.Search_time_count)
                soup = BeautifulSoup(response.text, 'lxml')
                self.links = soup.find('div', class_="list")

                names = list()
                singers = list()
                tokens = list()

                # 找到返回的搜索目录表格并写入，目录得到的歌名放入names列表，歌手放入singers列表，每一条结果的token放入tokens列表
                if self.links.find_all('li'):
                    for link in self.links.find_all('li'):
                        try:
                            # 有时候空格在json中会以\xa0显示，故需要替换
                            names.append(link.a.string.replace('\xa0', ' '))
                        except:
                            names.append(link.a.string)
                        try:
                            # 有时候空格在json中会以\xa0显示，故需要替换
                            singers.append(link.span.string.replace('\xa0', ' ')[1:-1])
                        except:
                            singers.append(link.span.string[1:-1])
                        tokens.append(link.a.attrs['dates'])

                    # 执行完后打包成元组，元组每一项即为一条搜索结果所包含的信息
                    self.search_list = tuple(zip(names, singers, tokens))

                else:
                    self.time_count_leave = 0
                    self.State_SV.set('未找到任何结果')
                    return None

            except:
                self.search_error = True  # 若搜索失败或者超时则返回error，并return中止
                return None

        # 清空列表树
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 结果写入列表树
        order = 1
        for result in self.search_list:
            if result[1].count(self.Enter_Singer_data.get()) or not self.Enter_Singer_data.get():
                # 树中隐藏了最后一列token，之所以这样存放是为了到时候好从表中找到选择项额token
                self.tree.insert('', tk.END, values=(order, result[0], result[1], result[2]))
                order += 1

    def get_lyric(self, token: str):  # 获取歌词方法
        if not self.TokenBackup == token or self.search_error:
            self.search_error = False
            self.TokenBackup = token

            # 此处非常重要，观察发现如果token结尾出现等号必须将其全部转化为%3D才可继续爬取
            if re.findall(r'=+$', token):
                count = len(re.findall(r'=+$', token)[0])
            else:
                count = 0
            for i in range(count):
                token = f"{token.strip('=')}" + "%3D"

            url = f'https://www.musicenc.com/searchr/?token={token}'
            try:
                html = requests.get(url, headers=self.header, timeout=self.Search_time_count)
                soup = BeautifulSoup(html.text, 'lxml')
                self.Search_lyric_data = soup.find('div', class_="content")
            except:
                self.search_error = True
                return None

        # print(self.Search_Lyric_data.contents)
        # print('***********************************')

        # 爬取歌词结果写入
        index = 2
        while index <= len(self.Search_lyric_data.contents):
            if index < len(self.Search_lyric_data.contents) - 1:
                Play_time = self.Search_lyric_data.contents[index][-7:]
                while self.Search_Lyric.get(Play_time):
                    Play_time = f'{Play_time}P'
                self.Search_Lyric[Play_time] = self.Search_lyric_data.contents[index][0:-7]
            else:
                # 最后结尾歌词是没有时间的，故用END作为key
                self.Search_Lyric['END'] = self.Search_lyric_data.contents[index]
                break
            index += 2

    def Preview_lyric(self):  # 预览歌词方法
        self.Preview_Lyric.delete(0, 'end')
        while not self.Search_Lyric:
            time.sleep(1)  # 等待歌词数据
        for item in self.Search_Lyric.values():
            self.Preview_Lyric.insert(tk.END, item)

    def Prevent_Overtime(self):  # 搜索超时中断方法
        self.time_count_leave = self.Search_time_count
        self.Button_state(0, 0, 0)
        while True:
            if self.links:
                if self.links.find_all('li'):
                    self.State_SV.set('')
                    self.Button_state(1, 1, 1)
                    break
            elif self.time_count_leave == 0 or self.search_error:
                self.State_SV.set('错误')
                self.Button_state(1, 1, 1)
                break
            else:
                self.State_SV.set(f'搜索中......(强制中断倒计时{int(self.time_count_leave)}秒)')
                time.sleep(1)
                self.time_count_leave -= 1

    def Generate_info(self):  # 类似与上面的中断方法，只不过是用于爬取歌词时用
        self.time_count_leave = self.Generate_time_count
        self.Button_state(0, 0, 0)
        while True:
            if self.Search_Lyric:
                self.State_SV.set('')
                self.Button_state(1, 1, 1)
                break
            elif self.time_count_leave == 0 or self.search_error:
                self.State_SV.set('错误')
                self.Button_state(1, 1, 1)
                break
            else:
                self.State_SV.set(f'提取歌词中......请稍后(强制中断倒计时{self.time_count_leave}秒)')
                time.sleep(1)
                self.time_count_leave -= 1
