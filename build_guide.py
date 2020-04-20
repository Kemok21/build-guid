import re, json, os, pickle, webbrowser, threading
import tkinter as tk
import tkinter.filedialog as fd
import requests as rq
from lol_guide import *
from choice_guide import *
from constant import *          #Создание иконки, импортирование объектов изображений и констант

class Kontmenu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent, tearoff=0, takefocus=0)   
        self.parent = parent
        self.add_command(label=LOC['copy'], command=self.copy)
        if isinstance(parent, tk.Entry):
            self.add_command(label=LOC['paste'], command=self.paste)
        self.parent.bind("<Button-3>", self.showMenu)

    def showMenu(self, e):
        self.e = e
        self.tk_popup(e.x_root, e.y_root)
        e.widget.focus()
    def copy(self):
        self.parent.event_generate('<<Copy>>')
    def paste(self):
        self.parent.event_generate('<<Paste>>')

class Listchamp(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.overrideredirect(True)
        self.withdraw()
        self.lis = tk.Listbox(self, selectmode=tk.BROWSE, width=LIS_WIDTH)
        self.lis.pack(fill=tk.BOTH, expand=1)
        ent.bind('<KeyRelease>', self.sch)
        ent.bind('<Down>', self.down)
        ent.bind('<Up>', self.up)
        self.lis.bind('<ButtonRelease-1>', self.choice)
        self.lis.bind('<KeyRelease-Return>', self.choice)
        root.bind('<Configure>', self.move)

    def sch(self, event):
        self.lis.delete(0, tk.END)
        st = ent.get().title()
        ch = lit_dict.get(st)
        if ch:
            self.geometry('+{}+{}'.format(root.winfo_x()+9, root.winfo_y()+78))
            self.lis.config(height=len(ch))
            self.deiconify()
            for n in sorted(ch):
                self.lis.insert(tk.END, n)
        else: self.withdraw()

    def down(self, event):
        self.lis.focus_set()
        self.lis.select_set(0)

    def up(self, event):
        self.lis.focus_set()
        self.lis.activate(tk.END)
        self.lis.select_set(tk.END)

    def choice(self, event):
        index = self.lis.curselection()[0]
        champ = self.lis.get(index)
        ent.delete(0, tk.END)
        ent.insert(0, champ)
        self.withdraw()

    def move(self, event):
        self.geometry('+{}+{}'.format(root.winfo_x()+9, root.winfo_y()+78))

class Bgex:
    def __init__(self):
        if os.path.exists('settings'):
            with open('settings', 'rb') as fset:
                self.sets = pickle.load(fset)
                if self.sets['loc'] == 'en': en_loc(rec=False)
                else: ru_loc(rec=False)
        else:
            en_loc(rec=False)        #заполнение локализации
            self.sets = {'path_dir': './{}/Recommended/',
                         'source': 'mf',
                         'loc': 'en',
                         'var': 'en_US'}
            sendMessage()

        self.dir = self.sets['path_dir']
        self.source = self.sets['source']

    def path(self):
        def ask_path():
            ent.delete(0, tk.END)
            ent.insert(0, fd.askdirectory())
        def save_path():
            if ent.get():
                self.dir = ent.get() + '/Config/Champions/{}/Recommended/'
            else:
                self.dir = './{}/Recommended/'
            self.sets['path_dir'] = self.dir
            top.destroy()
        top = tk.Toplevel(bg='black')
        top.resizable(width=False, height=False)
        top.grab_set()
        top.iconbitmap('image/lol.ico')
        top.title('Path to League of Legends')
        lab = tk.Label(top, bg='black', fg=WGT_FG, text='Example: C:\\Riot Games\\League of Legends')
        ent = tk.Entry(top, width=40)
        if not self.sets['path_dir'][0] == '.':
            ent.insert(0, self.sets['path_dir'][:-33])
        ent.focus_set()
        but1 = tk.Button(top, text='Browse', width=10, bg=WGT_FG, command=ask_path)
        but2 = tk.Button(top, text='Ok', width=10, bg=WGT_FG, command=save_path)
        Kontmenu(ent)
        lab.grid(row=0, columnspan=2)
        ent.grid(row=1, columnspan=2, padx=5)
        but1.grid(row=2, column=0, pady=10)
        but2.grid(row=2, column=1)

    def build(self, e=None):
        self.res = []
        if ent.get() in names:
            self.show_gs(ent.get(), source=self.source)
        else:
            self.show_bd(ent.get())

    def show_bd(self, address, source='mf'):
        tex.config(state=tk.NORMAL)
        tex.delete(1.0, tk.END)
        try:
            self.data = pars_page(address, source)
            self.champion = self.data[0][0]
            
            if imv.get():
                img = Item_image(self.champion, master=tex)
                tex.window_create(tk.END, window=img)
            tex.insert(tk.END, ' {}: {}\n'.format(LOC['name'], self.champion))

            for g in self.data:
                gd = guide(g, tex, LOC)
                self.res.append(gd)
                print_guide(gd, base_items, tex, var.get(), image=imv.get())
            bex.config(state=tk.NORMAL)
            tex.config(state=tk.DISABLED)
        except ZeroDivisionError as ex:
            tex.insert(tk.END, LOC['exp'])
            tex.config(state=tk.DISABLED)
            sendMessage(mes=':1 '+str(ex.__reduce__()))

    def show_gs(self, name, source='mf'):
        def season(text):
            last = text.split()[-1]
            return LOC['up_seson'].format(last)

        def vote(text):
            vt = text.split()
            if vt[0] == 'Votes:':
                return '{} {}'.format('Голосов:', vt[1])
            elif vt[1] == 'Pending':
                return 'Ожидание рейтинга'
            else: return 'Новый'

        tex.config(state=tk.NORMAL)
        tex.delete(1.0, tk.END)
        address = champs_dict[names[name]][self.source]
        guides = champ_gs(address, self.source)
        if imv.get():
            img = Item_image(names[name], master=tex)
            tex.window_create(tk.END, window=img)
        tex.insert(tk.END, ' {}: {}\n'.format(LOC['name'], name))
        for g in guides:
            g['title'] = ''.join([s for s in g['title'] if ord(s) in range(65536)])
            bbs = tk.Button(tex, text=LOC['browse'], bg=BBS_BG, fg=BBS_FG, relief=tk.GROOVE,
                            cursor='hand2', command=lambda x=g['url']: webbrowser.open(x))
            tex.window_create(tk.END, window=bbs)
            tex.insert(tk.END, '\n{}: {}\n'.format(LOC['title'], g['title']))
            tex.insert(tk.END, '{}\n'.format(g['season'] if LOC['loc'] == 'en' else season(g['season'])))
            tex.insert(tk.END, '{}: {}\n'.format(LOC['date'], g['date']))
            burl = tk.Button(tex, image=IMG_BUT['mini'], width=BURL_WIDTH, height=BURL_HEIGHT, bg=BUT_BG,
                            cursor='arrow', command=lambda x=g['url']: self.show_bd(x))
            tex.window_create(tk.END, window=burl)
            tex.insert(tk.END, ' {}\n'.format(g['vote'] if LOC['loc'] == 'en' else vote(g['vote'])))
            tex.insert(tk.END, '\n')
        tex.tag_config('href', foreground=HREF_FG)
        tex.config(state=tk.DISABLED)

    def export(self):
        direct = self.dir.format(self.champion)
        os.makedirs(direct, exist_ok=True)
        for g in self.res:
            with open(direct+g['title']+'.json', 'w') as f:
                json.dump(g, f)
        bex.config(state=tk.DISABLED)

def en_loc(rec=True):
    LOC['loc'] = 'en'
    LOC['copy'] = 'Copy'
    LOC['paste'] = 'Paste'
    LOC['settings'] = 'Settings'
    LOC['lab_text'] = "Enter champion's name:"
    LOC['path'] = 'Path to LoL'
    LOC['update'] = 'Updating data'
    LOC['loading'] = 'Loading.'
    LOC['image'] = 'Image'
    LOC['name'] = "Champion's name"
    LOC['title'] = 'Title'
    LOC['blocks'] = 'Blocks'
    LOC['date'] = 'Date'
    LOC['server'] = 'Server is not available'
    LOC['data'] = 'The data is obsolete!\nUpdate the data and restart the program.'
    LOC['lang'] = 'Language'
    LOC['help'] = 'Help'
    LOC['about'] = 'About the program'
    LOC['browse'] = 'Show guide in browser'
    LOC['exp'] = "Maybe wrong champion's name!"
    LOC['doc'] = ' Build guide LoL help:\n\n'\
                 ' ► The program is designed to create files-guides for League of Legends.\n\n'\
                 ' ► The program receives a list of guides from the site http://www.mobafire.com.\n\n'\
                 ' ► To view the list of guides, enter name of the champion in text field,\n'\
                 '   then press enter or "Show guides" button.\n'\
                 '   A list of guides for the given champion will appear in field below.\n\n'\
                 ' ► To view the guide, You need to click on the "show guide" button.\n'\
                 '   A list of items included in this guide appears in the field.\n\n'\
                 ' ► To export the selected guide to a file, click the "Export to file" button.\n\n'\
                 ' ► To get the file-guide in the required directory\n'\
                 '   (...\League of Legends\Config\Champions\{champion}\Recommended\),\n'\
                 '   You need to specify the path to the League of Legends in [settings->path].\n'\
                 '   By default, the file-guide is saved in the program directory.\n\n'\
                 ' ► To update data on subjects and champions, you need to use the option\n'\
                 '   [Settings-> Update Data].\n\n'\
                 ' ► The buttons "ru_RU" and "en_US" mean the localization of queries\n'\
                 '   for object names, Russian and English respectively.\n\n'\
                 ' ► After the first start, the program creates a setting file.\n\n E-mail: kilankemok@gmail.com'
    IMG_BUT['ex'] = en_ex
    IMG_BUT['mini'] = en_mini
    IMG_BUT['sg'] = en_sg
    if rec: re_config()
def ru_loc(rec=True):
    LOC['loc'] = 'ru'
    LOC['copy'] = 'Копировать'
    LOC['paste'] = 'Вставить'
    LOC['settings'] = 'Настройки'
    LOC['lab_text'] = 'Введите имя чемпиона:'
    LOC['path'] = 'Путь к LoL'
    LOC['update'] = 'Обновление данных'
    LOC['loading'] = 'Загрузка.'
    LOC['image'] = 'Изображение'
    LOC['name'] = 'Имя чемпиона'
    LOC['title'] = 'Название'
    LOC['blocks'] = 'Блоков'
    LOC['date'] = 'Дата'
    LOC['server'] = 'Сервер не доступен'
    LOC['data'] = 'Данные устарели!\nОбновите данные и перезапустите программу.'
    LOC['help'] = 'Справка'
    LOC['about'] = 'О программе'
    LOC['lang'] = 'Язык'
    LOC['browse'] = 'Показать гайд в браузере'
    LOC['exp'] = 'Возможно ошибочное имя чемпиона!'
    LOC['doc'] =  ' Справка Build guide LoL:\n\n'\
                 ' ► Программа предназначена для создания файлов-гайдов для League of Legends.\n\n'\
                 ' ► Программа получает список гайдов с сайта http://www.mobafire.com.\n\n'\
                 ' ► Чтобы посмотреть список гайдов, в текстовом поле нужно ввести имя чемпиона,\n'\
                 '   затем нажать ввод или кнопку "Показать гайды".\n'\
                 '   В поле ниже появится список гайдов на заданного чемпиона.\n\n'\
                 ' ► Чтобы посмотреть гайд, нужно нажать на кнопку "Показать гайд".\n'\
                 '   В поле появится список предметов входящие в этот гайд.\n\n'\
                 ' ► Чтобы экспортировать выбранный гайд в файл, нужно нажать кнопку\n'\
                 '   "Экспорт в файл".\n\n'\
                 ' ► Для того чтобы файл-гайд оказался в нужной директории\n'\
                 '   (...\League of Legends\Config\Champions\{champion}\Recommended\),\n'\
                 '   нужно в [Настройки->Путь к LoL] указать путь к League of Legends.\n'\
                 '   По умолчанию файл-гайд сохраняется в директорию программы.\n\n'\
                 ' ► Для обновления данных по предметам и чемпионам нужно использовать опцию\n'\
                 '   [Настройки->Обновление данных].\n\n'\
                 ' ► Кнопки "ru_RU" и "en_US", означают локализацию запросов на имена предметов,\n'\
                 '   Русская и Английская соответственно.\n\n'\
                 ' ► После первого запуска, программа создает файл настроек.\n\n E-mail: kilankemok@gmail.com'
    IMG_BUT['ex'] = ru_ex
    IMG_BUT['mini'] = ru_mini
    IMG_BUT['sg'] = ru_sg
    if rec: re_config()
def re_config():
    sm.entryconfigure(0, label=LOC['path'])
    sm.entryconfigure(1, label=LOC['update'])
    sm.entryconfigure(2, label=LOC['lang'])
    hm.entryconfigure(0, label=LOC['help'])
    hm.entryconfigure(1, label=LOC['about'])
    lab.configure(text=LOC['lab_text'])
    che.configure(text=LOC['image'])
    but.configure(image=IMG_BUT['sg'])
    bex.configure(image=IMG_BUT['ex'])
    bge.sets['loc'] = LOC['loc']
    Kontmenu(ent)
    Kontmenu(tex)
    
def hlp():
    top = tk.Toplevel()
    top.resizable(width=False, height=False)
    top.focus_set()
    top.grab_set()
    top.iconbitmap('image/lol.ico')
    top.title(LOC['help'])
    tex = tk.Text(top, width=80, height=29, wrap=tk.WORD)
    tex.insert(tk.END, LOC['doc'])
    tex.config(state=tk.DISABLED)
    Kontmenu(tex)
    tex.pack()

def about():
    top = tk.Toplevel(bg=WGT_FG)
    top.resizable(width=False, height=False)
    top.focus_set()
    top.grab_set()
    top.iconbitmap('image/lol.ico')
    top.title(LOC['about'])
    top.geometry('185x60')
    lab = tk.Label(top, text='Build guide LoL\nVersion 1.1\nKilankemok\n© 2017', bg=WGT_FG)
    lab.pack()

def load_update(widget):
    widget.config(state=tk.NORMAL)
    widget.delete(1.0, tk.END)
    widget.insert(tk.END, LOC['loading'])
    t = threading.Thread(target=update, args=(widget,))
    t.daemon = True
    t.start()

base_items = {}

root = tk.Tk()
root.config()
root.iconbitmap('image/lol.ico')
root.title('Build guide for League of Legends (Beta)')
root.geometry(ROOT_SIZE)
root.minsize(width=WIDTH_RG[0], height=HEIGHT_RG[0])
root.maxsize(width=WIDTH_RG[1], height=HEIGHT_RG[1])  

bg = tk.PhotoImage(file='image/background.png')
en_ex = tk.PhotoImage(file='image/en_ex.png')
en_mini = tk.PhotoImage(file='image/en_mini.png')
en_sg = tk.PhotoImage(file='image/en_sg.png')
ru_ex = tk.PhotoImage(file='image/ru_ex.png')
ru_mini = tk.PhotoImage(file='image/ru_mini.png')
ru_sg = tk.PhotoImage(file='image/ru_sg.png')

IMG_BUT = {'ex': en_ex, 'mini': en_mini, 'sg': en_sg}

LOC = {'up_rec': 'Свежий гайд, обновлен недавно.',
        'up_seson': 'Гайд обновлен для версии {}'}
        
fon = tk.Label(image=bg)
bge = Bgex()

var = tk.StringVar()
rad1 = tk.Radiobutton(root, text=RU, bg=WGT_BG, fg=WGT_FG, selectcolor=COLOR_FLAG, variable=var, value=RU)
rad2 = tk.Radiobutton(root, text=US, bg=WGT_BG, fg=WGT_FG, selectcolor=COLOR_FLAG, variable=var, value=US)
var.set(bge.sets['var'])

gm = tk.Menu(root)
root.config(menu=gm)
sm = tk.Menu(gm, tearoff=0, postcommand=re_config)
gm.add_cascade(label=LOC['settings'], menu=sm)
sm.add_command(label=LOC['path'], command=bge.path)
tex = tk.Text(root, bg=TEX_BG, wrap=tk.WORD, state=tk.DISABLED)
sm.add_command(label=LOC['update'], command=lambda x=tex: load_update(x))
lm = tk.Menu(sm, tearoff=0)
sm.add_cascade(label=LOC['lang'], menu=lm)
lm.add_command(label='English', command=en_loc)
lm.add_command(label='Русский', command=ru_loc)
hm = tk.Menu(gm, tearoff=0, postcommand=re_config)
gm.add_cascade(label=LOC['help'], menu=hm)
hm.add_command(label=LOC['help'], command=hlp)
hm.add_command(label=LOC['about'], command=about)

lab = tk.Label(root, text=LOC['lab_text'], bg=WGT_BG, fg=WGT_FG)
ent = tk.Entry(root, width=ENT_WIDTH, bg=WGT_FG)
ent.bind('<Return>', bge.build)
ent.focus_set()

imv = tk.BooleanVar()
che = tk.Checkbutton(root, text=LOC['image'], bg=WGT_BG, fg=WGT_FG, selectcolor=COLOR_FLAG, variable=imv, onvalue=True, offvalue=False)
imv.set(True)

but = tk.Button(root, image=IMG_BUT['sg'], width=BUT_WIDTH, height=BUT_HEIGHT, bg=BUT_BG, command=bge.build)
scr = tk.Scrollbar(root, command=tex.yview)
tex.configure(yscrollcommand=scr.set)

bex = tk.Button(root, image=IMG_BUT['ex'], width=BEX_WIDTH, height=BEX_HEIGHT, bg=BUT_BG, state=tk.DISABLED, command=bge.export)

fon.grid(row=0, column=0, rowspan=5, columnspan=8)
lab.grid(row=0, column=0, columnspan=8)
ent.grid(row=1, column=0, columnspan=8, padx=5, sticky=tk.EW)
che.grid(row=2, column=0, sticky=tk.W)
rad1.grid(row=2, column=1)
rad2.grid(row=2, column=2)
but.grid(row=2, column=5, columnspan=2, pady=5)
tex.grid(row=3, column=0, columnspan=8, padx=47, sticky=tk.NSEW)
scr.grid(row=3, column=7, sticky=tk.NS)
bex.grid(row=4, column=6, columnspan=2, padx=35)
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(3, weight=1)

Kontmenu(ent)
Kontmenu(tex)
Listchamp()

try:
    import id_base                       #Создает файл db_items.json
    champs_dict = ch_info(tex, LOC['data'])              #Заполняет names и lit_dict, создает словарь с ключами-именами Лиги
except(rq.RequestException) as ex:
    tex.config(state=tk.NORMAL)
    tex.insert(tk.END, LOC['server'])
    tex.config(state=tk.DISABLED)
    sendMessage(mes=':2 '+str(ex))
except(KeyError) as ex:
    tex.config(state=tk.NORMAL)
    tex.insert(tk.END, LOC['data'])
    tex.config(state=tk.DISABLED)
    sendMessage(mes=':3 '+str(ex))
except Exception as ex:
    tex.config(state=tk.NORMAL)
    tex.insert(tk.END, ex)
    tex.config(state=tk.DISABLED)
    sendMessage(mes=':4 '+str(ex.__reduce__()))

root.mainloop()

with open('settings', 'wb') as fset:
    bge.sets['var'] = var.get()
    pickle.dump(bge.sets, fset)