import customtkinter as CTK
import subprocess
from tkinter import filedialog
import os
import shutil
from wakepy import keep
from scrapers import amazon,best_buy,magazineluiza, lowes

# Prevents computer from going to sleep
mode = keep.presenting()

class SimpleDialog(CTK.CTk):
    def __init__(self, master=None, title="", message=""):
        super().__init__(master)
        self.title(title)
        self.geometry('300x150')
        
        label = CTK.CTkLabel(self, text=message, font=('Roboto', 14))
        label.pack(pady=20, padx=20)
        
        button = CTK.CTkButton(self, text="OK", command=self.destroy)
        button.pack(pady=10)
        
        self.iconbitmap('statics/error.ico')

class CustomFrame(CTK.CTkFrame):
    def __init__(self, master=None, label_text="", combobox_values=[], **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = CTK.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.combobox = CTK.CTkComboBox(self, values=combobox_values, state='readonly')
        self.combobox.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        self.columnconfigure(1, weight=1)  # Ensure the combobox expands to fill space
        
class CustomEntryFrame(CTK.CTkFrame):
    def __init__(self, master=None, label_text="", **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = CTK.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.entry = CTK.CTkEntry(self)
        self.entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        self.columnconfigure(1, weight=1)  # Ensure the combobox expands to fill space
        
country_list_BB = ['USA']
country_list_Lowes =  ['USA']
country_list_Amazon = ['USA', 'MXC', 'India', 'BR']
country_list_Magazineluiza = ['BR']

def center_window(window, width, height):
    # Obtém as dimensões da tela
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calcula a posição x e y para centralizar a janela
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Define a geometria da janela
    window.geometry(f'{width}x{height}+{x}+{y}')

def show_message():
    dialog = SimpleDialog(title="Error", message="Some Field is Missing")
    center_window(dialog, 300, 150)
    dialog.mainloop()

def on_confirm():
    global selected_retail
    keyword_value = keyword.get()
    need_change_location = check_var.get() == 'on'
    selected_retail = retail.get()
    selected_country = country.get()

    if not keyword_value or not selected_retail or not selected_country:
        show_message()
        return
    
    try:
        if selected_retail == "Best Buy": best_buy.run(keyword_value)            
        elif selected_retail == "Amazon": amazon.run(keyword_value, selected_country, str(need_change_location))
        elif selected_retail == 'Magazineluiza': magazineluiza.run(keyword_value)
        elif selected_retail == "Lowe's": lowes.run(keyword_value)


        # Habilitar o botão de download após a conclusão do subprocesso
        download_button.configure(state='normal')
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the script: {e}")
        show_message()
    

def update_country_list(*args):
    selected_retail = retail.get()
    if selected_retail == 'Best Buy':
        list_CB = country_list_BB
    elif selected_retail == "Lowe's":
        list_CB = country_list_Lowes
    elif selected_retail == 'Amazon':
        list_CB = country_list_Amazon
    elif selected_retail == 'Magazineluiza':
        list_CB = country_list_Magazineluiza
    else:
        list_CB = ['Error']
    country_combobox.configure(values=list_CB)
    if list_CB:
        country_combobox.set(list_CB[0])  # Set default value if available
    update_checkbox_visibility()

#download button
def on_button_click():
    directory = filedialog.askdirectory(title="Choose a folder to Download the CSV")
    if directory:
        save_csv_file(directory)

def save_csv_file(directory: str):
    selected_retail = retail.get().replace(" ", "_")
    source_files = [
        f"outputs/{selected_retail}/product_data.csv",
        f"outputs/{selected_retail}/added_models.csv",
        f"outputs/{selected_retail}/removed_models.csv",
        f"outputs/{selected_retail}/translated_product_data.csv"
    ]
    dest_files = ['product_data.csv', 'added_models.csv', 'removed_models.csv', 'translated_product_data.csv']

    # iters on source file and dest_file
    for source_file, dest_file in zip(source_files, dest_files):
        if os.path.exists(source_file):
            destination_file = os.path.join(directory, dest_file)
            shutil.copy(source_file, destination_file)
            print(f"File saved in: {destination_file}")
        else:
            print(f"File {source_file} doesn't exist.")        

    # clean files after cleaning
    try:
        for file in dest_files:
            try:
                file_path = os.path.join(f'outputs/{selected_retail}', file)  # Adjust paths
                with open(file_path, 'w') as arquivo:
                    pass
            except Exception as e:
                print(f"Error cleaning up {file}: {e}")
    except Exception as e:
        print(f"Not able to clean up: {e}")
        
def update_sas():
    old_file = "statics/sasva.csv"
    new_file = filedialog.askopenfilename(title="Select the file to upload", filetypes=[("Comma Separated", "*.csv")])
    print("file: ", new_file)
    if new_file:
        upload_csv_file(new_file, old_file)  
        
def update_traqline():
    old_file = "statics/traqline.csv"
    new_file = filedialog.askopenfilename(title="Select the file to upload", filetypes=[("Comma Separated", "*.csv")])
    print("file: ", new_file)
    if new_file:
        upload_csv_file(new_file, old_file)      

def update_old_file():
    old_file = "statics/old_file.csv"
    new_file = filedialog.askopenfilename(title="Select the file to upload", filetypes=[("Comma Separated", "*.csv")])
    print("file: ", new_file)
    if new_file:
        upload_csv_file(new_file, old_file)               

def upload_csv_file(new_file:str, old_file:str):
    if not os.path.exists(old_file):
        open(old_file, 'x')
        
    try:
        os.replace(new_file,old_file)
        print("Source path renamed to destination path successfully.")
        # If Source is a file
        # but destination is a directory
    except IsADirectoryError:
        print("Source is a file but destination is a directory.")

    # If source is a directory
    # but destination is a file
    except NotADirectoryError:
        print("Source is a directory but destination is a file.")

    # For permission related errors
    except PermissionError:
        print("Operation not permitted.")

    # For other errors
    except OSError as error:
        print(error)

       
def optionmenu_callback(choice):
    if "SAS VA" in choice: update_sas()
    elif "Traqline" in choice: update_traqline()
    elif "Old File" in choice: update_old_file()
        
def update_checkbox_visibility(*args):
    selected_retail = retail.get()
    selected_country = country.get()
    
    if selected_retail == "Amazon" and selected_country == "USA":
        need_change_location_cb.pack(pady=24, padx=20)
    else:
        need_change_location_cb.pack_forget()
              
with mode:
    CTK.set_appearance_mode('dark')
    CTK.set_default_color_theme('dark-blue')

    # Setup the main window
    root = CTK.CTk()
    width, height = 800, 600
    center_window(root, width, height)

    root.title("Scraper For Retails")
    # Define the icon for the application
    root.iconbitmap('statics/favicon.ico')

    # Options Menu
    optionmenu_var = CTK.StringVar(value="Update Static Files")
    optionmenu = CTK.CTkOptionMenu(root,values=["Upload Old Files for Comparison", "Update SAS VA 5-Star Report", "Update Traqline SKUMetrix"],
                                         command=optionmenu_callback,
                                         variable=optionmenu_var, anchor="center",
                                         )
    optionmenu.pack(anchor='nw', pady=10, padx=20)
    

    # Main frame
    frame = CTK.CTkFrame(root)
    frame.pack(pady=20, padx=60, fill='both', expand=True)
    
    label = CTK.CTkLabel(master=frame, text='Scraper for Retails', font=('Roboto', 30))
    label.pack(pady=24, padx=20)
    
    # Keywords frame and pack the CTkEntry
    keyword = CTK.StringVar(value="")
    keyword_frame = CustomEntryFrame(frame, label_text="Keyword to Scrape")
    keyword_frame.pack(pady=10, padx=20, fill='x')
    keyword_frame.entry.configure(textvariable=keyword)
    
    # Add hint label
    hint_label = CTK.CTkLabel(master=frame, 
                              text="Focus the search on specific sectors, like 'Front Load Washers', 'Dryers', 'Washtowers'.\nA broader search like 'Washers and Dryers' may yield incomplete results.\n\nIMPORTANT: when scraping other regions, use their languages!",
                              font=('Roboto', 10, 'italic', 'bold'))
    hint_label.pack(pady=5, padx=20, fill='x')

    # Retail combobox frame
    retail_frame = CustomFrame(frame, label_text="            Retail            ", combobox_values=['Amazon', 'Best Buy', "Lowe's", 'Magazineluiza'])
    retail_frame.pack(pady=10, padx=20, fill='x')

    retail = CTK.StringVar(value="")
    retail_frame.combobox.configure(variable=retail)
    retail.trace_add('write', update_country_list)

    # Country combobox frame
    country_frame = CustomFrame(frame, label_text=" Country to Scrape ", combobox_values=[''])
    country_frame.pack(pady=10, padx=20, fill='x')

    country_combobox = country_frame.combobox
    country = CTK.StringVar(value="")
    country_combobox.configure(variable=country)
    country.trace_add('write', update_checkbox_visibility)

    check_var = CTK.StringVar(value="on")
    need_change_location_cb = CTK.CTkCheckBox(master=frame, text='Are you scraping inside the target country?', variable=check_var, onvalue='on', offvalue='off')

    confirm_button = CTK.CTkButton(master=frame, text='Confirm', command=on_confirm)
    confirm_button.pack(pady=10, padx=20)

    download_button = CTK.CTkButton(master=frame, text='Download Products Data', command=on_button_click, state='disabled')
    download_button.pack(pady=10, padx=20)

    root.mainloop()
