"""
simple gui to install Copilot in either existing or new Thonny distribution
"""
import os
import sys
import time
import subprocess


def install_package(package):
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        os.system('sudo pacman -S ' +  package)
    else:
        print("you need to enable", package, "for your version of python")

#handle case when tkinter isn't enabled
try:
    from tkinter import *
    from tkinter import filedialog
    from tkinter.ttk import Progressbar
except ImportError:
    print("installing tkinter..")
    install_package("tk")
    from tkinter import filedialog
    from tkinter import *
    from tkinter.ttk import Progressbar




class InstallGUI:
    def __init__(self, master):
        self.master = master
        master.geometry('600x400')
        master.title("Co-Pilot Instalation Wizard")

        # some systems python3 commandline variable is stored as python
        self.python_cmd = 'python3' 

        self.pip_cmd = 'pip'

        #start up first page
        self.render_first_page()

        #set where file is downloaded
        self.target_dir = ''
        self.install_method = 'TBD'
        
        #render back button
        self.back_button = Button(master, text="Back", command=self.prev_page, font= "Helvetica", state="disabled")
        self.back_button.pack()
        self.back_button.place(relx= .34, rely= .95, anchor=CENTER)

        #render continue button
        self.continue_button = Button(self.master, text="Next", command=self.next_page, font= "Helvetica")
        self.continue_button.pack()
        self.continue_button.place(relx= .46, rely= .95, anchor=CENTER)

        #render back button
        self.cancel_button = Button(self.master, text="Cancel", command=master.quit, font= "Helvetica")
        self.cancel_button.pack()
        self.cancel_button.place(relx =.65, rely=.95, anchor=CENTER)

        #to manage page state
        self.page_state = 0

    #to destroy and create relevant objects
    def render_page(self):

        if self.page_state == 0:
            self.description_label.destroy()
            self.install_choice.destroy()
            self.top_label.destroy()
            self.render_first_page()
            self.target_dir = ''
            self.install_method = 'TBD'
            self.back_button["state"] = DISABLED
            self.continue_button["state"] = NORMAL
            
        elif self.page_state == 1:
            self.top_label.destroy()
            self.requirements.destroy()

            missing_requirments = self.check_requirments()
            if missing_requirments:
               self.description_label.configure(text="Missing packages: " + " ".join(missing_requirments),  fg='red')
            else:
                self.description_label.destroy()
                self.render_second_page()
                self.back_button["state"] = NORMAL

            self.continue_button["state"] = DISABLED

        elif self.page_state == 2:
            self.description_label.destroy()
            self.install_choice.destroy()
            self.top_label.destroy()
            self.back_button["state"] = DISABLED
            self.continue_button["state"] = DISABLED

            self.master.update_idletasks()
            self.start_download = Button(self.master, text="Start Download", command=self.install, font= "Helvetica")
            self.start_download.place(relx= .5, rely = .5, anchor=CENTER)

        elif self.page_state == 3:
            #run thonny
            self.launch_thonny()
            #os.system(self.python_cmd + " -m thonny")
            self.master.quit()

    def launch_thonny(self):
        #navigate to desktop
        desktop = ''
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') 
        else:
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
        os.chdir(desktop)
        
        #set up file path
        path = os.path.join(self.target_dir, self.folder_name) # change name

        #make shortuct
        f= open("thonny-codelive","w+")
        f.close()

        #set up short cut
        shortcut = f=open("thonny-codelive", "a+")
        if sys.platform in ('win32', 'cygwin'):
            shortcut.write('#!/bin/bash')

        #set enviornment variable
        path_to_plugin = os.path.join(path, self.plugin_name)
        cmd =  "PYTHONPATH=" + path_to_plugin
        windows_cmd = "set " + cmd
        linux_cmd = "export " + cmd

        #handle multiple os
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            shortcut.write(linux_cmd + '\n')
        else:
            shortcut.write(windows_cmd + '\n')

        shortcut.write("cd " + path +'\n')
        shortcut.write(self.python_cmd + " -m thonny")
        shortcut.close()
        os.system("cat thonny-codelive")

        # make short cut executable
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            os.system("chmod +x thonny-codelive")
        else:
            os.system("chmod u+x thonny-codelive")

        # launch thonny
        os.chdir(path)
        (self.python_cmd + " -m thonny")

    def render_first_page(self):
         #render top lable
        self.top_label = Label(self.master, text="Welcome To CodeLive\n Install Wizard", font= "Helvetica 24 bold")
        self.top_label.pack()
        self.top_label.place(relx= .5, rely = .2, anchor=CENTER)
        
        #description
        self.description_label = Label(self.master, text="This wizard will install Codelive to your exisiting\n version of thonny or install a new version of thonny.", font="Helvetica 12")
        
        self.description_label.pack()
        self.description_label.place(relx= .5, rely = .5, anchor=CENTER)
        requirements = "\nRequirements:\n - git\n - python3\n - pip" 
        self.requirements = Label(self.master, text=requirements, font="Helvetica 12", justify=LEFT)
        self.requirements.place(relx= .5, rely = .7, anchor=CENTER)

    def render_second_page(self):
        def change_dropdown(*args):
           choice = dropdown_var.get()
           message = "***"
           if  choice != '':
               if choice == "existing version of thonny":
                    try:
                       import thonny
                       self.target_dir = os.path.dirname(thonny.__file__)
                       self.install_method="partial"
                    except ModuleNotFoundError:
                        print("oopsie")
                        self.target_dir = ''
                        message = "thonny is not installed on your device. "
                       
               else:
                   self.target_dir = filedialog.askdirectory(initialdir="/", title="Choose where to save Thonny")
                   self.install_method = "full"
                   message = "bad file location. "
                   
           #prevent user from continuing without choice
           if self.target_dir != () and self.target_dir != '':
               self.continue_button["state"] = NORMAL
               self.top_label.configure(text="Valid Selection", fg="green")
           else:
               self.continue_button["state"] = DISABLED
               self.install_method = "TBD"
               self.top_label.configure(text="Invalid Selection: " + message + "Try again", fg="red")
               dropdown_var.set('')
               
        #set top label
        self.top_label = Label(self.master, text="Select a option:", font="Helvetica 12")
        self.top_label.pack()
        self.top_label.place(relx= .5, rely = .4, anchor=CENTER)

        #set description
        self.description_label = Label(self.master, text="I would like to install CodeLive on a", font="Helvetica 12")
        self.description_label.grid(row=2, column=1, pady=200)

        #dropdown to choose installation method
        #choices= {'existing version of thonny', 'new version thonny'}
        choices= {'new version thonny'}
        dropdown_var = StringVar(self.master)
        dropdown_var.set('')
        dropdown_var.trace("w", change_dropdown)
        self.install_choice = OptionMenu(self.master, dropdown_var, *choices)
        self.install_choice.grid(row=2, column=2)

    #modifying thonny file may require this
    def get_root_access(self):
        try:
            from elevate import elevate
        except ModuleNotFoundError:
            os.system(self.pip_cmd +" install elevate")
            from elevate import elevate
        elevate()

    def check_requirments(self):
        missing_requirments = []
        requirements = ['git', 'pip', 'python3']
        for package in requirements:
            if os.system(package + ' --version') != 0:

                # some systems python3 commandline variable is stored as python
                if package == 'python3':
                    ret = os.popen('python --version').read().find('Python 3')
                    if ret == 0:
                        self.python_cmd = 'python'
                        continue
                if package == 'pip':
                    ret = os.popen('pip3 --version').read().find('pip 21')
                    if ret == 0:
                        self.pip_cmd = 'pip3'
                        continue
                missing_requirments.append(package)

        return missing_requirments

    def install(self):
        self.start_download.destroy()
        self.back_button["state"] = DISABLED
        
        self.master.update_idletasks()

        self.progress = Progressbar(self.master, orient = HORIZONTAL, length= 500, mode='determinate')
        self.progress.place(relx= .5, rely = .5, anchor=CENTER)
        self.progress['value'] = 3
        self.master.update_idletasks()

        self.plugin_name = 'thonny-codelive'
        self.folder_name = 'CodeLiveThonny'

        if self.install_method == "full":
            #clone thonny repo
            path = os.path.join(self.target_dir, self.folder_name)
            os.mkdir(path)
            os.system("git clone https://github.com/thonny/thonny " + path)
            self.progress['value'] = 25
            self.master.update_idletasks()
            
            #install requirements
            os.chdir(path)
            os.system("python3 -m " + self.pip_cmd +" install -r requirements.txt")
            

        path = os.path.join(self.target_dir, self.folder_name, self.plugin_name)
        self.progress['value'] =50
        self.master.update_idletasks()

        #install codelive plugin
        try:
            os.mkdir(path)
        except PermissionError:
            self.get_root_access()
            os.mkdir(path)

        os.system("git clone https://github.com/codelive-project/codelive " + path)
        self.progress['value'] = 75
        self.master.update_idletasks()


        #install requirements
        os.system(self.pip_cmd + " install paho-mqtt")
        os.system(self.pip_cmd + " install pyinstaller")

        self.progress['value'] = 99
        self.master.update_idletasks()

        
        self.back_button.destroy()
        self.cancel_button.destroy()

        #set up for thonny launch
        self.continue_button.configure(text="complete")
        self.continue_button["state"] = NORMAL
        self.continue_button.place(relx=.5, rely=.9)
            
            
        
    def next_page(self):
        self.page_state += 1
        self.render_page()


    def prev_page(self):
        self.page_state -=1
        self.render_page()

root = Tk()
gui = InstallGUI(root)
root.mainloop()
