import pickle
from tkinter import messagebox
import os
import db
import calendar
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk


datetime = calendar.datetime.datetime
timedelta = calendar.datetime.timedelta
class Calendar:

    def __init__(s, point=None, position=None):
        # point    提供一个基点，来确定窗口位置
        # position 窗口在点的位置 'ur'-右上, 'ul'-左上, 'll'-左下, 'lr'-右下
        # s.master = tk.Tk()
        s.master = tk.Toplevel()
        s.master.withdraw()
        fwday = calendar.SUNDAY

        year = datetime.now().year
        month = datetime.now().month
        locale = None
        sel_bg = '#ecffc4'
        sel_fg = '#05640e'

        s._date = datetime(year, month, 1)
        s._selection = None  # 设置为未选中日期

        s.G_Frame = ttk.Frame(s.master)

        s._cal = s.__get_calendar(locale, fwday)

        s.__setup_styles()  # 创建自定义样式
        s.__place_widgets()  # pack/grid 小部件
        s.__config_calendar()  # 调整日历列和安装标记
        # 配置画布和正确的绑定，以选择日期。
        s.__setup_selection(sel_bg, sel_fg)

        # 存储项ID，用于稍后插入。
        s._items = [s._calendar.insert('', 'end', values='') for _ in range(6)]

        # 在当前空日历中插入日期
        s._update()

        s.G_Frame.pack(expand=1, fill='both')
        s.master.overrideredirect(1)
        s.master.update_idletasks()
        width, height = s.master.winfo_reqwidth(), s.master.winfo_reqheight()
        if point and position:
            if position == 'ur':
                x, y = point[0], point[1] - height
            elif position == 'lr':
                x, y = point[0], point[1]
            elif position == 'ul':
                x, y = point[0] - width, point[1] - height
            elif position == 'll':
                x, y = point[0] - width, point[1]
        else:
            x, y = (s.master.winfo_screenwidth() - width) / 2, (s.master.winfo_screenheight() - height) / 2
        s.master.geometry('%dx%d+%d+%d' % (width, height, x, y))  # 窗口位置居中
        s.master.after(300, s._main_judge)
        s.master.deiconify()
        s.master.focus_set()
        s.master.wait_window()  # 这里应该使用wait_window挂起窗口，如果使用mainloop,可能会导致主程序很多错误

    def __get_calendar(s, locale, fwday):
        # 实例化适当的日历类
        if locale is None:
            return calendar.TextCalendar(fwday)
        else:
            return calendar.LocaleTextCalendar(fwday, locale)

    def __setitem__(s, item, value):
        if item in ('year', 'month'):
            raise AttributeError("attribute '%s' is not writeable" % item)
        elif item == 'selectbackground':
            s._canvas['background'] = value
        elif item == 'selectforeground':
            s._canvas.itemconfigure(s._canvas.text, item=value)
        else:
            s.G_Frame.__setitem__(s, item, value)

    def __getitem__(s, item):
        if item in ('year', 'month'):
            return getattr(s._date, item)
        elif item == 'selectbackground':
            return s._canvas['background']
        elif item == 'selectforeground':
            return s._canvas.itemcget(s._canvas.text, 'fill')
        else:
            r = ttk.tclobjs_to_py({item: ttk.Frame.__getitem__(s, item)})
            return r[item]

    def __setup_styles(s):
        # 自定义TTK风格
        style = ttk.Style(s.master)
        arrow_layout = lambda dir: (
            [('Button.focus', {'children': [('Button.%sarrow' % dir, None)]})]
        )
        style.layout('L.TButton', arrow_layout('left'))
        style.layout('R.TButton', arrow_layout('right'))

    def __place_widgets(s):
        # 标头框架及其小部件
        Input_judgment_num = s.master.register(s.Input_judgment)  # 需要将函数包装一下，必要的
        hframe = ttk.Frame(s.G_Frame)
        gframe = ttk.Frame(s.G_Frame)
        bframe = ttk.Frame(s.G_Frame)
        hframe.pack(in_=s.G_Frame, side='top', pady=5, anchor='center')
        gframe.pack(in_=s.G_Frame, fill=tk.X, pady=5)
        bframe.pack(in_=s.G_Frame, side='bottom', pady=5)

        lbtn = ttk.Button(hframe, style='L.TButton', command=s._prev_month)
        lbtn.grid(in_=hframe, column=0, row=0, padx=12)
        rbtn = ttk.Button(hframe, style='R.TButton', command=s._next_month)
        rbtn.grid(in_=hframe, column=5, row=0, padx=12)

        s.CB_year = ttk.Combobox(hframe, width=5, values=[str(year) for year in
                                                          range(datetime.now().year, datetime.now().year - 11, -1)],
                                 validate='key', validatecommand=(Input_judgment_num, '%P'))
        s.CB_year.current(0)
        s.CB_year.grid(in_=hframe, column=1, row=0)
        s.CB_year.bind('<KeyPress>', lambda event: s._update(event, True))
        s.CB_year.bind("<<ComboboxSelected>>", s._update)
        tk.Label(hframe, text='年', justify='left').grid(in_=hframe, column=2, row=0, padx=(0, 5))

        s.CB_month = ttk.Combobox(hframe, width=3, values=['%02d' % month for month in range(1, 13)], state='readonly')
        s.CB_month.current(datetime.now().month - 1)
        s.CB_month.grid(in_=hframe, column=3, row=0)
        s.CB_month.bind("<<ComboboxSelected>>", s._update)
        tk.Label(hframe, text='月', justify='left').grid(in_=hframe, column=4, row=0)

        # 日历部件
        s._calendar = ttk.Treeview(gframe, show='', selectmode='none', height=7)
        s._calendar.pack(expand=1, fill='both', side='bottom', padx=5)

        ttk.Button(bframe, text="确 定", width=6, command=lambda: s._exit(True)).grid(row=0, column=0, sticky='ns',
                                                                                    padx=20)
        ttk.Button(bframe, text="取 消", width=6, command=s._exit).grid(row=0, column=1, sticky='ne', padx=20)

        tk.Frame(s.G_Frame, bg='#565656').place(x=0, y=0, relx=0, rely=0, relwidth=1, relheigh=2 / 200)
        tk.Frame(s.G_Frame, bg='#565656').place(x=0, y=0, relx=0, rely=198 / 200, relwidth=1, relheigh=2 / 200)
        tk.Frame(s.G_Frame, bg='#565656').place(x=0, y=0, relx=0, rely=0, relwidth=2 / 200, relheigh=1)
        tk.Frame(s.G_Frame, bg='#565656').place(x=0, y=0, relx=198 / 200, rely=0, relwidth=2 / 200, relheigh=1)

    def __config_calendar(s):
        # cols = s._cal.formatweekheader(3).split()
        cols = ['日', '一', '二', '三', '四', '五', '六']
        s._calendar['columns'] = cols
        s._calendar.tag_configure('header', background='grey90')
        s._calendar.insert('', 'end', values=cols, tag='header')
        # 调整其列宽
        font = tkFont.Font()
        maxwidth = max(font.measure(col) for col in cols)
        for col in cols:
            s._calendar.column(col, width=maxwidth, minwidth=maxwidth,
                               anchor='center')

    def __setup_selection(s, sel_bg, sel_fg):
        def __canvas_forget(evt):
            canvas.place_forget()
            s._selection = None

        s._font = tkFont.Font()
        s._canvas = canvas = tk.Canvas(s._calendar, background=sel_bg, borderwidth=0, highlightthickness=0)
        canvas.text = canvas.create_text(0, 0, fill=sel_fg, anchor='w')

        canvas.bind('<Button-1>', __canvas_forget)
        s._calendar.bind('<Configure>', __canvas_forget)
        s._calendar.bind('<Button-1>', s._pressed)

    def _build_calendar(s):
        year, month = s._date.year, s._date.month

        # update header text (Month, YEAR)
        header = s._cal.formatmonthname(year, month, 0)

        # 更新日历显示的日期
        cal = s._cal.monthdayscalendar(year, month)
        for indx, item in enumerate(s._items):
            week = cal[indx] if indx < len(cal) else []
            fmt_week = [('%02d' % day) if day else '' for day in week]
            s._calendar.item(item, values=fmt_week)

    def _show_select(s, text, bbox):
        """为新的选择配置画布。"""
        x, y, width, height = bbox

        textw = s._font.measure(text)

        canvas = s._canvas
        canvas.configure(width=width, height=height)
        canvas.coords(canvas.text, (width - textw) / 2, height / 2 - 1)
        canvas.itemconfigure(canvas.text, text=text)
        canvas.place(in_=s._calendar, x=x, y=y)

    def _pressed(s, evt=None, item=None, column=None, widget=None):
        """在日历的某个地方点击。"""
        if not item:
            x, y, widget = evt.x, evt.y, evt.widget
            item = widget.identify_row(y)
            column = widget.identify_column(x)

        if not column or not item in s._items:
            # 在工作日行中单击或仅在列外单击。
            return

        item_values = widget.item(item)['values']
        if not len(item_values):  # 这个月的行是空的。
            return

        text = item_values[int(column[1]) - 1]
        if not text:  # 日期为空
            return

        bbox = widget.bbox(item, column)
        if not bbox:  # 日历尚不可见
            s.master.after(20, lambda: s._pressed(item=item, column=column, widget=widget))
            return

        # 更新，然后显示选择
        text = '%02d' % text
        s._selection = (text, item, column)
        s._show_select(text, bbox)

    def _prev_month(s):
        """更新日历以显示前一个月。"""
        s._canvas.place_forget()
        s._selection = None

        s._date = s._date - timedelta(days=1)
        s._date = datetime(s._date.year, s._date.month, 1)
        s.CB_year.set(s._date.year)
        s.CB_month.set(s._date.month)
        s._update()

    def _next_month(s):
        """更新日历以显示下一个月。"""
        s._canvas.place_forget()
        s._selection = None

        year, month = s._date.year, s._date.month
        s._date = s._date + timedelta(
            days=calendar.monthrange(year, month)[1] + 1)
        s._date = datetime(s._date.year, s._date.month, 1)
        s.CB_year.set(s._date.year)
        s.CB_month.set(s._date.month)
        s._update()

    def _update(s, event=None, key=None):
        """刷新界面"""
        if key and event.keysym != 'Return': return
        year = int(s.CB_year.get())
        month = int(s.CB_month.get())
        if year == 0 or year > 9999: return
        s._canvas.place_forget()
        s._date = datetime(year, month, 1)
        s._build_calendar()  # 重建日历

        if year == datetime.now().year and month == datetime.now().month:
            day = datetime.now().day
            for _item, day_list in enumerate(s._cal.monthdayscalendar(year, month)):
                if day in day_list:
                    item = 'I00' + str(_item + 2)
                    column = '#' + str(day_list.index(day) + 1)
                    s.master.after(100, lambda: s._pressed(item=item, column=column, widget=s._calendar))

    def _exit(s, confirm=False):
        """退出窗口"""
        if not confirm: s._selection = None
        s.master.destroy()

    def _main_judge(s):
        """判断窗口是否在最顶层"""
        try:
            # s.master 为 TK 窗口
            # if not s.master.focus_displayof(): s._exit()
            # else: s.master.after(10, s._main_judge)

            # s.master 为 toplevel 窗口
            if s.master.focus_displayof() == None or 'toplevel' not in str(s.master.focus_displayof()):
                s._exit()
            else:
                s.master.after(10, s._main_judge)
        except:
            s.master.after(10, s._main_judge)

        # s.master.tk_focusFollowsMouse() # 焦点跟随鼠标

    def selection(s):
        """返回表示当前选定日期的日期时间。"""
        if not s._selection: return None

        year, month = s._date.year, s._date.month
        return str(datetime(year, month, int(s._selection[0])))[:10]

    def Input_judgment(s, content):
        """输入判断"""
        # 如果不加上==""的话，就会发现删不完。总会剩下一个数字
        if content.isdigit() or content == "":
            return True
        else:
            return False

#正片开始
window=tk.Tk()
window.title('Decade')
window.geometry('500x600')

canvas=tk.Canvas(window,height=200,width=500)
image_file=tk.PhotoImage(file='04.gif')
image=canvas.create_image(0,0,anchor='nw',image=image_file)
canvas.pack(side='top')

tk.Label(window,text='User name:').place(x=50,y=250)
tk.Label(window,text='Password:').place(x=50,y=290)

var_name=tk.StringVar()
var_name.set('example@163.com')
entry_name=tk.Entry(window,textvariable=var_name)
entry_name.place(x=160,y=250)
var_pwd=tk.StringVar()
entry_name=tk.Entry(window,textvariable=var_pwd,show='*')
entry_name.place(x=160,y=290)

def login():
    usr_name=var_name.get()
    usr_pwd=var_pwd.get()
    usr_type=var_type.get()
    try:
        with open('usrs_info.pickle','rb') as usr_file:
            usrs_info=pickle.load(usr_file)
    except FileNotFoundError:
        with open('usrs_info.pickle','wb') as usr_file:
            usrs_info={'ID':'3'}
            pickle.dump(usrs_info,usr_file)
    if usr_name in usrs_info:
        if usr_pwd==usrs_info[usr_name]:
            tk.messagebox.showinfo(title='Welcome',message='How are you?'+usr_name)
        else:
            tk.messagebox.showerror(message='Error,your password is wrong,try again')
    else:
        is_sign_up=tk.messagebox.askyesno(title='Welcome',message='You have not sign up yet.Sign up today?')
        if is_sign_up:
            sign_up()
    os.remove('usrs_info.pickle')

    window.destroy()
    if usr_type=='C':
        window_C()
    elif usr_type=='B':
        window_B()
    else:
        window_A()
def window_A():


    window1 = tk.Tk()
    window1.title("Welcome")
    window1.geometry('300x200')

    canvas = tk.Canvas(window1, height=200, width=200)
    image_file = tk.PhotoImage(file='05.gif')
    image = canvas.create_image(0, 0, anchor='n', image=image_file)
    canvas.pack(side='left')

    var = tk.StringVar()

    def order():
        window_order = tk.Toplevel(window1)
        window_order.title('Order Time')
        window_order.geometry('300x300')

        width, height = window_order.winfo_reqwidth() + 50, 50  # 窗口大小
        x, y = (window_order.winfo_screenwidth() - width) / 2, (window_order.winfo_screenheight() - height) / 2

        date_str = tk.StringVar()
        date = ttk.Entry(window_order, textvariable=date_str)
        date.place(x=80, y=50)

        date_str_gain = lambda: [
            date_str.set(date)
            for date in [Calendar((x, y), 'ur').selection()]
            if date]

        tk.Button(window_order, text='预订日期', command=date_str_gain, relief='groove').place(x=20, y=50)
        tk.Label(window_order, text='预定天数:').place(x=20, y=90)
        tk.Label(window_order, text='信用卡号:').place(x=20, y=130)

        var_days = tk.StringVar()
        entry_days = tk.Entry(window_order, textvariable=var_days)
        entry_days.place(x=80, y=90)
        var_money = tk.StringVar()
        entry_money = tk.Entry(window_order, textvariable=var_money)
        entry_money.place(x=80, y=130)

        var_type = tk.StringVar()
        r1 = tk.Radiobutton(window_order, text='常规预订', variable=var_type, value=1)
        r1.place(x=30, y=190)
        r2 = tk.Radiobutton(window_order, text='预付金预订', variable=var_type, value=0)
        r2.place(x=30, y=220)

        btn_order = tk.Button(window_order, text='确定', command=order_confirm, relief='groove', bg='pink').place(x=240,
                                                                                                                y=220)

    def order_confirm():
        pass

    def order_info():
        window_order_info = tk.Toplevel(window1)
        window_order_info.title('Order Info')
        window_order_info.geometry('350x200')

        var2 = tk.StringVar()
        lb = tk.Listbox(window_order_info, listvariable=var2)
        list_items = [1, 2, 3, 4]
        for item in list_items:
            lb.insert('end', item)
        lb.place(x=5, y=5)

        def order_change():
            value = lb.get(lb.curselection())
            print(value)
            pass

        def order_cancel():
            pass

        btn_order_change = tk.Button(window_order_info, text='取消预订', command=order_change, relief='groove',
                                     bg='pink').place(x=200, y=50)
        btn_order_cancel = tk.Button(window_order_info, text='更改预定', command=order_cancel, relief='groove',
                                     bg='pink').place(x=200, y=100)

    btn_order = tk.Button(window1, text='预订', command=order, relief='groove', bg='pink').place(x=150, y=50)
    btn_order_info = tk.Button(window1, text='查看我的订单', command=order_info, relief='groove', bg='pink').place(x=150,
                                                                                                             y=100)

    window1.mainloop()
def window_B():
    window1 = tk.Tk()
    window1.title("Welcome")
    window1.geometry('292x300')

    canvas = tk.Canvas(window1, height=292, width=300)
    image_file = tk.PhotoImage(file='06.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.pack(side='top')

    l1 = tk.Label(window1, text='工作要勤劳', font='清茶楷体预览版', bg='white').place(x=0, y=0)
    l2 = tk.Label(window1, text='绝对不逃跑', font='清茶楷体预览版', bg='white').place(x=0, y=30)
    l3 = tk.Label(window1, text='一路有微笑', font='清茶楷体预览版', bg='white').place(x=0, y=60)
    var = tk.StringVar()

    def check_in_confirm():
        pass

    def check_in():
        window_check_in = tk.Toplevel(window1)
        window_check_in.title('入住登记')
        window_check_in.geometry('350x200')
        l1 = tk.Label(window_check_in, text='用户姓名:').place(x=5, y=0)
        l2 = tk.Label(window_check_in, text='用户身份证号:').place(x=5, y=30)
        l3 = tk.Label(window_check_in, text='房间号:').place(x=5, y=60)
        l4 = tk.Label(window_check_in, text='入住日期:').place(x=5, y=90)

        var1 = tk.Entry(window_check_in).place(x=90, y=0)
        var2 = tk.Entry(window_check_in).place(x=90, y=30)
        var3 = tk.Entry(window_check_in).place(x=90, y=60)
        var4 = tk.Entry(window_check_in).place(x=90, y=90)
        btn_check_in = tk.Button(window_check_in, text='确定', command=check_in_confirm, relief='groove', bg='pink',
                                 width=15).place(x=180, y=150)

    def check_out_confirm():
        pass

    def check_out():
        window_check_out = tk.Toplevel(window1)
        window_check_out.title('退房')
        window_check_out.geometry('350x200')
        l1 = tk.Label(window_check_out, text='用户姓名:').place(x=5, y=0)
        l2 = tk.Label(window_check_out, text='用户身份证号:').place(x=5, y=30)
        l3 = tk.Label(window_check_out, text='房间号:').place(x=5, y=60)
        l4 = tk.Label(window_check_out, text='退房日期:').place(x=5, y=90)
        var1 = tk.Entry(window_check_out).place(x=90, y=0)
        var2 = tk.Entry(window_check_out).place(x=90, y=30)
        var3 = tk.Entry(window_check_out).place(x=90, y=60)
        var4 = tk.Entry(window_check_out).place(x=90, y=90)
        btn_check_in = tk.Button(window_check_out, text='确定', command=check_out_confirm, relief='groove', bg='pink',
                                 width=15).place(x=180, y=150)

    btn_check_in = tk.Button(window1, text='入住登记', command=check_in, relief='groove', bg='pink', width=15).place(x=30,
                                                                                                                 y=250)
    btn_check_out = tk.Button(window1, text='退房', command=check_out, relief='groove', bg='pink', width=15).place(x=150,
                                                                                                                 y=250)

    window1.mainloop()
def window_C():
    window1 = tk.Tk()
    window1.title("Welcome")
    window1.geometry('400x400')

    canvas = tk.Canvas(window1, height=300, width=400)
    image_file = tk.PhotoImage(file='07.gif')
    image = canvas.create_image(0, 0, anchor='nw', image=image_file)
    canvas.pack(side='top')

    l = tk.Label(window1, text='基价').place(x=0, y=250)
    e = tk.Entry(window1).place(x=40, y=250)
    var = tk.StringVar()

    def out1():
        window_check_in = tk.Toplevel(window1)
        window_check_in.title('预计入住报表')
        window_check_in.geometry('350x200')

    def out2():
        window_check_out = tk.Toplevel(window1)
        window_check_out.title('预计收入报表')
        window_check_out.geometry('350x200')

    def basic_price():
        pass

    btn_out1 = tk.Button(window1, text='预计入住报表', command=out1, relief='groove', bg='pink', width=15).place(x=50, y=320)
    btn_out2 = tk.Button(window1, text='预计收入报表', command=out2, relief='groove', bg='pink', width=15).place(x=50, y=360)
    btn_basic_price = tk.Button(window1, text='更改基价', command=basic_price, relief='groove', bg='pink', width=15).place(
        x=200, y=250)

    window1.mainloop()
def sign_up():
    def sign_to_python():
        np=new_pwd.get()
        npf=new_pwd_confirm.get()
        nn=new_name.get()
        with open('usrs_info.pickle','rb') as usr_file:
            exist_usr_info=pickle.load(usr_file)
        if np!=npf:
            tk.messagebox.showerror(message='Password and confirm password must be the same!')
        elif nn in exist_usr_info:
            tk.messagebox.showerror(message="The user has already signed up!")
        else:
            exist_usr_info[nn]=np
            with open('usrs_info.pickle','wb') as usr_file:
                pickle.dump(exist_usr_info,usr_file)
            tk.messagebox.showinfo(title='Welcome',message="You have successfully signed up!")
            window_sign_up.destroy()
    window_sign_up=tk.Toplevel(window)
    window_sign_up.title('Sign up')
    window_sign_up.geometry('350x250')

    new_name=tk.StringVar()
    new_name.set('example@163.com')
    tk.Label(window_sign_up,text='User name:').place(x=10,y=10)
    entry_new_name=tk.Entry(window_sign_up,textvariable=new_name)
    entry_new_name.place(x=150,y=10)

    new_pwd = tk.StringVar()
    tk.Label(window_sign_up, text='Password:').place(x=10, y=50)
    entry_new_pwd = tk.Entry(window_sign_up, textvariable=new_pwd,show='*')
    entry_new_pwd.place(x=150, y=50)

    new_pwd_confirm = tk.StringVar()
    tk.Label(window_sign_up, text='Confirm password:').place(x=10, y=90)
    entry_new_pwd_confirm = tk.Entry(window_sign_up, textvariable=new_pwd_confirm,show='*')
    entry_new_pwd_confirm.place(x=150, y=90)

    new_real_name = tk.StringVar()
    tk.Label(window_sign_up, text='Real Name:').place(x=10, y=130)
    entry_new_real_name = tk.Entry(window_sign_up, textvariable=new_real_name)
    entry_new_real_name.place(x=150, y=130)

    new_ID = tk.StringVar()
    tk.Label(window_sign_up, text='ID:').place(x=10, y=170)
    entry_new__ID = tk.Entry(window_sign_up, textvariable=new_ID)
    entry_new__ID.place(x=150, y=170)

    btn_confirm_signup=tk.Button(window_sign_up,text='Sign up',command=sign_to_python)
    btn_confirm_signup.place(x=130,y=220)

var_type= tk.StringVar()
r1=tk.Radiobutton(window,text='客户',variable=var_type,value='A')
r1.place(x=160,y=320)
r2=tk.Radiobutton(window,text='雇员',variable=var_type,value='B')
r2.place(x=160,y=340)
r3=tk.Radiobutton(window,text='管理员',variable=var_type,value='C')
r3.place(x=160,y=360)

btn_login=tk.Button(window,text='Login',command=login,relief='groove')
btn_login.place(x=170,y=400)
btn_sign_up=tk.Button(window,text='Sign up',command=sign_up,relief='groove')
btn_sign_up.place(x=270,y=400)


query_sql='select ID from person'
print(db.query_data(query_sql))

window.mainloop()