"""
simple gui to install Codelive in either existing or new Thonny distribution
"""
import os
import sys
import time

def install_package(package):
    if sys.platform == "linux":
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
        master.title("Codelive Instalation Wizard")

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
            self.render_first_page()
            self.target_dir = ''
            self.install_method = 'TBD'
            self.back_button["state"] = DISABLED
            self.continue_button["state"] = NORMAL
        elif self.page_state == 1:
            self.top_label.destroy()
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
            self.install()
        elif self.page_state == 3:
            #run thonny
            path = os.path.dirname(self.target_dir)
            path = os.path.dirname(path)
            path = os.path.dirname(path)
            os.chdir(path)
            os.system("python3 -m thonny")
            self.master.quit()
            
    def render_first_page(self):
         #render top lable
        self.top_label = Label(self.master, text="Welcome To CodeLive\n Install Wizard", font= "Helvetica 24 bold")
        self.top_label.pack()
        self.top_label.place(relx= .5, rely = .2, anchor=CENTER)
        
        #description
        self.description_label = Label(self.master, text="This wizard will install Codelive to your exisiting\n version of thonny or install a new version of thonny.", font="Helvetica 12")
        
        self.description_label.pack()
        self.description_label.place(relx= .5, rely = .5, anchor=CENTER)
        requirements = "\nRequirements:\n \t*git\n \t*python3\n \t*pip" #\\TODO: make label for these

    def render_second_page(self):
        def change_dropdown(*args):
           choice = dropdown_var.get()
           if  choice != '':
               if choice == "existing version of thonny":
                   self.install_method="partial"
                   self.target_dir = filedialog.askdirectory(initialdir="/", title="Choose your Thonny folder")
               else:
                   self.target_dir = filedialog.askdirectory(initialdir="/", title="Choose where to save Thonny")
                   self.install_method = "full"
                   
           #prevent user from continuing without choice
           if self.target_dir != () and self.target_dir != '':
               self.continue_button["state"] = NORMAL
           else:
               self.continue_button["state"] = DISABLED
               self.install_method = "TBD"
               dropdown_var.set('')
               
        #set top label
        self.top_label = Label(self.master, text="Select a option:", font="Helvetica 12")
        self.top_label.pack()
        self.top_label.place(relx= .5, rely = .2, anchor=CENTER)

        #set description
        self.description_label = Label(self.master, text="I would like to install CodeLive on a", font="Helvetica 12")
        self.description_label.grid(row=2, column=1, pady=200)

        #dropdown to choose installation method
        choices= {'existing version of thonny', 'new version thonny'}
        dropdown_var = StringVar(self.master)
        dropdown_var.set('')
        dropdown_var.trace("w", change_dropdown)
        self.install_choice = OptionMenu(self.master, dropdown_var, *choices)
        self.install_choice.grid(row=2, column=2)

       
    def install(self):
        self.progress = Progressbar(self.master, orient = HORIZONTAL, length= 100, mode='determinate')
        self.progress.place(relx= .5, rely = .5, anchor=CENTER)
        self.progress['value'] = 0
        self.master.update_idletasks()

        if self.install_method == "full":
            #clone thonny repo
            path = os.path.join(self.target_dir, "CopilotThonny")
            os.mkdir(path)
            os.system("git clone https://github.com/thonny/thonny " + path)
            self.progress['value'] = 25
            self.master.update_idletasks()
            
            #install requirements
            os.chdir(path)
            os.system("python3 -m pip install -r requirements.txt")
            
            
            #set enviornment variable
            path = os.path.join(path, "thonny")
            cmd =  "PYTHONPATH=" + path
            windows_cmd = "set " + cmd
            linux_cmd = "export " + cmd

            #handle multiple os
            if sys.platform == "linux":
                os.system(linux_cmd)
            else:
                os.system(windows_cmd)

            #navigate to plugins folder
            path = os.path.join(path, "plugins", "codelive")
        else:
            #navigate to plugins folder
            path = os.path.join(self.target_dir,"plugins","codelive")

        self.progress['value'] =50
        self.master.update_idletasks()

        #install codelive plugin
        os.mkdir(path)
        os.system("git clone https://github.com/codelive-project/codelive " + path)
        self.progress['value'] = 75
        self.master.update_idletasks()

        #install requirements
        os.system("pip install paho-mqtt")

        self.progress['value'] = 99
        self.master.update_idletasks()

        
        self.back_button.destroy()
        self.cancel_button.destroy()

        #set up for thonny launch
        self.continue_button.configure(text="complete")
        self.continue_button["state"] = NORMAL
        self.continue_button.place(relx=.5, rely=.9)
        self.target_dir = path
    
            
            
        
    def next_page(self):
        self.page_state += 1
        self.render_page()


    def prev_page(self):
        self.page_state -=1
        self.render_page()

root = Tk()
gui = InstallGUI(root)
root.mainloop()
