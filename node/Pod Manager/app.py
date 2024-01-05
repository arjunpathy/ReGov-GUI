import tkinter as tk
from customtkinter import *
from PIL import Image
import re
import locale
from tkinter import messagebox
from ttkbootstrap.tableview import Tableview
from CTkToolTip import *
from DTaddresses import *
from DTpod_service import StoppableHTTPServer, DTpod_service
from DTobligation_oracle import DTobligation_oracle
from DTindexing_oracle import DTindexing_oracle

from threading import Thread
from pod_manager import *
from DTutilities import *
from DTconsumerMokup import *
from DTauthenticator import *

LIGHT_BLUE= "#334155"
DARK_BLUE= "#1F2937"
LIGHT_GREEN= "#16A34A"
DARK_GREEN= "#2A8C55"
LIGHT_YELLOW="#ffbe4d"

pod_types = (NO_OBLIGATION, "Financial", 'Social', 'Medical')
pod_details = {}
DIR_PATH = os.path.abspath(os.path.dirname(__file__))
country_names= readFileData(os.path.abspath(os.path.join(DIR_PATH,"../../node/assets/files/countries.json")))

info_icon = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/info.png")))
info_icon_img = CTkImage(dark_image=info_icon, light_image=info_icon, size=(15, 15))
help_icon = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/question.png")))
help_icon_img = CTkImage(dark_image=help_icon, light_image=help_icon, size=(15, 15))
help_tooltips =['The maximum number of times\n a resource is accessible.','The time until a\n resource is accessible.','The authorized domain in\nwhich a resource is accessible.','The country in which a\n resource is accessible.']
DEFAULT_POD_LOCATION = DEFAULT_POD_LOCATION + '/' if DEFAULT_POD_LOCATION[-1] != '/' else DEFAULT_POD_LOCATION

class tkinterApp(CTk):

    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):

        # __init__ function for class Tk
        super().__init__( *args, **kwargs)
        locale.setlocale(locale.LC_ALL, 'english-american')
        set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"    
        set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

        container = CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.title("ReGov") 
        self.geometry('885x670')
        self.minsize(875,670)

        # initializing frames to an empty array
        self.frames = {}
        self.pod_btns= {}
        self.res_frame={}
        self.pods_frame={}
        for F in ["StartPage", "PodManagementPage", "PodCreatePage", "ViewResourcePage", "RegisterResourcePage","LogsPage"]:
            self.pod_btns[F] = []

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, PodManagementPage, PodCreatePage, ViewResourcePage, RegisterResourcePage,
                  LogsPage):
            frame = F(container, self)

            # initializing frame of that object from StartPage, PodManagementPage, PodCreatePage, ViewResourcePage, RegisterResourcePage, LogsPage respectively with for loop
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")
        set_appearance_mode('Dark')
        self.show_frame(StartPage)

    # to display the current frame passed as
    # parameter
    def show_frame(self, cont, data=None):
        frame = self.frames[cont]
        frame.tkraise()
        if data is not None:
            set_appearance_mode('Dark')
            frame.load_data(data)

    def fill_resources(self,pod_id,pods_file_system,pageName):
            pod_btns = self.pod_btns[pageName]
            res_frame = self.res_frame[pageName]
            for pod in pods_file_system['pods']:
                data = readFileData(DEFAULT_POD_LOCATION+pod+"/DTconfig.json")
                if data is not None:
                    pods_file_system['hierarchy'][pod] =  data['resources'].keys()
            for widgets in res_frame.winfo_children():
                widgets.destroy()
            label = CTkLabel(res_frame, compound='left',text="Resource\nList", font=("Arial Bold", 11),text_color='white')
            label.pack(anchor='center',pady=(0,2))
            if (pod_id in pods_file_system['hierarchy']):
                for res in pods_file_system['hierarchy'][pod_id]:
                    # CTkButton(res_frame,text="Res "+res,width=10,state='diabled',fg_color=LIGHT_BLUE,text_color='#fff').pack(anchor='w',pady=2)
                    CTkLabel(res_frame, text="Res "+res,width=10,font=("Arial Italic", 15),text_color=LIGHT_BLUE).pack(pady=1)

            for pod in pod_btns:
                active_color = DARK_BLUE if pod.cget('text') == "Pod "+pod_id else "#2FA572"
                pod.configure(fg_color=active_color)
        
    def update_pods_button(self,controller):
        pods_file_system = {"pods":[],'hierarchy':{}}
        dir_path = DEFAULT_POD_LOCATION
        self.pod_btns = {}
        for file_path in os.listdir(dir_path):
            if os.path.isdir(os.path.join(dir_path, file_path)):
                pods_file_system['pods'].append(file_path)
        for pageName in ["StartPage", "PodManagementPage", "PodCreatePage", "ViewResourcePage", "RegisterResourcePage","LogsPage"]:
            for widgets in self.pods_frame[pageName].winfo_children():
                widgets.destroy()
        pods_file_system['pods'] = sorted(pods_file_system['pods'], key=lambda x: int(x))
        for pageName in ["StartPage", "PodManagementPage", "PodCreatePage", "ViewResourcePage", "RegisterResourcePage","LogsPage"]:
            self.pod_btns[pageName]=[]  
          
            label = CTkLabel(self.pods_frame[pageName], compound='left',text="Pod List", font=("Arial Bold", 12),text_color='white')
            label.pack(anchor='w',pady=0)

            for pod in pods_file_system['pods']:
                btn = CTkButton(self.pods_frame[pageName],text="Pod "+pod,width=15,command=lambda pageName=pageName,pod=pod:controller.fill_resources(pod,pods_file_system,pageName),border_width=1,border_color="#fff")
                btn.pack(anchor='w',pady=2)
                self.pod_btns[pageName].append(btn)

                

    def create_sidebar(self,page,controller,pageName):        
                
        # Sidebar code
        sidebar_frame = CTkFrame(page, fg_color=DARK_GREEN, width=175, height=670, corner_radius=0)
        sidebar_frame.pack_propagate(0)
        sidebar_frame.pack( anchor="w", side="left",fill='both')
        pods_file_system = {"pods":[],'hierarchy':{}}
        dir_path = DEFAULT_POD_LOCATION

        for file_path in os.listdir(dir_path):
            if os.path.isdir(os.path.join(dir_path, file_path)):
                pods_file_system['pods'].append(file_path)

        logo_img_data = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/blockchain.png")))
        logo_img = CTkImage(dark_image=logo_img_data, light_image=logo_img_data, size=(100,100))
        CTkLabel(sidebar_frame, text="", image=logo_img).pack(pady=(38, 0), anchor="center")
        pod_icon_data = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/pod.png")))
        pod_icon = CTkImage(dark_image=pod_icon_data, light_image=pod_icon_data)

        frame = CTkFrame(sidebar_frame,fg_color='transparent',width=155,border_color='#fff',border_width=1)
        # label = CTkLabel(frame, image=pod_icon,compound='left',text="  Available Pods", font=("Arial Bold", 14),text_color='white')
        label = CTkLabel(frame, compound='left',text="View Pod-Resource", font=("Arial Bold", 14),text_color='white')
        label.pack(pady=(6,0))

        frame2 = CTkFrame(frame,fg_color='transparent',width=155)
        label2 = CTkLabel(frame2, compound='left',text="Hierarchy  ", font=("Arial Bold", 14),text_color='white')
        label2.pack(anchor='n',side='left')
        help_icon = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/question.png")))
        help_icon_img = CTkImage(dark_image=help_icon, light_image=help_icon, size=(13, 13))
        help_icon1=CTkLabel(frame2, text="", image=help_icon_img, width=15, height=15,)
        help_icon1.pack(side='left')
        frame2.pack(pady=0)

        tooltip = CTkToolTip(help_icon1, delay=0.5,padding=(5,5),text_color="black",bg_color=LIGHT_YELLOW,border_color='white',border_width=1,message='Click on a pod to\nlist its resources')
    
        self.pods_frame[pageName] = CTkScrollableFrame(frame,width=53,fg_color='transparent',scrollbar_button_color=DARK_GREEN,scrollbar_button_hover_color="#207244")
        self.pods_frame[pageName].pack(side="left",padx=5,pady=5,fill='y')

        self.res_frame[pageName] = CTkScrollableFrame(frame,width=57,fg_color='transparent',scrollbar_button_color=DARK_GREEN,scrollbar_button_hover_color="#207244")
        self.res_frame[pageName].pack(side="left",padx=2,pady=5,fill='y')


        frame.pack(pady=(260,5),padx=5,fill='both',expand=True)
        pods_file_system['pods'] = sorted(pods_file_system['pods'], key=lambda x: int(x))
        label = CTkLabel(self.pods_frame[pageName], compound='left',text="Pod List", font=("Arial Bold", 12),text_color='white')
        label.pack(anchor='w',pady=0)

        for pod in pods_file_system['pods']:
            btn = CTkButton(self.pods_frame[pageName],text="Pod "+pod,width=15,command=lambda pod=pod:controller.fill_resources(pod,pods_file_system,pageName),border_width=1,border_color='white')
            btn.pack(anchor='w',pady=2)
            self.pod_btns[pageName].append(btn)

    def invoke_button(self,controller,id,page):
        for btn in controller.pod_btns[page]:
            if btn.cget('text')=='Pod '+id:
                btn.invoke()

# first window frame startpage
class StartPage(CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.create_sidebar(self,controller,'StartPage')
        def open_pod():
            pod_location = filedialog.askdirectory()
            print(pod_location)
            if pod_location:
                config = readFileData(pod_location + "/DTconfig.json")
                obligations = readFileData(pod_location + '/DTobligations.json')
                if config is None or obligations is None:
                    messagebox.showerror(title="Error", message="Invalid Pod Location! No Pod Selected.")
                else:
                    data = {"config": config, "path": pod_location, "obligations": obligations}
                    controller.show_frame(PodManagementPage, data)

        package_img_data = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/package.png")))
        package_img = CTkImage(dark_image=package_img_data, light_image=package_img_data, size=(40, 40))

        register_pod_data = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/new_pod.png")))
        register_pod_icon = CTkImage(dark_image=register_pod_data, light_image=register_pod_data, size=(40, 40))

        main_view = CTkFrame(self, width=690, height=650, corner_radius=0, fg_color=DARK_BLUE)
        main_view.pack_propagate(0)
        main_view.pack(side="left", fill='both',expand=True)

        CTkLabel(master=main_view, text="Welcome to Pod Manager", text_color=DARK_GREEN, font=("Arial Bold", 35)).pack(anchor="center", ipady=5, pady=(160, 0))

        pods_container = CTkFrame(master=main_view, fg_color="transparent")
        pods_container.pack(anchor="center", fill="x", padx=27, pady=(36, 0))

        # Create a horizontal container frame for the buttons
        button_container = CTkFrame(master=pods_container, fg_color="transparent")
        button_container.pack(anchor="center")

        CTkButton(master=button_container, image=package_img, compound='top', text="Open Existing Pod",width=180,corner_radius=15,
                  command=open_pod, fg_color=LIGHT_BLUE, font=("Arial Bold", 14),
                  text_color= LIGHT_GREEN, hover_color='#eee', anchor="center").pack(side="left", ipady=5, pady=(16, 0),padx=3)

        CTkButton(master=button_container, image=register_pod_icon, compound='top', text="Register New Pod",width=180,corner_radius=15,
                  fg_color=LIGHT_BLUE, font=("Arial Bold", 14), text_color=LIGHT_GREEN, hover_color="#eee", anchor="center",
                  command=lambda: controller.show_frame(PodCreatePage,DEFAULT_POD_LOCATION)).pack(side="left", ipady=5, pady=(16, 0),padx=3)

class Popup(CTkToplevel):
    def __init__(self,parent,type=None,val=None,title=None):
        super().__init__(parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.mystring = StringVar(self)
        if(type=='country'):
            self.geometry("500x330")
            self.minsize(500,330)
        else:
            self.geometry("480x210")
            self.minsize(480,210)

        self.title("Edit Obligations for "+title)
        self.configure(fg_color=DARK_BLUE)
        label_text = "Access Counter" if type == "access_counter" else "Temporal Obligation" if type == "temporal" else "Domain Obligation" if type == "domain" else "Country Obligation"
        frame = CTkFrame(self, corner_radius=10,fg_color=LIGHT_BLUE)
        CTkLabel(frame, text='New '+label_text+' Value : ',text_color='white').grid(row=0, column=0, padx=20,pady=7)
        if type == "country":
            frame.pack(padx=10,pady=10,fill='y')
            country_list = CTkScrollableFrame(frame, height=100, width=200, corner_radius=10, fg_color=DARK_BLUE,orientation='vertical')
            country_list.grid(row=0, column=1, padx=5,pady=5)
            self.scrollable_frame_radios = []
            val = '0' if val == "Unrestricted" else str(country_names['countries'].index(val))
            self.mystring = StringVar(value=val)
            self.entry = CTkEntry(frame, textvariable=self.mystring, width=100)
            for i,name in enumerate(country_names['countries']):    
                radio = CTkRadioButton(country_list, text=name,variable=self.mystring,value=str(i),font=('Arial',12),text_color='white')
                radio.grid(row=i, column=0, padx=1, pady=(0, 2),sticky='w')
                self.scrollable_frame_radios.append(radio)
        elif type == "domain":
            frame.pack(padx=10,pady=10)
            pod_domains = [NO_OBLIGATION, "Financial", "Social", "Medical"]
            self.mystring = StringVar(value=pod_domains[0])  # set initial value
            self.entry = CTkComboBox(frame, values=pod_domains, variable=self.mystring,
                                   width=150, button_color=DARK_GREEN, border_color=DARK_GREEN, border_width=1,
                                   button_hover_color="#207244", dropdown_hover_color="#207244",
                                   dropdown_fg_color=DARK_GREEN, dropdown_text_color="#fff")
            self.entry.grid(row=0, column=1, padx=10,pady=5)
        elif type =='temporal':
            frame.pack(padx=10,pady=10)
            self.days = StringVar(value="0")
            self.hours = StringVar(value="0")
            self.minutes = StringVar(value="0")
            self.seconds = StringVar(value="0")
            timestamp_frame = CTkFrame(frame, corner_radius=10,fg_color='transparent')
            timestamp_frame.grid(row=0, column=1, padx=1,pady=5)
            frame1 = CTkFrame(timestamp_frame,fg_color='transparent')
            frame2 = CTkFrame(timestamp_frame,fg_color='transparent')
            CTkLabel(frame1,text='Days', font=('Arial',12),text_color='white').pack(side='left',pady=3, padx=(4,10))
            CTkLabel(frame1,text='Hrs', font=('Arial',12),text_color='white').pack(side='left',pady=3, padx=9)
            CTkLabel(frame1,text='Mins', font=('Arial',12),text_color='white').pack(side='left',pady=3, padx=10)
            CTkLabel(frame1,text='Secs', font=('Arial',12),text_color='white').pack(side='left',pady=3, padx=10)
            CTkEntry(frame2,width=40,placeholder_text="Days", textvariable=self.days,border_width=1).pack(side='left',padx=2)
            CTkEntry(frame2,width=40,placeholder_text="Hrs", textvariable=self.hours,border_width=1).pack(side='left',padx=2)
            CTkEntry(frame2,width=40,placeholder_text="Mins",textvariable=self.minutes,border_width=1).pack(side='left',padx=2)
            CTkEntry(frame2,width=40,placeholder_text="Secs",textvariable=self.seconds,border_width=1).pack(side='left',padx=2)
            frame1.pack()
            frame2.pack()
            self.mystring =StringVar(value="0")
        else:
            frame.pack(padx=5,pady=10)
            self.entry = CTkEntry(frame, textvariable=self.mystring, width=200, border_width=1)
            self.entry.grid(row=0, column=1, padx=10,pady=5)

        self.error_msg = StringVar(value='')
        error_msg_label = CTkLabel(frame,textvariable=self.error_msg, font=('Arial',12), text_color='#FF4847')
        error_msg_label.grid(row=1, column=1, columnspan=2, pady=2)
        action_row = 2 if type != 'country'else 1
        actions = CTkFrame(frame,fg_color='transparent')
        pady = (4,4) if type == 'country' else (4,10)
        actions.grid(row=action_row, column=0, columnspan=2, pady= pady)

        self.ok_button = CTkButton(actions, width=60, text='Ok', command=lambda: self.on_button(type))
        self.ok_button.grid(row=0, column=0, padx=(0, 10),pady=(0,2))
        self.cancel_button = CTkButton(actions, width=60, text='Cancel',command=lambda:self.withdraw())
        self.cancel_button.grid(row=0, column=1,pady=(0,2))


        info_frame =  CTkFrame(self, corner_radius=10,fg_color=DARK_BLUE)
        info_frame.pack(padx=10, pady=10, side='bottom', fill='x')
        info_text = "  To make it 'Unrestricted' leave the value field empty and click Ok." if type=='access_counter' else "  To make it 'Unrestricted fill all fields with 0 and click Ok." if type=='temporal' else "  To make it 'Unrestricted' select the first option and click Ok."
        CTkLabel(info_frame,image=info_icon_img,compound='left',text=info_text,text_color='white').pack(anchor='center', padx=5)

    def on_button(self,type):

        if type == 'temporal':
            for i in [self.days,self.hours,self.minutes,self.seconds]:
                if (i.get() == ''):
                    i.set(0)
            if(not re.findall(pattern='^\d{1,45}$', string=self.days.get()) or not re.findall(pattern='^\d{1,45}$', string=self.hours.get()) or not re.findall(pattern='^\d{1,45}$', string=self.minutes.get()) or not re.findall(pattern='^\d{1,45}$', string=self.seconds.get())):
                self.error_msg.set("All values should be numerical\nand non-negative")
                return
            else:
                self.new_value = "" if (self.days.get()=='0' and self.hours.get()=='0' and self.minutes.get()=='0' and self.seconds.get()=='0') else str(int(self.days.get()) * 86400 + int(self.hours.get()) * 3600 + int(self.minutes.get()) * 60 + int(self.seconds.get()))
        else:
            self.new_value = self.mystring.get() 
        self.new_value = "" if type=='country' and self.new_value == "0" else self.new_value
        if(self.new_value == ''):
            self.destroy()  # Close the popup window
        else:
            if (type != 'domain' and not re.findall(pattern='^\d*$', string=self.new_value)):
                self.error_msg.set("Value should be numerical\nand non-negative")
            elif (type == 'access_counter' and re.findall(pattern='^\d*$', string=self.new_value) and int(self.new_value)>1000000):
                self.error_msg.set("Maximum value is 1000000")
            elif (type == 'temporal' and int(self.new_value) <= 86400 ):
                self.error_msg.set("Value should be more than a day")
            elif (type == 'temporal' and int(self.new_value) > 86400000 ):
                self.error_msg.set("Maximum value is 1000 days")
            elif (type == 'domain' and not self.new_value in pod_types):
                self.error_msg.set("Invalid Domain Obligation")
            else:
                self.destroy()

    def get_new_value(self):
        return self.new_value

# Pod Management Page : dashboard to view pod info and edit default pod obligations
class PodManagementPage(CTkFrame):

    def load_data(self, data):
        pod_data = data['config']
        print(pod_data)
        pod_path = data['path']
        self.access_control_input.delete(0, END)
        self.controller.port_number.delete(0, END)
        self.controller.port_number.insert(0, 8080)
        if len(data['path']) >40 :
            pod_path = data['path'][0:35]+'...'
            message = '\n'.join([data['path'][i:i+30] for i in range(0, len(data['path']), 30)])
            tooltip = CTkToolTip(self.controller.pod_path, delay=0.2,padding=(5,5),text_color="White" ,bg_color=DARK_BLUE,border_color='white',border_width=1,message=message)
        self.controller.pod_location = data['path']
        self.controller.pod_id.configure(text=pod_data['id'])
        self.controller.pod_address.configure(text=pod_data['address'])
        self.controller.pod_path.configure(text=pod_path)
        self.controller.pod_owner.configure(text=pod_data['owner'])
        self.controller.obligations = data['obligations']
        self.controller.config = pod_data
        self.access_control_list("load")
        self.refresh_layout()
        self.display_resource_widgets()
        self.controller.selected_pod_id = pod_data['id']
        self.controller.invoke_button(self.controller,pod_data['id'],'PodManagementPage')

    def display_resource_widgets(self):
        CTkLabel(master=self.controller.row2_frame, width=20, text="Resources", font=("Arial Bold", 14),text_color="#eee").grid(row=0, column=0, sticky="nw")
        btn_frame = CTkFrame(self.controller.row2_frame,fg_color="transparent")
        btn1 = CTkButton(btn_frame,width=60, text="Add New",fg_color=DARK_BLUE, border_width=1, border_color='white',command=lambda: self.controller.show_frame(RegisterResourcePage, self.controller.config['id']))
        btn1.pack(side='left',padx=2)
        btn2 = CTkButton(btn_frame, text="View", width=60, fg_color=DARK_BLUE, border_width=1, border_color='white',command=lambda: self.controller.show_frame(ViewResourcePage, self.controller.config['id']))
        btn2.pack(side='left',padx=2)
        btn3 = CTkButton(btn_frame, text="Logs", width=60,fg_color=DARK_BLUE, border_width=1, border_color='white',command=lambda: self.controller.show_frame(LogsPage, {"pod_id":self.controller.config['id'],'page':"PodPage"}))
        btn3.pack(side='left',padx=2)
        btn_frame.grid(row=2, column=0, columnspan=2)

    def read_config(self):
        if not hasattr(self.controller, 'pod_location'):
            self.controller.pod_location = DEFAULT_POD_LOCATION + ""
        config = readFileData(self.controller.pod_location + "/DTconfig.json")
        self.controller.config = config
        self.controller.pod_pk = config["private_key"]

    def open_edit_popup(self,type_variable,val=None):
        try:
            title= "Pod "+ self.controller.selected_pod_id
            popup = Popup(self,type_variable,val,title)
            popup.focus() 
            self.wait_window(popup)  # Wait for the popup to close
            new_value =popup.get_new_value()
            if type_variable == 'domain':
                new_value = '' if new_value == NO_OBLIGATION else str(pod_types.index(new_value)-1)
            print("new_value", new_value)
            self.update_default_obligations(new_value, type_variable)
        except Exception as e:
            print("Popup closed ")
            print("Retrying...")
            self.update_default_obligations(new_value, type_variable)


    def refresh_layout(self):
        print("Refreshing...")
        
        for widget in self.controller.obligations_frame.winfo_children():
            widget.destroy()

        self.read_config()
        self.controller.obligations = readFileData(self.controller.pod_location + "/DTobligations.json")
        self.controller.obligations_oracle = DTobligation_oracle(self.controller.obligations['address'],
                                                                 self.controller.pod_pk)
        
        if(hasattr(self.controller,'monitoring_thread')):
            self.controller.obligations_oracle.stop_monitoring()

        self.controller.monitoring_thread = Thread(None, self.controller.obligations_oracle.listen_monitoring_response)
        self.controller.monitoring_thread.start()

        def_access_counter = str(self.controller.obligations['default']['access_counter']) if hasattr(self.controller,"obligations") and self.controller.obligations['default'] != {} and "access_counter" in self.controller.obligations['default'] else "Unrestricted"
        def_temporal_obligation = str(self.controller.obligations['default']['temporal']) if hasattr(self.controller,"obligations") and self.controller.obligations['default'] != {} and "temporal" in self.controller.obligations['default'] else "Unrestricted"
        def_temporal_obligation = get_time_string(def_temporal_obligation) if def_temporal_obligation != 'Unrestricted' else 'Unrestricted'
        def_domain_obligation = pod_types[(self.controller.obligations['default']['domain'])+1] if hasattr(self.controller, "obligations") and self.controller.obligations['default'] != {} and "domain" in self.controller.obligations['default'] else "Unrestricted"
        def_domain_obligation = "Unrestricted" if def_domain_obligation == '' else  def_domain_obligation
        country_obligation = country_names['countries'][(self.controller.obligations['default']['country'])] if hasattr(self.controller, "obligations") and self.controller.obligations['default'] != {} and "country" in self.controller.obligations['default'] else "Unrestricted"
        def_country_obligation = country_obligation if len(country_obligation) <14 else country_obligation[0:11]+"..."

        CTkLabel(self.controller.obligations_frame, text='Resource Obligations', font=("Arial Bold", 14),text_color='#FFF').pack()
        frames = CTkFrame(self.controller.obligations_frame, fg_color='transparent', corner_radius=10)
        frames.pack( anchor='center', padx=6, pady=3,fill='x',expand=True)

        frame1 = CTkFrame(master=frames, height=100, width=240, fg_color=DARK_BLUE, corner_radius=10)
        f1= CTkFrame(master=frame1,fg_color=DARK_BLUE,corner_radius=20,width=210)
        CTkLabel(f1, text="Access Counter", font=('Arial', 14), text_color='white').pack(side='left', padx=5)
        help_icon1=CTkLabel(f1, text="", image=help_icon_img, width=15, height=15,)
        help_icon1.pack(side='left')
        f1.pack(pady=2, padx=5)
        access_counter_val = CTkLabel(frame1, text=def_access_counter, font=('Arial Bold', 16),text_color='white')
        access_counter_val.pack(anchor='center')
        CTkButton(frame1, text="Edit", width=60, fg_color=DARK_BLUE, border_width=1, border_color='white',command=lambda:self.open_edit_popup("access_counter")).pack(
            anchor='center', pady=(5,10))
        help_tooltip1 = CTkToolTip(help_icon1, delay=0.5,padding=(5,5),text_color="black",border_width=1,border_color='white',bg_color=LIGHT_YELLOW,message=help_tooltips[0])
        frame1.pack(side='left', padx=2, pady=5,fill='both',expand=True)

        frame2 = CTkFrame(master=frames, height=100, width=220, fg_color=DARK_BLUE, corner_radius=10)
        f2= CTkFrame(frame2,fg_color=DARK_BLUE,corner_radius=20,width=210)
        CTkLabel(f2, text="Temporal Obligation", font=('Arial', 14),text_color='white').pack(side='left', padx=5)
        help_icon2=CTkLabel(f2, text="", image=help_icon_img, width=15, height=15)
        help_icon2.pack(side='left')
        f2.pack(pady=2, padx=5)
        access_counter_val = CTkLabel(frame2, text=def_temporal_obligation, font=('Arial Bold', 16),text_color='white')
        access_counter_val.pack(anchor='center')
        CTkButton(frame2, text="Edit", width=60, fg_color=DARK_BLUE, border_width=1, border_color='white',command=lambda:self.open_edit_popup("temporal")).pack(
            anchor='center', pady=(5,10))
        help_tooltip2 = CTkToolTip(help_icon2, delay=0.5,padding=(5,5),text_color="black",border_width=1,border_color='white',bg_color=LIGHT_YELLOW,message=help_tooltips[1])
        frame2.pack(side='left', padx=2, pady=5,fill='both',expand=True)

        frame3 = CTkFrame(master=frames, height=100, width=220, fg_color=DARK_BLUE, corner_radius=10)
        f3= CTkFrame(frame3,fg_color=DARK_BLUE,corner_radius=20,width=210)
        CTkLabel(f3, text="Domain Obligation", font=('Arial', 14),text_color='white').pack(side='left', padx=5)
        help_icon3=CTkLabel(f3, text="", image=help_icon_img, width=15, height=15)
        help_icon3.pack(side='left')
        f3.pack(pady=2, padx=5)
        access_counter_val = CTkLabel(frame3, text=def_domain_obligation, font=('Arial Bold', 16),text_color='white')
        access_counter_val.pack(anchor='center')
        CTkButton(frame3, text="Edit", width=60, fg_color=DARK_BLUE, border_width=1, border_color='white',command=lambda:self.open_edit_popup("domain")).pack(
            anchor='center', pady=(5,10))
        help_tooltip3 = CTkToolTip(help_icon3, delay=0.5,padding=(5,5),text_color="black",border_width=1,border_color='white',bg_color=LIGHT_YELLOW,message=help_tooltips[2])
        frame3.pack(side='left', padx=2, pady=5,fill='both',expand=True)

        frame4 = CTkFrame(master=frames, height=100, width=250 , fg_color=DARK_BLUE, corner_radius=10)
        f4= CTkFrame(frame4,fg_color=DARK_BLUE,corner_radius=20,width=210)
        CTkLabel(f4, text="Country Obligation", font=('Arial', 14),text_color='white').pack(side='left', padx=(4,3))
        help_icon4=CTkLabel(f4, text="", image=help_icon_img, width=15, height=15)
        help_icon4.pack(side='left')
        f4.pack(pady=2, padx=10)
        access_counter_val = CTkLabel(frame4, text=def_country_obligation, font=('Arial Bold', 16),text_color='white')
        access_counter_val.pack(anchor='center')
        CTkButton(frame4, text="Edit", width=60, fg_color=DARK_BLUE, border_width=1, border_color='white',command=lambda:self.open_edit_popup("country",country_obligation)).pack(anchor='center', pady=(5,10))
        help_tooltip4 = CTkToolTip(help_icon4, delay=0.5,padding=(5,5),text_color="black",border_width=1,border_color='white',bg_color=LIGHT_YELLOW,message=help_tooltips[3])
        tooltip_1 = CTkToolTip(access_counter_val, delay=0.5, message=country_obligation,text_color='white',bg_color=LIGHT_BLUE,border_color='white',border_width=1)
        frame4.pack(side='left', padx=2, pady=5,fill='both',expand=True)

    def access_control_list(self, action):

        pod_id = self.controller.pod_id.cget('text')
        filepath = DEFAULT_POD_LOCATION + pod_id + "/DTaccess_control_list.json"

        if (action == "update"):
            data = {"pub_keys": self.controller.whitelisted_pub_keys}
            updateFileData(data, filepath)
        elif (action == 'load'):
            whitelisted_pub_keys = readFileData(filepath)
            self.controller.whitelisted_pub_keys = [] if whitelisted_pub_keys == None else whitelisted_pub_keys[
                'pub_keys']
        for widget in self.table_label_frame.winfo_children():
            widget.destroy()
        self.table_label_frame.grid_columnconfigure(1, weight=2)

        labels = []
        delete_btns = []
        data = self.controller.whitelisted_pub_keys if hasattr(self.controller, 'whitelisted_pub_keys') else []
        for index in range(len(data)):
            key = data[index]
            frame = CTkFrame(master=self.table_label_frame, fg_color='transparent')
            frame.pack(anchor='center')
            labels.append(CTkLabel(frame, text=str(key),text_color='white'))
            delete_btns.append(CTkButton(frame, text="Delete", width=25, height=25, corner_radius=5,command=lambda idx=index: self.remove_pub_key(data, data[idx]),font=("Arial", 14), border_color="#E76F51", hover_color="#E76F51", border_width=1,fg_color='transparent', text_color="#EEE"))

            labels[index].grid(row=index,column = 0, padx =10, pady=3)
            delete_btns[index].grid(row=index,column = 1, padx =10,pady=3)
        self.table_label_frame.pack(anchor="center", padx=20, pady=(0,20),fill='y',expand=True)

    def add_pub_key(self):
        new_key = self.access_control_input.get()

        if len(new_key)!=42 or not (re.findall(pattern='0x[a-fA-F0-9]{40}$', string=new_key)):
            messagebox.showerror(title="Error", message="Invalid Public Key !")
            return

        if new_key not in self.controller.whitelisted_pub_keys:
            pod_id = self.controller.pod_id.cget('text')
            filepath = DEFAULT_POD_LOCATION + pod_id + "/DTconfig.json"

            self.controller.whitelisted_pub_keys.append(new_key)
            self.access_control_input.delete(0, END)
            self.access_control_list("update")
            for resource_id, resource_data in self.controller.config['resources'].items():
                if new_key not in resource_data["access_control_list"]:
                    resource_data["access_control_list"].append(new_key)
            updateFileData(self.controller.config, filepath)
        else:
            messagebox.showerror(title="Error", message="Public key already whitelisted !")
            return

    def remove_pub_key(self, data, pub_key):
        pod_id = self.controller.pod_id.cget('text')
        filepath = DEFAULT_POD_LOCATION + pod_id + "/DTconfig.json"
        data.remove(pub_key)
        self.controller.whitelisted_pub_keys = data
        self.access_control_list("update")
        for resource_id, resource_data in self.controller.config['resources'].items():
            if pub_key in resource_data["access_control_list"]:
                resource_data["access_control_list"].remove(pub_key)
        updateFileData(self.controller.config, filepath)

    def update_default_obligations(self, value, type_variable):
        if (value == '' or value is None):
            self.remove_default_obligations(type_variable)
        elif (re.findall(pattern='^\d*$', string=value)):
            self.send_default_obligation(type_variable, int(value))
        else:
            print("Special Case ",type_variable,value)

    def create_label_pair(self,label_text, value_text, frame):
        label_frame = CTkFrame(frame, fg_color="transparent")
        CTkLabel(label_frame, text=label_text, font=("Arial Bold", 14),text_color=LIGHT_GREEN).pack(side='left', padx=5)
        value_label = CTkLabel(label_frame, text=value_text, font=("Arial", 13),text_color='white')
        value_label.pack(side='left', padx=5)
        label_frame.pack(fill="x", padx=10, pady=0, anchor="w")
        return value_label

    """
    Starts the recording of a new default obligation rules.
    """

    def send_default_obligation(self, type, value):
        try:
            if type == 'access_counter':
                self.controller.obligations_oracle.set_default_access_counter_obligation(value)
            elif type == 'temporal':
                self.controller.obligations_oracle.set_default_temporal_obligation(value)
            elif type == 'domain':
                self.controller.obligations_oracle.set_default_domain_obligation(value)
            elif type == 'country':
                self.controller.obligations_oracle.set_default_country_obligation(value)
            self.write_default_obligations(type, value)
            self.refresh_layout()
        except Exception as e:
            if(hasattr(e,'code') and e.code == 1000):
                self.send_default_obligation(self, type, value)
            else:
                print("Error : "+repr(e))

    """
    Starts the deactivation of a default country obligation rule.
    """

    def remove_default_obligations(self, type):
        try:
            if type == 'access_counter':
                self.controller.obligations_oracle.deactivate_default_access_counter_obligation()
            elif type == 'temporal':
                self.controller.obligations_oracle.deactivate_default_temporal_obligation()
            elif type == 'domain':
                self.controller.obligations_oracle.deactivate_default_domain_obligation()
            elif type == 'country':
                self.controller.obligations_oracle.deactivate_default_country_obligation()
            print(self.reset_default_obligation_json(type))
            self.refresh_layout()
        except Exception as e:
            if(hasattr(e,'code') and e.code == 1000):
                self.remove_default_obligations(type)
            else:
                print("Error : "+repr(e))
    """
    Records a new rule in the local DTobligation.json file
    """

    def write_default_obligations(self, obligation_name, value):
        obligations = readFileData(self.controller.pod_location + "/DTobligations.json")
        obligations['default'][obligation_name] = value
        updateFileData(obligations, self.controller.pod_location + "/DTobligations.json")
        self.controller.obligations = obligations
        return True

    """
    Remove an obligation rule from the local DTobligations.json file
    """

    def reset_default_obligation_json(self, obligation_name):
        obligations = readFileData(self.controller.pod_location + "/DTobligations.json")
        if obligations != None:
            obligations['default'].pop(obligation_name)
            updateFileData(obligations, self.controller.pod_location + "/DTobligations.json")
            self.controller.obligations = obligations
            return True
        return False

    def start_stop_pod(self,port_number=''):
        port_number = port_number.get() if type(port_number) != type('') else port_number
        if not (re.findall(pattern='^(?:\d+|)$', string=port_number)):
            message = "Invalid port number.\nServer cannot be "
            self.controller.server_switch_value.set(not self.controller.server_switch_value.get())
            message = message+"stopped." if self.controller.server_switch_value.get() else message+"started."
            messagebox.showerror(title="Error", message=message)
            return
        port = 8080 if port_number=='' else int(port_number)
        try:
            if self.controller.server_switch_value.get():
                if(0<port and port<=65535):
                    self.start_server(port)
                    print("Server running on port " + str(port))
                    self.controller.port_number.configure(state='disabled')
                    messagebox.showinfo(title="Server Running", message="Server running on port "+ str(port))
                    self.controller.port_number_val = port
                else:
                    messagebox.showerror(title="Error", message="Port number must between 1 to 65535")
                    self.controller.server_switch_value.set(FALSE)
            else:
                self.stop_server(port)
        except Exception as e:
            print(f"An error occurred: {e}")
            messagebox.showerror(title="Error", message="An error occurred: "+repr(e))
    """
    Starts the HTTP web service for the resources delivery.
    """

    def start_server(self, port):
        def handler(*args):
            DTpod_service(self.controller.pod_pk, *args)
        self.pod = StoppableHTTPServer(('localhost', port), handler, self.controller.pod_location)
        self.thread = Thread(None, self.pod.serve_forever)
        self.thread.start()

    """
    Stops the HTTP web service for the pod.
    """

    def stop_server(self, port):
        self.controller.port_number.configure(state='normal')
        print(self.thread)
        self.pod.force_stop()

        def handler(*args):
            DTpod_service(self.controller.pod_pk, *args)

        self.pod = StoppableHTTPServer(('localhost', port), handler, self.controller.pod_location)
    
    def exit_page(self):
        if self.controller.server_switch_value.get():
            self.controller.server_switch_value.set(FALSE)
            self.start_stop_pod()
        self.controller.pod_page_title.focus_set()
        self.controller.show_frame(StartPage)

    def paste_from_clipboard(self,entry):
        entry.delete(0, END)
        entry.insert(0, app.clipboard_get())

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.create_sidebar(self,controller,'PodManagementPage')


        main_view = CTkFrame(self, width=700, height=650, corner_radius=0, fg_color=DARK_BLUE)
        main_view.pack_propagate(0)
        main_view.pack(side="left", fill='both',expand=True)

        title_frame=CTkFrame(main_view,fg_color='transparent')
        title_frame.pack(padx=10,pady=20,fill='x')
        CTkButton(title_frame,text='Back',border_color="#FFF", hover_color="#E76F51",fg_color='transparent', command=self.exit_page,border_width=1, text_color="#FFF",width=60).pack(side='left', padx=10)
        self.controller.pod_page_title = CTkLabel(master=title_frame, text="Pod Manager\t", font=("Arial Bold", 25), text_color=DARK_GREEN)
        self.controller.pod_page_title.pack(anchor='center',expand=True)

        pod_info_frame = CTkFrame(master=main_view,fg_color=LIGHT_BLUE, corner_radius=11,width=700)
        pod_info_frame.pack(anchor="center", padx=20, pady=5,fill='x')

        information_frame = CTkFrame(master=pod_info_frame,width=400,fg_color='transparent')
        information_frame.pack(side='left', padx=5, pady=(0,5))

        self.controller.pod_id = self.create_label_pair("Id: ", "",  information_frame)
        self.controller.pod_address = self.create_label_pair("Address: ", "", information_frame)
        self.controller.pod_path = self.create_label_pair("Pod path: ", "",  information_frame)
        self.controller.pod_owner = self.create_label_pair("Pod owner: ", "",  information_frame)
        information_frame.pack(side='left',padx=5)

        frame = CTkFrame(master=pod_info_frame, corner_radius=10,width=100,fg_color='transparent')
        frame.pack(side='left',padx=(5,7),fill='x',expand=True)

        row1_frame = CTkFrame(master=frame,fg_color='transparent')
        self.controller.row2_frame = CTkFrame(master=frame,fg_color='transparent')
        row1_frame.pack( pady=(10, 1), padx=(0,5))
        self.controller.row2_frame.pack(pady=(5, 8))

        CTkLabel(master=row1_frame, text="Server", font=("Arial Bold", 14), text_color="#eee").grid(row=0,column=0,sticky="nw",padx=(0,5))
        port_number = StringVar(value="8080")
        self.controller.port_number = CTkEntry(master=row1_frame, textvariable=port_number, width=80, placeholder_text='port number', border_width=1)
        self.controller.port_number.grid(row=1, column=0)

        self.controller.server_switch_value = BooleanVar(value=FALSE)
        server_switch = CTkSwitch(master=row1_frame, text="Stop / Start", font=("Arial", 13),text_color='white',variable=self.controller.server_switch_value,onvalue=TRUE, offvalue=FALSE, command=lambda: self.start_stop_pod(port_number),button_color='#D5D9DE',button_hover_color='white')
        server_switch.grid(row=1, column=1, padx=3)

        self.controller.obligations_frame = CTkFrame(master=main_view, corner_radius=12, fg_color=LIGHT_BLUE)
        self.controller.obligations_frame.pack(anchor="center", padx=20, pady=5,fill='x')

        access_control_list_frame = CTkFrame(main_view, fg_color='transparent')
        acl_label=CTkLabel(access_control_list_frame, text="Access Control List", font=("Arial Bold", 14),text_color='white')
        acl_label.pack(side='left', padx=5)
        help_icon1=CTkLabel(access_control_list_frame, text="", image=help_icon_img, width=15, height=15,)
        help_icon1.pack(side='left', padx=5)
        acl_tooltip = CTkToolTip(help_icon1, delay=0.5,padding=(5,5),text_color="black",bg_color=LIGHT_YELLOW,border_color='white',border_width=1,message='Whitelist the public key\nto access resource api')

        new_key = StringVar(value="")
        self.access_control_input = CTkEntry(access_control_list_frame, width=324, textvariable=new_key, border_width=1)
        self.access_control_input.pack(side="left", anchor='w', padx=(5, 10), pady=5)
        add_icon = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/add.png")))
        add_icon_img = CTkImage(dark_image=add_icon, light_image=add_icon, size=(20, 20))
        paste_icon = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/paste.png")))
        paste_img = CTkImage(dark_image=paste_icon, light_image=paste_icon, size=(20,20))
        paste_btn = CTkButton(master=access_control_list_frame, image=paste_img, text="", width=25, height=25,
                  command=lambda: self.paste_from_clipboard(self.access_control_input),
                  fg_color="transparent",hover_color="#eee")
        paste_btn.pack(side="left", anchor='w', pady=3)
        add_btn = CTkButton(access_control_list_frame, image=add_icon_img, text="", width=25, height=25, fg_color="transparent",
                hover_color="#eee",command=self.add_pub_key)
        add_btn.pack(side="left", anchor='w', pady=3)
        paste_tooltip = CTkToolTip(paste_btn, delay=0.5,padding=(5,5),text_color="White",bg_color=LIGHT_GREEN,border_color='white',border_width=1,message='Paste copied key\nfrom clipboard')
        add_icon_tooltip = CTkToolTip(add_btn, delay=0.5,padding=(5,5),text_color="White",bg_color=LIGHT_GREEN,border_color='white',border_width=1,message='Add key to \nAccess control list')
        access_control_list_frame.pack(anchor='center', pady=0)
        self.table_label_frame = CTkScrollableFrame(master=main_view, height=180, width=550, corner_radius=10, fg_color=LIGHT_BLUE)

class PodCreatePage(CTkFrame):

    def load_data(self, loc):
            self.pod_location_entry.delete(0, END)
            self.pod_location_entry.insert(0, loc)

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.create_sidebar(self,controller,'PodCreatePage')

        pod_domains = [ "Financial","Social", "Medical"]


        def paste_from_clipboard(entry):
            entry.delete(0, END)
            entry.insert(0, app.clipboard_get())

        def browse_button():
            pod_location = filedialog.askdirectory()
            self.pod_location_entry.delete(0, END)
            self.pod_location_entry.insert(0, pod_location)
        
        def open_pod(pod_id):
            if(pod_id is not None):
                pod_location = DEFAULT_POD_LOCATION+pod_id
                print(pod_location)
                if pod_location:
                    config = readFileData(pod_location + "/DTconfig.json")
                    obligations = readFileData(pod_location + '/DTobligations.json')
                    if config is None or obligations is None:
                        messagebox.showerror(title="Error", message="Invalid Pod Location! No Pod Selected.")
                    else:
                        data = {"config": config, "path": pod_location, "obligations": obligations}
                        controller.show_frame(PodManagementPage, data)
        
        def validate(domain_name,pod_type,public_key_pod,private_key_pod,pod_loc):
            for widget in [self.domain_name_err_msg,self.pod_type_err_msg,self.pvt_key_err_msg,self.pub_key_err_msg,self.pod_loc_err_msg] :
                widget.set("")
            if domain_name == '':
                self.domain_name_err_msg.set("Domain name cannot be empty")
            if pod_type == 'Invalid':
                self.pod_type_err_msg.set("Invalid pod type!")
            if pod_loc == '':
                self.pod_loc_err_msg.set("Pod location cannot be empty")
            elif not DEFAULT_POD_LOCATION in pod_loc:
                self.pod_loc_err_msg.set("Pod location cannot be different from configured pod location")
            if public_key_pod == '':
                self.pub_key_err_msg.set("Owner public key cannot be empty")
            elif not (re.findall(pattern='0x[a-fA-F0-9]{40}$', string=public_key_pod)):
                self.pub_key_err_msg.set("Invalid public key!")
            if private_key_pod == '':
                self.pvt_key_err_msg.set("Owner private key cannot be empty")
            if public_key_pod != '' and private_key_pod != '' and not DTauthenticator.validate_private_public_keys(public_key_pod,private_key_pod):
                messagebox.showerror(title='Error',message="Invalid private or public key!\nPlease make sure to copy keys\nwithout blank spaces.")
                return False
            return (domain_name != '' and pod_loc != '' and DEFAULT_POD_LOCATION in pod_loc and public_key_pod != '' and private_key_pod != ''and len(public_key_pod)==42 and (re.findall(pattern='0x[a-fA-F0-9]{40}$', string=public_key_pod)))

        def submit():
            domain_name = domain_name_input.get()
            pod_domain_type = pod_domains.index(pod_type.get()) if pod_type.get() in pod_domains else "Invalid"
            public_key_pod = public_key.get()
            private_key_pod = private_key.get()
            pod_loc = self.pod_location_entry.get()

            if(validate(domain_name,pod_domain_type,public_key_pod,private_key_pod,pod_loc)):

                print(domain_name, pod_domain_type, public_key_pod, private_key_pod, pod_loc)
                pod = register_pod(pod_loc, pod_domain_type, public_key_pod, private_key_pod)
                message = "Pod " + pod['id'] + " created successfully." if pod['id'] is not None else "Pod creation failed.\n"+pod['message']
                for widget in [domain_name_input, public_key, private_key, self.pod_location_entry]:
                    widget.delete(0, END)
                    widget.insert(0, "")
                self.controller.update_pods_button(self.controller)
                messagebox.showinfo(title="Pod Creation", message=message)
                open_pod(pod['id'])

        def clear_and_exit():
            pod_type.set("Financial")
            for widget in [domain_name_input, public_key, private_key,self.pod_location_entry]:
                widget.delete(0, END)
                widget.insert(0, "")
            for label in [self.domain_name_err_msg,self.pub_key_err_msg,self.pvt_key_err_msg,self.pod_type_err_msg,self.pod_loc_err_msg]:
                label.set("")
            self.controller.add_pod_title.focus_set()
            controller.show_frame(StartPage)


        main_view = CTkFrame(self, width=690, height=650, corner_radius=0, fg_color=DARK_BLUE)
        main_view.pack_propagate(0)
        main_view.pack(side="left", fill='both',expand=True)

        paste_icon = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/paste.png")))
        paste_img = CTkImage(dark_image=paste_icon, light_image=paste_icon, size=(20,20))

        title_frame=CTkFrame(main_view, fg_color='transparent')
        title_frame.pack(padx=10,pady=20,fill='x')
        CTkButton(title_frame,text='Back',command=clear_and_exit,border_color="#FFF", hover_color="#E76F51",fg_color='transparent',
                      border_width=1, text_color="#FFF",width=60).pack(side='left', padx=10)
        self.controller.add_pod_title = CTkLabel(master=title_frame, text="Create New Pod \t", font=("Arial Bold", 25), text_color=DARK_GREEN)
        self.controller.add_pod_title.pack(anchor="center")

        frame = CTkFrame(master=main_view, fg_color=LIGHT_BLUE)
        frame.pack(anchor='center')

        input_frame = CTkFrame(master=frame, fg_color="transparent")
        input_frame.pack(pady=(10,0),padx=30,fill="x",anchor='center')

        CTkLabel(master=input_frame, text="Domain Name", font=("Arial Bold", 17), text_color="#fff").grid(row=0,column=0,sticky="w",pady=(0,4))
        help_icon1=CTkLabel(input_frame, text="", image=help_icon_img, width=15, height=15,)
        help_icon1.grid(row=0,column=0,sticky="e",padx=(0,145),pady=(0,4))
        domain_name_input = CTkEntry(master=input_frame, width=260, border_width=1,takefocus=0)
        domain_name_input.grid(row=1, column=0,padx=10)

        self.domain_name_err_msg = StringVar(value='')
        domain_name_err_msg_label = CTkLabel(input_frame,textvariable=self.domain_name_err_msg, font=('Arial',12), text_color='#FF4847',fg_color="transparent")
        domain_name_err_msg_label.grid(row=2, column=0, padx=20,sticky='sw',pady = (0,3))

        CTkLabel(master=input_frame, text="Pod Type", font=("Arial Bold", 17), text_color="#fff").grid(row=0,column=1,sticky="w",pady=(0,4))
        help_icon2=CTkLabel(input_frame, text="", image=help_icon_img, width=15, height=15,)
        help_icon2.grid(row=0,column=1,sticky="e",padx=(0,155),pady=(0,4))

        pod_type = StringVar(value="Financial")  # set initial value
        combobox = CTkComboBox(master=input_frame, values=pod_domains, variable=pod_type,
                               width=255, button_color=DARK_GREEN, border_color=DARK_GREEN, border_width=1,
                               button_hover_color="#207244", dropdown_hover_color="#207244",
                               dropdown_fg_color=DARK_GREEN, dropdown_text_color="#fff")
        combobox.grid(row=1, column=1, padx=(5,0))

        self.pod_type_err_msg = StringVar(value='')
        pod_type_err_msg_label = CTkLabel(input_frame,textvariable=self.pod_type_err_msg, font=('Arial',12), text_color='#FF4847',fg_color="transparent")
        pod_type_err_msg_label.grid(row=2, column=1, padx=20,sticky='sw',pady = (0,3))


        pub_key_frame = CTkFrame(master=frame, fg_color="transparent")
        pub_key_frame.pack(fill='x',padx=27)
        CTkLabel(pub_key_frame, text="Owner Public Key", font=("Arial Bold", 17), text_color="#fff").pack(side = 'left')
        help_icon3=CTkLabel(pub_key_frame, text="", image=help_icon_img, width=15, height=15,)
        help_icon3.pack(side='left',padx = 10)

        pub_key_container = CTkFrame(master=frame, fg_color="transparent")
        pub_key_container.pack(pady=(4,0),padx=30,fill="x",anchor='center')
        self.pub_key_err_msg = StringVar(value='')
        pub_key_err_msg_label = CTkLabel(pub_key_container,textvariable=self.pub_key_err_msg, font=('Arial',12), text_color='#FF4847')
        pub_key_err_msg_label.pack(side="bottom",anchor='w',padx=20)
        public_key = CTkEntry(master=pub_key_container,width=480, border_width=1,takefocus=0)
        public_key.pack(side='left',padx=10)

        paste_btn = CTkButton(master=pub_key_container, image=paste_img, text="", width=20, height=20,
                  command=lambda public_key=public_key:paste_from_clipboard(public_key),
                  fg_color="transparent", border_color="#fff", hover_color="#eee",
                  border_width=1)
        paste_btn.pack(side='left',padx=(0,16))
        paste_tooltip = CTkToolTip(paste_btn, delay=0.5,padding=(5,5),text_color="White",bg_color=LIGHT_GREEN,border_color='white',border_width=1,message='Paste copied key\nfrom clipboard')

        pvt_key_frame = CTkFrame(master=frame, fg_color="transparent")
        pvt_key_frame.pack(fill='x',padx=27)
        CTkLabel(pvt_key_frame, text="Owner Private Key", font=("Arial Bold", 17), text_color="#fff").pack(side = 'left')
        help_icon4=CTkLabel(pvt_key_frame, text="", image=help_icon_img, width=15, height=15,)
        help_icon4.pack(side='left',padx = 10)


        pvt_key_container = CTkFrame(master=frame, fg_color="transparent")
        pvt_key_container.pack(pady=(4,0),padx=30,fill="x",anchor='center')
        self.pvt_key_err_msg = StringVar(value='')
        pvt_key_err_msg_label = CTkLabel(pvt_key_container,textvariable=self.pvt_key_err_msg, font=('Arial',12), text_color='#FF4847')
        pvt_key_err_msg_label.pack(side="bottom",anchor='w',padx=20)
        private_key = CTkEntry(master=pvt_key_container,width=480, border_width=1,show='*')
        private_key.pack(side='left',padx=10)
        paste_btn2 = CTkButton(master=pvt_key_container, image=paste_img, text="", width=20, height=20,
                  command=lambda private_key=private_key:paste_from_clipboard(private_key),
                  fg_color="transparent", border_color="#fff", hover_color="#eee",
                  border_width=1)
        paste_btn2.pack(side='left',padx=(0,10))
        paste_tooltip2 = CTkToolTip(paste_btn2, delay=0.5,padding=(5,5),text_color="White",bg_color=LIGHT_GREEN,border_color='white',border_width=1,message='Paste copied key\nfrom clipboard')

        pod_location_frame = CTkFrame(master=frame, fg_color="transparent")
        pod_location_frame.pack(fill='x',padx=27)
        CTkLabel(master=pod_location_frame, text="Pod Location", font=("Arial Bold", 17), text_color="#fff").pack(side = 'left')
        help_icon5=CTkLabel(pod_location_frame, text="", image=help_icon_img, width=15, height=15,)
        help_icon5.pack(side='left',padx = 10)

        location_container = CTkFrame(master=frame, fg_color="transparent")
        location_container.pack(anchor='center', pady=(4, 10), padx=5)

        self.pod_loc_err_msg = StringVar(value='')
        pod_loc_err_msg_label = CTkLabel(location_container,textvariable=self.pod_loc_err_msg, font=('Arial',12), text_color='#FF4847')
        pod_loc_err_msg_label.pack(side="bottom", anchor='w', padx=20) 

        pod_location = StringVar(value=DEFAULT_POD_LOCATION)
        self.pod_location_entry = CTkEntry(master=location_container, width=400, textvariable=pod_location, border_width=1)
        self.pod_location_entry.pack(side="left",padx=5)

        CTkButton(master=location_container, text="Browse", width=112,  fg_color=DARK_BLUE, border_width=1, border_color='white',hover_color=LIGHT_GREEN, command=browse_button).pack(side="left", padx=10)



        help_tooltip1 = CTkToolTip(help_icon1, delay=0.5,padding=(5,3),text_color='black',bg_color=LIGHT_YELLOW,border_color='white',border_width=1,font=("Arial", 12),message='Enter any domain name for the pod')
        help_tooltip2 = CTkToolTip(help_icon2, delay=0.5,padding=(5,3),text_color='black',bg_color=LIGHT_YELLOW,border_color='white',border_width=1,font=("Arial", 12),message="Choose a pod domain type")
        help_tooltip3 = CTkToolTip(help_icon3, delay=0.5,padding=(5,3),text_color='black',bg_color=LIGHT_YELLOW,border_color='white',border_width=1,font=("Arial", 12),message="Enter the public key of\npod owner's account")
        help_tooltip4 = CTkToolTip(help_icon4, delay=0.5,padding=(5,3),text_color='black',bg_color=LIGHT_YELLOW,border_color='white',border_width=1,font=("Arial", 12),message="Enter the private key of\npod owner's account")
        help_tooltip5 = CTkToolTip(help_icon5, delay=0.5,padding=(5,3),text_color='black',bg_color=LIGHT_YELLOW,border_color='white',border_width=1,font=("Arial", 12),message="Default location of all pods")

        CTkButton(master=frame, text="Create", width=300, command=submit, font=("Arial Bold", 17), border_width=1,border_color='white',fg_color=LIGHT_BLUE,hover_color=LIGHT_GREEN, text_color="#fff").pack(anchor='center',pady=10)

class DisplayResource(CTkToplevel):

    def __init__(self, *args, data=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("440x580")
        self.minsize(440,580)
        self.title("Resource "+data['res_id'])
        self.configure(fg_color=DARK_BLUE)

        frame = CTkFrame(self, corner_radius=10, fg_color=DARK_BLUE)
        CTkLabel(frame,text='Resource '+data['res_id'],font=("Arial Bold", 16),text_color='white').pack(padx=5,pady=2,side='top')

        response_frame = CTkFrame(frame, corner_radius=15, fg_color=LIGHT_BLUE)
        api_response_data = Image.open(os.path.abspath(os.path.join(DIR_PATH,"../../",data['image_path'])))
        response_img = CTkImage(dark_image=api_response_data, light_image=api_response_data, size=(350, 350))
        label = CTkLabel(response_frame, image=response_img, text='',corner_radius=10)
        label.pack(anchor='center',padx=10,pady=10,fill='both')
        response_frame.pack(anchor='center', fill='both', padx=10,pady=10)

        obligations_frame = CTkFrame(frame, fg_color='transparent')
        obligations_frame.pack(anchor='center', fill='both',expand=True,padx=10,pady=10)
        
        access = str(get_obligations(data,data,'access_counter')['value'])
        temporal = get_obligations(data,data,'temporal')['value']
        domain = get_obligations(data,data,'domain')['value']
        country = get_obligations(data,data,'country')['value']


        CTkLabel(obligations_frame,text_color='white',text='Access Control : '+access).pack()
        CTkLabel(obligations_frame,text_color='white',text='Temporal Obligation : '+temporal).pack()
        CTkLabel(obligations_frame,text_color='white',text='Domain Obligation : '+domain).pack()
        CTkLabel(obligations_frame,text_color='white',text='Country Obligation : '+country).pack()

        frame.pack(anchor='center', fill='both', padx=10,pady=10)

class ViewResourcePage(CTkFrame):

    def load_data(self, id):
        self.controller.selected_pod_id = id
        self.controller.invoke_button(self.controller,id,'ViewResourcePage')
        self.create_tabs()
    def exit_page(self):
        self.controller.invoke_button(self.controller,self.controller.selected_pod_id,'PodManagementPage')
        self.controller.show_frame(PodManagementPage)

    def paste_from_clipboard(self,entry):
        entry.delete(0, END)
        entry.insert(0, app.clipboard_get())

    def open_edit_popup(self,res_id,type_variable,val=None):
        try:
            title = "Res "+ str(res_id)
            popup = Popup(self,type_variable,val,title)
            popup.focus() 
            self.wait_window(popup)  # Wait for the popup to close
            new_value = popup.get_new_value()
            if type_variable == 'domain':
                new_value = '' if new_value == NO_OBLIGATION else str(pod_types.index(new_value)-1)
            print("new_value", new_value)
            self.update_obligations(res_id,new_value,type_variable)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("recv")
            self.update_obligations(res_id,new_value,type_variable)
            

    def update_obligations(self,res_id,value, type_variable):
        if (value == '' or value is None):
            self.remove_obligations(res_id,type_variable)
        elif (re.findall(pattern='^\d*$', string=value)):
            self.send_obligation(res_id,type_variable, int(value))

    def send_obligation(self, res_id, type, value):
        try:
            if type == 'access_counter':
                self.controller.obligations_oracle.set_access_counter_obligation(res_id, value)
            elif type == 'temporal':
                self.controller.obligations_oracle.set_temporal_obligation(res_id, value)
            elif type == 'domain':
                self.controller.obligations_oracle.set_domain_obligation(res_id, value)
            elif type == 'country':
                self.controller.obligations_oracle.set_country_obligation(res_id, value)

            self.controller.config['resources'][str(res_id)]['obligations'][type] = value
            self.update_config()
            self.create_tabs("Res "+str(res_id))
        except Exception as e:
            if(hasattr(e,'code') and e.code ==1000):
                self.send_obligation(res_id, type, value)
            else:
                print(f"An error occurred: {e}")
                messagebox.showerror(title="Error",message=repr(e))

    def remove_obligations(self,res_id, type):
        try:
            if type == 'access_counter':
                self.controller.obligations_oracle.deactivate_access_counter_obligation(res_id)
            elif type == 'temporal':
                self.controller.obligations_oracle.deactivate_temporal_obligation(res_id)
            elif type == 'domain':
                self.controller.obligations_oracle.deactivate_domain_obligation(res_id)
            elif type == 'country':
                self.controller.obligations_oracle.deactivate_country_obligation(res_id)
            if type in self.controller.config['resources'][str(res_id)]['obligations'] :
                del self.controller.config['resources'][str(res_id)]['obligations'][type]
            self.update_config()
            self.create_tabs("Res "+str(res_id))
        except Exception as e:
            if(hasattr(e,'code') and e.code ==1000):
                self.remove_obligations(res_id, type)
            else:
                print(f"An error occurred: {e}")
                messagebox.showerror(title="Error",message=repr(e))

    def write_default_obligations(self, obligation_name, value):
        obligations = readFileData(self.controller.pod_location + "/DTobligations.json")
        obligations['default'][obligation_name] = value
        updateFileData(obligations, self.controller.pod_location + "/DTobligations.json")
        self.controller.obligations = obligations
        return True

    def start_monitoring(self, res_id):
        print("Monitoring resource id : ", res_id)
        self.controller.obligations_oracle.start_monitoring_routine(int(res_id))
        messagebox.showinfo(title="Monitor Routine", message="Monitor routine started.\nUsage logs updated successfully.")

    def deactivate(self, res_id, current_tab):

        result = messagebox.askyesno(title='Confirmation',message='Deactivating Resource ' + res_id + '\n\nAre you sure ?')
        if result:
            deactivate_resource(int(res_id))
            self.controller.tabview.delete(current_tab)
            pod_id = self.controller.selected_pod_id
            config = readFileData(DEFAULT_POD_LOCATION + pod_id + "/DTconfig.json")
            del config['resources'][res_id]
            updateFileData(config, self.controller.pod_location + "/DTconfig.json")
            print("Deactivated " + res_id)
            self.controller.invoke_button(self.controller,pod_id,'ViewResourcePage')
            if(config['resources'] == {}):
                self.controller.show_frame(PodManagementPage)
        else:
            print("Cancelled")

    def request_resource_api(self,res_path, res_id):

            if not self.controller.server_switch_value.get():
                messagebox.showerror(title="Error", message="No active server found.\nPlease go back and start the server.")
                return
            claim = get_user_address()  # get the current user wallet address (public key)
            if claim not in self.controller.config['resources'][str(res_id)]["access_control_list"]:
                messagebox.showerror(title="Error",
                                     message="Please add your public key to acccess\ncontrol list before requesting resource.")
                return
            res_path = res_path.decode()
            res_path_shortened = res_path.replace(DEFAULT_POD_LOCATION, "/")
            url = "http://localhost:" + str(self.controller.port_number_val) + res_path_shortened
            sub_id = self.controller.config['resources'][str(res_id)]['subscription_id']
            pod_id = self.controller.config['id']
            default_obligations = readFileData(DEFAULT_POD_LOCATION +pod_id+'/DTobligations.json')
            resource_data = callAPI(url, res_path_shortened, sub_id, claim)
            print(resource_data)
            self.toplevel_window1 = None
            if resource_data:
                if self.toplevel_window1 is None or not self.toplevel_window1.winfo_exists():
                    self.toplevel_window1 = DisplayResource(self.controller, data={'res_id':str(res_id),"image_path":resource_data,"obligations":self.controller.config['resources'][str(res_id)]['obligations'],"default":default_obligations['default']})
                else:
                    self.toplevel_window1.focus()  
            else:
                message = "IP Geolocation Failed! Check your internet connection." if resource_data is None else  resource_data.reason
                messagebox.showerror(title="Error", message=message)

    def create_tabs(self, tab__name=None):
        self.controller.config = readFileData(DEFAULT_POD_LOCATION +self.controller.selected_pod_id+ "/DTconfig.json")
        if hasattr(self.controller, 'tabview'):
            self.controller.tabview.pack_forget()
            del self.controller.tabview

        self.controller.tabview = CTkTabview(self.controller.main_view,segmented_button_fg_color='#4a4a4a',segmented_button_unselected_color='#4a4a4a')
        self.controller.tabview.pack(padx=2, pady=(0,5),fill='both',expand=True)
        title = "Resources of Pod " + str(self.controller.selected_pod_id+'\t')
        self.controller.page_title.configure(text=title)

        disable_icon = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/disable.png")))
        disable_img = CTkImage(dark_image=disable_icon, light_image=disable_icon, size=(25, 25))
        monitoring_icon = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/research.png")))
        monitoring_img = CTkImage(dark_image=monitoring_icon, light_image=monitoring_icon, size=(25, 25))
        logs_icon = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/log.png")))
        logs_img = CTkImage(dark_image=logs_icon, light_image=logs_icon, size=(25, 25))
        api_call_icon = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/file.png")))
        api_call_img = CTkImage(dark_image=api_call_icon, light_image=api_call_icon, size=(25, 25))

        self.controller.resources = get_resource_by_pod(self.controller.selected_pod_id, 0)
        if self.controller.resources:
            self.table_label_frames = {}
            for resource in self.controller.resources:
                res_id = str(resource[0])
                self.controller.tabview.configure(fg_color=DARK_BLUE,border_color=LIGHT_BLUE,border_width=1)
                tab_name = "Res " + res_id
                self.controller.tabview.add(tab_name)
                tab = self.controller.tabview.tab(tab_name)
                tab.configure(fg_color='transparent')
                main_frame = CTkFrame(tab, fg_color=LIGHT_BLUE,corner_radius=12)
                main_frame.pack(anchor='center', padx=10, fill='x')

                status = "Active" if resource[4] else "Inactive"
                tab_frame = CTkFrame(main_frame, corner_radius=20, width=600, fg_color='transparent')
                tab_frame.pack(side='left',padx=10,pady=5)
                resource_url_path_full = resource[2].decode("utf-8")
                resource_url_path_short = resource_url_path_full if len(resource_url_path_full) <50 else resource_url_path_full[0:45]+"..."


                self.create_label_pair(tab_frame, 'Id : ', resource[0])
                self.create_label_pair(tab_frame, 'Address : ', resource[1])
                self.create_label_pair(tab_frame, 'Url : ', resource_url_path_short,True,resource_url_path_full)
                self.create_label_pair(tab_frame, 'Pod Id : ', resource[3])
                self.create_label_pair(tab_frame, 'Status : ', status)

                buttons_frame = CTkFrame(main_frame, corner_radius=20, width=200, fg_color='transparent')
                buttons_frame.pack(side='left', padx=10,expand='True')


                btn_1=CTkButton(master=buttons_frame,image=logs_img, text="View Logs",compound='left', height=30,
                          command=lambda res=resource[0]: self.controller.show_frame(LogsPage, {"pod_id":self.controller.selected_pod_id, "res_id":res,"page":'ResourcePage'}),
                          fg_color="transparent", border_color="#fff", hover_color=DARK_BLUE,
                          border_width=2)
                          
                btn_2=CTkButton(master=buttons_frame, image=disable_img, text="De-activate",compound='left', height=30,
                          command=lambda res_id=str(resource[0]), tab_name=tab_name: self.deactivate(res_id, tab_name),
                          fg_color="transparent", border_color="#E76F51", hover_color=DARK_BLUE,
                          border_width=2)
                
                btn_3=CTkButton(master=buttons_frame,image=monitoring_img,  text="Start Monitoring",compound='left', height=30,
                          command=lambda res=resource[0]: self.start_monitoring(res),
                          fg_color="transparent", border_color="#fff", hover_color=DARK_BLUE,
                          border_width=2)

                btn_4=CTkButton(master=buttons_frame,image=api_call_img, text="Get Resource",compound='left', height=35,
                          command=lambda res_id=resource[0],res_path=resource[2]: self.request_resource_api(res_path,res_id),
                          fg_color="transparent", border_color="#fff", hover_color=DARK_BLUE,
                          border_width=2)

                btn_3.pack(padx=3, pady=3) #monioring routine
                btn_1.pack(padx=3, pady=3) #logs
                btn_4.pack(padx=3, pady=3) #get resource
                btn_2.pack(padx=3, pady=3) #deactivate


                tooltip_1 = CTkToolTip(btn_1, delay=0.5, bg_color=LIGHT_GREEN,border_color='white',border_width=1,text_color='white',padding=(5,5) ,message="View the resource\nusage logs.")
                tooltip_2 = CTkToolTip(btn_2, delay=0.5, bg_color="#B23117",padding=(5,5),border_color='white',border_width=1,text_color='white',message="Deactivating the resource\n makes it inaccessible.")
                tooltip_3 = CTkToolTip(btn_3, delay=0.5, bg_color=LIGHT_GREEN,border_color='white',border_width=1,text_color='white',padding=(5,5) ,message="Monitor the resource usaage")
                tooltip_4 = CTkToolTip(btn_4, delay=0.5, bg_color=LIGHT_GREEN,border_color='white',border_width=1,text_color='white',padding=(5,5) ,message="Get Resource by Api")
 
                obligations_frame = CTkFrame(master=tab, corner_radius=12,height=200, fg_color=LIGHT_BLUE)
                obligations_frame.pack(anchor="w", padx=10, pady=10, fill='both')

                CTkLabel(obligations_frame, text='Resource Obligations',text_color="white", font=("Arial Bold", 14)).pack(anchor='center')
                frames = CTkFrame(master=obligations_frame, fg_color='transparent')
                frames.pack(fill='x', anchor='center',padx=2,pady=5)

                resource_data = self.controller.config['resources'][res_id]
                default_pod_obligations= readFileData(self.controller.pod_location+"/DTobligations.json")
                access_counter = get_obligations(default_pod_obligations,resource_data,"access_counter")
                temporal_obligation = get_obligations(default_pod_obligations,resource_data,"temporal")
                domain_obligation =  get_obligations(default_pod_obligations,resource_data,"domain")
                country_obligation =  get_obligations(default_pod_obligations,resource_data,"country")
                def_access_counter = access_counter['value']
                def_temporal_obligation = temporal_obligation['value']
                def_domain_obligation = domain_obligation['value']
                def_country_obligation = country_obligation['value'] if len(country_obligation['value']) <14 else country_obligation['value'][0:11]+"..."

                text_color= DARK_GREEN if access_counter['pod_default_value'] else 'white'
                frame1 = CTkFrame(master=frames,height=100,width=140,fg_color=DARK_BLUE,corner_radius=10)
                f1= CTkFrame(frame1,fg_color=DARK_BLUE,corner_radius=20,width=140)
                CTkLabel(f1, text="Access Counter", font=('Arial', 14),text_color='white').pack(side='left', padx=5)
                help_icon1=CTkLabel(f1, text="", image=help_icon_img, width=15, height=15,)
                help_icon1.pack(side='left')
                f1.pack(pady=2, padx=5)
                access_counter_val = CTkLabel(frame1,text=def_access_counter,font=('Arial Bold',16),text_color=text_color)
                access_counter_val.pack(anchor='center')
                CTkButton(frame1,text="Edit",width=60,fg_color=DARK_BLUE,border_width=1,border_color='white',command=lambda res_id=resource[0]: self.open_edit_popup(res_id,'access_counter')).pack(anchor='center',pady=10)
                help_tooltip1 = CTkToolTip(help_icon1, delay=0.5,padding=(5,5),text_color='black',bg_color=LIGHT_YELLOW,message=help_tooltips[0],border_color='white',border_width=1)
                frame1.pack(side='left',padx=(4,2),pady=5,fill='both',expand=True)

                text_color= DARK_GREEN if temporal_obligation['pod_default_value'] else 'white'
                frame2 = CTkFrame(master=frames,height=100,width=140,fg_color=DARK_BLUE,corner_radius=10)
                f2= CTkFrame(frame2,fg_color=DARK_BLUE,corner_radius=20,width=140)
                CTkLabel(f2, text="Temporal Obligation", font=('Arial', 14),text_color='white').pack(side='left', padx=5)
                help_icon2=CTkLabel(f2, text="", image=help_icon_img, width=15, height=15,)
                help_icon2.pack(side='left')
                f2.pack(pady=2, padx=5)
                temporal_obligation_val = CTkLabel(frame2,text=def_temporal_obligation,font=('Arial Bold',16),text_color=text_color)
                temporal_obligation_val.pack(anchor='center')
                CTkButton(frame2,text="Edit",width=60,fg_color=DARK_BLUE,border_width=1,border_color='white',command=lambda res_id=resource[0]: self.open_edit_popup(res_id,'temporal')).pack(anchor='center',pady=10)
                help_tooltip2 = CTkToolTip(help_icon2, delay=0.5,padding=(5,5),text_color='black',bg_color=LIGHT_YELLOW,message=help_tooltips[1],border_color='white',border_width=1)
                frame2.pack(side='left',padx=2,pady=5,fill='both',expand=True)

                text_color= DARK_GREEN if domain_obligation['pod_default_value'] else 'white'
                frame3 = CTkFrame(master=frames,height=100,width=140,fg_color=DARK_BLUE,corner_radius=10)
                f3= CTkFrame(frame3,fg_color=DARK_BLUE,corner_radius=20,width=140)
                CTkLabel(f3, text="Domain Obligation", font=('Arial', 14),text_color='white').pack(side='left', padx=5)
                help_icon3=CTkLabel(f3, text="", image=help_icon_img, width=15, height=15,)
                help_icon3.pack(side='left')
                f3.pack(pady=2, padx=5)
                domain_obligation_val = CTkLabel(frame3,text=def_domain_obligation,font=('Arial Bold',16),text_color=text_color)
                domain_obligation_val.pack(anchor='center')
                CTkButton(frame3,text="Edit",width=60,fg_color=DARK_BLUE,border_width=1,border_color='white',command=lambda res_id=resource[0]: self.open_edit_popup(res_id,'domain')).pack(anchor='center',pady=10)
                help_tooltip3 = CTkToolTip(help_icon3, delay=0.5,padding=(5,5),text_color='black',bg_color=LIGHT_YELLOW,message=help_tooltips[2],border_color='white',border_width=1)
                frame3.pack(side='left',padx=2,pady=5,fill='both',expand=True)

                text_color= DARK_GREEN if country_obligation['pod_default_value'] else 'white'
                frame4 = CTkFrame(master=frames,height=100,width=140,fg_color=DARK_BLUE,corner_radius=10)
                f4= CTkFrame(frame4,fg_color=DARK_BLUE,corner_radius=20,width=140)
                CTkLabel(f4, text="Country Obligation", font=('Arial', 14),text_color='white').pack(side='left', padx=5)
                help_icon4=CTkLabel(f4, text="", image=help_icon_img, width=15, height=15,)
                help_icon4.pack(side='left')
                f4.pack(pady=2, padx=5)
                country_obligation_val = CTkLabel(frame4,text=def_country_obligation,font=('Arial Bold',16),text_color=text_color)
                country_obligation_val.pack(anchor='center')
                CTkButton(frame4,text="Edit",width=60,fg_color=DARK_BLUE,border_width=1,border_color='white',command=lambda res_id=resource[0],val=NO_OBLIGATION if country_obligation['pod_default_value'] else country_obligation['value']: self.open_edit_popup(res_id,'country',val)).pack(anchor='center',pady=10)
                frame4.pack(side='left',padx=(2,4),pady=5,fill='both',expand=True)
                help_tooltip4 = CTkToolTip(help_icon4, delay=0.5,padding=(5,5),text_color='black',bg_color=LIGHT_YELLOW,message=help_tooltips[3],border_color='white',border_width=1)
                tooltip_5 = CTkToolTip(country_obligation_val, delay=0.5, message=country_obligation['value'],text_color='white',bg_color=LIGHT_BLUE,border_color='white',border_width=1)
                
                if access_counter['pod_default_value'] or temporal_obligation['pod_default_value'] or domain_obligation['pod_default_value']  or country_obligation['pod_default_value'] :
                    info_frame =  CTkFrame(obligations_frame, corner_radius=20,fg_color='transparent')
                    info_frame.pack(padx=10, side='bottom', fill='x',pady=(0,2))
                    CTkLabel(info_frame,image=info_icon_img,compound='left',text="  Green values indicates that they are inherited from pod",text_color='white').pack(side='right', padx=5)

                input_frame = CTkFrame(tab, fg_color='transparent')
                acl_label = CTkLabel(input_frame, text="Access Control List", font=("Arial Bold", 14),text_color='white')
                acl_label.pack(side='left', padx=5)
                help_icon1=CTkLabel(input_frame, text="", image=help_icon_img, width=15, height=15,)
                help_icon1.pack(side='left', padx=5)
                acl_tooltip = CTkToolTip(help_icon1, delay=0.5,padding=(5,5),text_color="black",bg_color=LIGHT_YELLOW,border_color='white',border_width=1,message='Whitelist the public key\nto access resource api')

                new_key = StringVar(value="")
                access_control_input = CTkEntry(input_frame, width=324, textvariable=new_key, border_width=1)
                access_control_input.pack(side="left", anchor='w', padx=(5, 10), pady=5)
                add_icon = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/add.png")))
                add_icon_img = CTkImage(dark_image=add_icon, light_image=add_icon, size=(20, 20))
                paste_icon = Image.open(os.path.abspath(os.path.join(DIR_PATH, "../../node/assets/paste.png")))
                paste_img = CTkImage(dark_image=paste_icon, light_image=paste_icon, size=(20,20))

                paste_btn = CTkButton(master=input_frame, image=paste_img, text="", width=20, height=20,
                  command=lambda input=access_control_input:self.paste_from_clipboard(input),
                  fg_color="transparent",hover_color="#eee")
                paste_btn.pack(side="left", anchor='w', pady=3)
                paste_tooltip = CTkToolTip(paste_btn, delay=0.5,padding=(5,5),text_color="White",bg_color=LIGHT_GREEN,border_color='white',border_width=1,message='Paste copied key\nfrom clipboard')


                add_btn = CTkButton(input_frame,image=add_icon_img, text="", width=20, height=20,fg_color="transparent",hover_color='#eee',command=lambda res_id=res_id, new_key=access_control_input: self.add_pub_key(res_id, new_key,tab))
                add_btn.pack(side="left", anchor='w',pady=3)
                add_icon_tooltip = CTkToolTip(add_btn, delay=0.5,padding=(5,5),text_color="White",bg_color=LIGHT_GREEN,border_color='white',border_width=1,message='Add key to \nAccess control list')

                input_frame.pack(anchor='center')
                self.table_label_frames[res_id] = CTkScrollableFrame(tab, height=150,width=550,corner_radius=10,fg_color= LIGHT_BLUE)
                self.display_access_control_list(tab, res_id)
            if tab__name:
                self.controller.tabview.set(tab__name)
        else:
            self.controller.tabview.add("No Resource")
            tab = self.controller.tabview.tab("No Resource")
            main_frame = CTkFrame(tab)
            main_frame.pack(anchor='center', padx=10, fill='both')
            CTkLabel(main_frame, text="No Resource Found", text_color='#fff').pack(anchor='center')

    def update_config(self):
        pod_id = self.controller.pod_id.cget("text")
        updateFileData(self.controller.config, DEFAULT_POD_LOCATION + pod_id + "/DTconfig.json")

    def add_pub_key(self, res_id, key, tab):
        new_key = key.get()
        if len(new_key) != 42 or not (re.findall(pattern='0x[a-fA-F0-9]{40}$', string=new_key)):
            print("INVALID KEY")
            messagebox.showerror(title="Error", message="Invalid Public Key !")
            return

        if new_key not in self.controller.config['resources'][res_id]["access_control_list"]:
            self.controller.config['resources'][res_id]["access_control_list"].append(new_key)
            key.delete(0, END)
            self.update_config()
            self.display_access_control_list(tab, res_id)
        else:
            messagebox.showerror(title="Error", message="Public key already whitelisted !")
            return

    def remove_pub_key(self, data, res_id, pub_key, tab):
        data.remove(pub_key)
        print(data)
        self.controller.config['resources'][res_id]["access_control_list"] = data
        self.update_config()
        self.display_access_control_list(tab, res_id)

    def display_access_control_list(self, tab, res_id):

        table_label_frame2 = self.table_label_frames[res_id]
        for widgets in table_label_frame2.winfo_children():
            widgets.destroy()

        labels = []
        delete_btns = []
        data = self.controller.config['resources'][res_id]["access_control_list"] if hasattr(self.controller,'config') else []
        for index in range(len(data)):
            key = data[index]
            frame = CTkFrame(master=table_label_frame2, fg_color='transparent')
            frame.pack(anchor='center')
            labels.append(CTkLabel(frame, text=str(key),text_color='white'))
            delete_btns.append(CTkButton(frame, text="Delete", width=25, height=25, corner_radius=5,
                                         command=lambda idx=index: self.remove_pub_key(data, res_id, data[idx], tab),
                                         font=("Arial", 13), border_color="#E76F51", hover_color="#E76F51", border_width=1,
                                         fg_color='transparent', text_color="#eee"))

            labels[index].grid(row=index,column = 0, padx =10, pady=3)
            delete_btns[index].grid(row=index,column = 1, padx =10,pady=3)

        table_label_frame2.pack(anchor="center", padx=20,fill='y',expand=True)

    def create_label_pair(self, tab, label_text, value_text, addTooltip=False,message = None):
        label_frame = CTkFrame(tab, fg_color="transparent")
        label = CTkLabel(label_frame, text=label_text,text_color=LIGHT_GREEN, font=("Arial Bold", 15))
        label.pack(side="left", anchor="w")
        value = CTkLabel(label_frame, text=value_text,text_color='white')
        value.pack(side="left", anchor="w")
        if(message and len(message)>=50):
            message = '\n'.join([message[i:i+30] for i in range(0, len(message), 30)])
            tooltip = CTkToolTip(value, delay=0.2,padding=(5,5),text_color="White" ,bg_color=DARK_BLUE,border_color='white',border_width=1,message=message)
        label_frame.pack(fill="x", padx=10, pady=0, anchor="w")

    def __init__(self, parent, controller):
        super().__init__( parent)
        self.controller = controller
        self.controller.create_sidebar(self,controller,'ViewResourcePage')


        ###### MOCKUP ############
        self.controller.monitoringThread = Thread(None, DTmonitoringMockup().listen_monitoring)  # MOCKUP
        self.controller.monitoringThread.start()  # MOCKUP
        ###########################

        self.controller.main_view = CTkFrame(self, width=690, height=650, corner_radius=0, fg_color=DARK_BLUE)
        self.controller.main_view.pack_propagate(0)
        self.controller.main_view.pack(side="left", fill='both',expand=True)

        title_frame=CTkFrame(self.controller.main_view, fg_color='transparent')
        title_frame.pack(padx=10,pady=20,fill='x')
        CTkButton(title_frame,text='Back',command=self.exit_page,border_color="#FFF", hover_color="#E76F51",fg_color='transparent',
                      border_width=1, text_color="#FFF",width=60).pack(side='left',padx=10)
        self.controller.page_title = CTkLabel(title_frame, text='', font=("Arial Bold", 25),text_color=DARK_GREEN)
        self.controller.page_title.pack(anchor='center')

class RegisterResourcePage(CTkFrame):

    def __init__(self, parent, controller):

        def clear_and_exit():
            for widget in [self.controller.pod_id_input, self.controller.url_input_entry, self.controller.sub_id_input]:
                widget.delete(0, END)
                widget.insert(0, "")
            for label in [self.sub_error_msg,self.loc_error_msg]:
                label.set("")

            self.controller.invoke_button(self.controller,self.controller.selected_pod_id,'PodManagementPage')
            controller.show_frame(PodManagementPage)

        def browse_button():
            url = filedialog.askopenfilename()
            self.controller.url_input_entry.delete(0, END)
            self.controller.url_input_entry.insert(0, url)

        def check_if_resource_exist(url):
            for res in self.controller.config['resources']:
                if url  == self.controller.config['resources'][res]['url']:
                    return True
            return False
            
        
        def validate(url,sub_id):
            flag = 0
            file_name = url.split('/')[-1]
            if(check_if_resource_exist(url)):
                messagebox.showerror(title='Error',message="This resource already exists in this Pod.\nSelect another resource or duplicate the\nresource file with different name.")
                return
            # if sub_id == "":
            #     self.sub_error_msg.set("Subscription Id cannot be empty")
            #     flag+=1
            if sub_id != "" and not re.findall(pattern='^\d*$', string= sub_id):
                self.sub_error_msg.set("Subscription Id should be\nnumerical and non-negative")
                flag+=1
            if url == "":
                self.loc_error_msg.set("Resource Path cannot be empty")
                flag+=1
            elif not (DEFAULT_POD_LOCATION in url):
                self.loc_error_msg.set("Resource must be inside the parent pod")
                flag+=1
            elif not re.findall(pattern="^[a-zA-Z0-9_.-]+$", string=file_name):
                self.loc_error_msg.set("Resource name should only contain alphanumeric characters,\nhyphen( - ), underscore( _ ) and period( . )")
                flag+=1
            else:
                file_exist=os.path.exists(url)
                if not file_exist:
                    self.loc_error_msg.set("Resource file does not exist.")
                    flag+=1
            return flag == 0

        def submit():
            self.sub_error_msg.set("")
            self.loc_error_msg.set("")

            pod_id = self.controller.pod_id_input.get()
            url = url_input.get()
            sub_id = self.controller.sub_id_input.get()
            print(pod_id, url, sub_id)

            if(validate(url,sub_id)):           
                directory_arr = url.split("/")
                sub_id = self.controller.sub_id_input.get()
                sub_id = sub_id if sub_id != '' else "0"
                
                if not ( DEFAULT_POD_LOCATION+pod_id+'/images/' in url):
                    print("Wrong Pod")
                    messagebox.showerror(title="Error", message="Selected resource does not belong to Pod " + pod_id+"\nResources must be inside a folder called images")
                elif (directory_arr[-3] == pod_id):
                    resource = register_resource(DEFAULT_POD_LOCATION, pod_id, url, sub_id,self.controller.whitelisted_pub_keys)
                    if(resource['id'] is not None):
                        self.controller.invoke_button(self.controller,pod_id,'RegisterResourcePage')
                        messagebox.showinfo(title="Resource Creation", message=resource['message'])
                        self.controller.config = readFileData(DEFAULT_POD_LOCATION+pod_id + "/DTconfig.json")
                    else:
                        messagebox.showerror(title="Resource Creation", message=resource['message'])
                    for widget in [self.controller.url_input_entry, self.controller.sub_id_input]:
                        widget.delete(0, END)
                        widget.insert(0, "")
                else:
                    print("Wrong Pod")
                    messagebox.showerror(title="Error", message="Selected resource does not belong to Pod " + pod_id+"\nResources must be inside a folder called images")

        super().__init__(parent)
        self.controller = controller
        self.controller.create_sidebar(self,controller,'RegisterResourcePage')


        main_view = CTkFrame(self, width=690, height=650, corner_radius=0, fg_color=DARK_BLUE)
        main_view.pack_propagate(0)
        main_view.pack(side="left", fill='both',expand=True)

        title_frame = CTkFrame(main_view, fg_color='transparent')
        title_frame.pack(padx=10,pady=20,fill='x')
        CTkButton(title_frame, text='Back', command=lambda: clear_and_exit() ,border_color="#FFF", hover_color="#E76F51", fg_color='transparent',border_width=1, text_color="#FFF", width=60).pack(side='left', padx=(10, 20))
        CTkLabel(master=title_frame, text="Register New Resource\t", font=("Arial Bold", 25), text_color=DARK_GREEN).pack(anchor="center")


        new_resource_frame = CTkFrame(master=main_view, corner_radius=10,fg_color=LIGHT_BLUE)
        new_resource_frame.pack(padx=20, pady=10)

        # Create a frame for the input labels and entries
        input_frame = CTkFrame(master=new_resource_frame,fg_color='transparent')
        input_frame.pack(padx=30,pady=10)

        CTkLabel(master=input_frame, text="Pod Id", font=("Arial Bold", 14), text_color="#fff",).grid(row=0, column=0,sticky="w",pady=5)
        help_icon1=CTkLabel(input_frame, text="", image=help_icon_img, width=15, height=15,)
        help_icon1.grid(row=0,column=0,sticky="e",padx=(0,200),pady=0)
        self.controller.pod_id_input = CTkEntry(master=input_frame, width=260, border_width=1)
        self.controller.pod_id_input.grid(row=1, column=0,padx=5)

        CTkLabel(master=input_frame, text="Subscription Id (optional)", font=("Arial Bold", 14), text_color="#fff").grid(row=0,column=1,sticky="w",padx=5,pady=5)
        help_icon2=CTkLabel(input_frame, text="", image=help_icon_img, width=15, height=15,)
        help_icon2.grid(row=0,column=1,sticky="e",padx=(0,80),pady=0)
        self.controller.sub_id_input = CTkEntry(master=input_frame, width=260, border_width=1)
        self.controller.sub_id_input.grid(row=1, column=1, padx=10)
        self.sub_error_msg = StringVar(value='')
        error_msg_label1 = CTkLabel(input_frame,textvariable=self.sub_error_msg, font=('Arial',12), text_color='#FF4847',fg_color="transparent")
        error_msg_label1.grid(row=2, column=1, padx=20,sticky='sw',pady=1)


        res_path_frame = CTkFrame(new_resource_frame, fg_color="transparent")
        res_path_frame.pack(fill='x',padx=27)
        CTkLabel(res_path_frame, text="Resource Path", font=("Arial Bold", 14), text_color="#fff").pack(side = 'left')
        help_icon3=CTkLabel(res_path_frame, text="", image=help_icon_img, width=15, height=15,)
        help_icon3.pack(side='left',padx = 10)

        location_container = CTkFrame(new_resource_frame, fg_color="transparent")
        location_container.pack(anchor="w", pady=(10, 0), padx=(27, 0))
        self.loc_error_msg = StringVar(value='')
        error_msg_label2 = CTkLabel(location_container,textvariable=self.loc_error_msg, font=('Arial',12), text_color='#FF4847')
        error_msg_label2.pack(side="bottom",anchor='w',padx=10)

        url_input = StringVar(value="")
        self.controller.url_input_entry = CTkEntry(location_container, width=415, textvariable=url_input, border_width=1)
        self.controller.url_input_entry.pack(side="left",padx=(5,0))

        help_tooltip1 = CTkToolTip(help_icon1, delay=0.5,padding=(5,3),text_color='black',bg_color=LIGHT_YELLOW,border_color='white',border_width=1,font=("Arial", 12),message='ID of the parent pod\nThis field is uneditable')
        help_tooltip2 = CTkToolTip(help_icon2, delay=0.5,padding=(5,3),text_color='black',bg_color=LIGHT_YELLOW,border_color='white',border_width=1,font=("Arial", 12),message="Enter a non-negative numerical\nvalue as a subscription ID")
        help_tooltip3 = CTkToolTip(help_icon3, delay=0.5,padding=(5,3),text_color='black',bg_color=LIGHT_YELLOW,border_color='white',border_width=1,font=("Arial", 12),message="Choose a resource file\nfrom the parent pod")
        
        CTkButton(master=location_container, text="Browse", width=110, fg_color=LIGHT_BLUE, border_width=1, border_color='white',hover_color=DARK_BLUE, command=browse_button).pack(side="left", padx=(10, 0))
        CTkButton(master=new_resource_frame, text="Create", width=300, command=submit, font=("Arial Bold", 17),
                  hover_color=LIGHT_GREEN,height=10,border_color='white',border_width=1,fg_color=LIGHT_BLUE, text_color="#fff").pack( anchor="center", pady=(30, 10), padx=(0, 27))


    def load_data(self, id):
        self.controller.pod_id_input.configure(state='normal')
        self.controller.pod_id_input.delete(0, tk.END)
        self.controller.pod_id_input.insert(0, int(id))
        self.controller.pod_id_input.configure(state='disabled')
        for widget in [self.controller.url_input_entry, self.controller.sub_id_input]:
            widget.delete(0, END)
            widget.insert(0, "")
        self.controller.invoke_button(self.controller,id,'RegisterResourcePage')
              
class LogWindow(CTkToplevel):

    def create_label_pair(self,label_text, value_text, row, frame):
        label_frame = CTkFrame(frame, fg_color="transparent")
        CTkLabel(label_frame, text=label_text, font=("Arial Bold", 15)).grid(row=row, column=0)
        value_label = CTkLabel(label_frame, text=value_text,text_color='white')
        value_label.grid(row=row, column=1)
        label_frame.pack(fill="x", padx=10, pady=0, anchor="w")
        return value_label

    def __init__(self, *args, logs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x410")
        self.title("Resource Logs")
        self.configure(fg_color=DARK_BLUE)
        logs_frame = CTkFrame(self, corner_radius=10, fg_color=LIGHT_BLUE)
        self.create_label_pair("Id : ",logs["monitoring_id"],0,logs_frame)
        self.create_label_pair("Timestamp : ",logs["timestamp"],1,logs_frame)
        self.create_label_pair("Resource Id : ",logs["resource_monitored"],2,logs_frame)
        self.create_label_pair("Request status : ",logs["request_status"],3,logs_frame)
        self.create_label_pair("Consumer address : ",logs["consumer_address"],4,logs_frame)
        self.create_label_pair("Outcome : ",logs["outcome"],5,logs_frame)
        logs_container = CTkFrame(master=logs_frame, fg_color="transparent")
        logs_container.pack(fill="x", padx=10, pady=10, anchor="w")
        CTkLabel(logs_container, text="Logs : ", font=("Arial Bold", 15)).grid(row=6, column=0)
        logs_box = CTkTextbox(master=logs_container, width=450, corner_radius=10)
        logs_box.insert("0.0",logs['log_file'])
        logs_box.grid(row=6, column=1, padx=20)
        logs_frame.pack(anchor='center', fill='both', padx=10,pady=10)

class LogsPage(CTkFrame):

    def load_data(self, data):
        set_appearance_mode('Light')
        self.go_back_to = data['page']
        self.display_log_table(data)
        self.controller.invoke_button(self.controller,self.controller.selected_pod_id,'LogsPage')


    def exit_page(self):
        for widgets in self.logs_table.winfo_children():
            widgets.destroy()
        set_appearance_mode('Dark')
        if self.go_back_to == "ResourcePage":
            self.controller.show_frame(ViewResourcePage)
        elif self.go_back_to == "PodPage":
            self.controller.show_frame(PodManagementPage)

    def on_row_select(self,dt):
        selected_row_id = dt.view.selection()[0]
        selected_row_values = dt.iidmap.get(selected_row_id)
        print(selected_row_values.values)
        if(selected_row_values.values[4] =='  No Logs Found  '):
            messagebox.showerror(title="Error", message="No logs to examine.\nPlease start monitoring\nprocedure to create new logs.")
            return
        logs = (x for x in self.controller.table_data['logs'] if x["monitoring_id"] == selected_row_values.values[0])
        logs = next(logs)

        self.toplevel_window = LogWindow(self.controller, logs=logs)
        # if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
        #     self.toplevel_window = LogWindow(self.controller, logs=logs)
        # else:
        #     self.toplevel_window.focus()  # if window exists focus it

    def display_log_table(self, data):
        coldata = [
            {"text": "Id", "width": 30,"stretch": False},
            {"text": "Timestamp", "width": 90,"stretch": False},
            {"text": "Resource Id", "width": 90,"stretch": False},
            {"text": "Request status", "width": 90, "stretch": True},
            {"text": "Consumer address", "width": 300, "stretch": True},
            {"text": "Outcome", "width": 100},
            {"text": "logs",'width':1,"stretch": False}
        ]
        self.controller.table_data = readFileData(DEFAULT_POD_LOCATION  + "logs.json")
        rowdata = []
        if self.controller.table_data is None:
            rowdata.append(("","","","","  No Logs Found  ",""))
        elif data['page'] == 'ResourcePage':
                self.controller.table_data['logs'] = [log for log in self.controller.table_data['logs'] if log['resource_monitored'] == data['res_id']]
                if not self.controller.table_data['logs']:
                    rowdata.append(("", "", "", "", "  No Logs Found  ", "", ""))
                else:
                    for log in self.controller.table_data['logs']:
                        rowdata.append((log["monitoring_id"], log["timestamp"], log["resource_monitored"], log["request_status"], log["consumer_address"],log["outcome"],log['log_file']))
        else:
            self.controller.table_data['logs'] = [log for log in self.controller.table_data['logs'] if str(log['resource_monitored']) in self.controller.config['resources'].keys()]
            if not self.controller.table_data['logs']:
                    rowdata.append(("", "", "", "", "  No Logs Found  ", "", ""))
            else:
                for log in self.controller.table_data['logs']:
                    rowdata.append((log["monitoring_id"], log["timestamp"], log["resource_monitored"],log["request_status"], log["consumer_address"], log["outcome"],log['log_file']))

        self.controller.logs_table = Tableview(
            master=self.logs_table,
            coldata=coldata,
            rowdata=rowdata,
            paginated=True,
            searchable=True,
            bootstyle="dark",
            # autofit=True,
            # stripecolor=('#9bf7b5', None),
        )
        self.controller.logs_table.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        self.toplevel_window = None
        CTkButton(master=self.logs_table,text="Examine Selected Log",fg_color=DARK_BLUE,hover_color=LIGHT_GREEN,border_color='#eee',border_width=1, command=lambda: self.on_row_select(self.controller.logs_table)).pack(pady=5)
        set_appearance_mode('Dark')

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.create_sidebar(self,controller,'LogsPage')

        self.main_view = CTkFrame(self, width=700, height=650, corner_radius=0, fg_color=DARK_BLUE)
        self.main_view.pack_propagate(0)
        self.main_view.pack(side="left", fill='both',expand=True)

        title_frame = CTkFrame(self.main_view, fg_color='transparent')
        title_frame.pack(padx=10,pady=20,fill='x')
        CTkButton(title_frame, text='Back', command=self.exit_page,border_color="#FFF", hover_color="#E76F51", fg_color='transparent',border_width=1, text_color="#FFF", width=60).pack(side='left', padx=10)
        label = CTkLabel(title_frame, text="Resource Logs\t", font=("Arial Bold", 25), text_color=DARK_GREEN)
        label.pack(anchor='center')

        self.logs_table = CTkFrame(self.main_view, fg_color="transparent")
        self.logs_table.pack(padx=15, fill='both')


# Driver Code
app = tkinterApp()
app.mainloop()
