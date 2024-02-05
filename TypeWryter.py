#
# TypeWryter
#
# This code is a heavily modified version of zerowriter. Feel free to modify and redistribute as you want.
# Zerowriter GitHub: https://github.com/zerowriter/zerowriter1/tree/main
#
# Using the new4in2part library
#
# a python e-typewriter using eink and a USB keyboard
# this program outputs directly to the SPI eink screen, and is driven by a
# raspberry pi zero (or any pi). technically, it operates headless as the OS has no
# access to the SPI screen. it handles keyboard input directly via keyboard library.
#
# currently ONLY supports waveshare 4in2


import time
import keymaps
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import subprocess
from local_file_browser import start_server, stop_server
from utils import get_local_ip_address, get_random_name, clean_empty_files
import keyboard


class Menu:
    def __init__(self, display_draw, epd, display_image):
        self.display_draw = display_draw
        self.epd = epd
        self.display_image = display_image
        self.menu_items = []
        self.selected_item = 0
        # Get the current directory of this file
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Construct the absolute path to the font
        font_path = os.path.join(script_dir, 'Courier Prime.ttf')
        self.font16 = ImageFont.truetype(font_path, 16)
        #self.font13 = ImageFont.truetype('Courier Prime.ttf', 16)
    
    def addItem(self, text, action):
        self.menu_items.append({'text': text, 'action': action})

    def up(self):
        self.selected_item -= 1
        if self.selected_item < 0:
            self.selected_item = len(self.menu_items) - 1
        self.display()
    
    def down(self):
        self.selected_item += 1
        if self.selected_item > len(self.menu_items) - 1:
            self.selected_item = 0
        self.display()

    def select(self):
        self.menu_items[self.selected_item]['action']()

    def display(self):
        self.display_draw.rectangle((0, 0, 400, 300), fill=255)
        y_position = 10
        for index, item in enumerate(self.menu_items):
            prefix = self.selected_item == index and "> " or "  "
            self.display_draw.text((2, y_position), prefix + item['text'], font=self.font13, fill=0)
            y_position += 30
        partial_buffer = self.epd.getbuffer(self.display_image)
        self.epd.display_Partial(partial_buffer)

class TypeWryter:
    def __init__(self):

        #modifying thesde will mess up how text displays
        self.chars_per_line = 50 
        self.lines_on_screen = 15 
        self.font_size = 13
        self.line_spacing = 20
        self.scrollindex = 1

        #initializing vars
        self.epd = None
        self.display_image = None
        self.display_draw = None
        self.display_updating = False
        self.cursor_position = 0
        self.text_content = ""
        self.input_content = ""
        self.previous_lines = []
        self.needs_display_update = True
        self.needs_input_update = True
        self.console_message = ""
        self.updating_input_area = False
        self.control_active = False
        self.shift_active = False
        self.menu_mode = False
        self.server_menu = None
        self.menu = None
        self.parent_menu = None # used to store the menu that was open before the load menu was opened
        self.typewrytes_dir = ""

        # Can add other font sizes and change them wherever text is rendered.

        # Get the current directory of this file
        script_dir = os.path.dirname(os.path.realpath(__file__))

        # Construct the absolute path to the font
        font_path = os.path.join(script_dir, 'Courier Prime.ttf')

        # Use the absolute path for the font
        self.font13 = ImageFont.truetype(font_path, 13)
        self.font16 = ImageFont.truetype(font_path, 16)
        #self.font13 = ImageFont.truetype('Courier Prime.ttf', 13)
        #self.font16 = ImageFont.truetype('Courier Prime.ttf', 16)
        
        self.ascii_art_lines = [
        "+-----------------------------------+",
        "| _____                             |",
        "||_   _|   _ _ __   ___             |",
        "|  | || | | | '_ \\ / _ \\            |",
        "|  | || |_| | |_) |  __/            |",
        "|  |_| \\__, | .__/ \\___|            |",
        "|__    |___/|_|        _            |",
        "|\\ \\      / / __ _   _| |_ ___ _ __ |",
        "| \\ \\ /\\ / / '__| | | | __/ _ \\ '__||",
        "|  \\ V  V /| |  | |_| | ||  __/ |   |",
        "|   \\_/\\_/ |_|   \\__, |\\__\\___|_|   |",
        "|                |___/              |",
        "+-----------------------------------+",
        ]
        self.help_lines = [
        "                                     ",
        "[CTRL+M]   - Show Menu",
        "[CTRL+S]   - Save",
        "[CTRL+N]   - New File",
        "[CTRL+R]   - Refresh the display",
        "[CTRL+W]   - Show current word count",
        "[CTRL+esc] - Reboot the device",
        "                                ",
        " ** Press any key to continue** "
        ]
        
        #Get a random from utils and create the initial file
        self.fname,self.short_name = get_random_name()
        self.filename = os.path.join(os.path.dirname(__file__), 'TypeWrytes', f'{self.fname}.txt')
        
        self.manual = self.cache_file_path = os.path.join(os.path.dirname(__file__), 'data', 'TypeWryter_Manual.txt') # Manual file
        self.cache_file_path = os.path.join(os.path.dirname(__file__), 'data', 'cache.txt') # cache file
    
    def initialize(self):
        #init the display and create initial image
        self.epd.init()
        self.epd.Clear()
        self.display_image = Image.new('1', (self.epd.width, self.epd.height), 255)
        self.display_draw = ImageDraw.Draw(self.display_image)
        self.last_display_update = time.time()

        clean_empty_files() #clean empty files in the TypeWrytes directory

        self.splash_screen() #display startup splash screen

        # establish keyboard listeners
        self.keyboard.on_press(self.handle_key_down, suppress=False) #handles modifiers and shortcuts
        self.keyboard.on_release(self.handle_key_press, suppress=True)
    
        # Populate the main menu items
        self.menu = Menu(self.display_draw, self.epd, self.display_image)
        self.menu.addItem("New", lambda: self.new_file())
        self.menu.addItem("Load", lambda: self.show_load_menu())
        self.menu.addItem("Network File browser", lambda: self.show_server_menu())
        self.menu.addItem("Help", lambda: self.load_manual())
        self.menu.addItem("Update TypeWryter", self.update_TypeWryter)
        self.menu.addItem("Power Off", self.power_down)
        self.menu.addItem("Back", self.hide_menu)

        # populate the 'load' menu
        self.load_menu = Menu(self.display_draw, self.epd, self.display_image)
        self.populate_load_menu()

        # Populate the network browser menu
        self.server_menu = Menu(self.display_draw, self.epd, self.display_image)
        self.server_menu.addItem("Start Server", lambda: self.start_file_server())
        self.server_menu.addItem("Stop Server", lambda: self.stop_file_server())
        self.server_menu.addItem("Back", lambda: self.hide_child_menu())

    #generate initial display buffer for display
    def partial_update_buffer(self):
        partial_buffer = self.epd.getbuffer(self.display_image)
        self.epd.display_Partial(partial_buffer)

    # Update the display with the new image
    def full_update_buffer(self):
        partial_buffer = self.epd.getbuffer(self.display_image)
        self.epd.display(partial_buffer)

    def splash_screen(self):
        y_position = 2 # Starting Y position
        # Add each line of the ASCII art to the image
        for line in self.ascii_art_lines:
            self.display_draw.text((50, y_position), line, font=self.font13, fill=0)
            y_position += 13  # Adjust line spacing as needed

        # Add each line of the help text
        for line in self.help_lines:
            self.display_draw.text((50, y_position), line, font=self.font13, fill=0)
            y_position += 13

        # Update the display with the new image
        self.full_update_buffer()
        keyboard.read_key() # wait for any keyboard input before proceeding past the splash screen

    def show_load_menu(self):
        print("showing load menu")
        self.parent_menu = self.menu
        self.populate_load_menu()

        self.menu = self.load_menu
        self.menu.display()

    def hide_child_menu(self):
        print("hiding child menu")
        self.menu = self.parent_menu
        self.menu.display()

    def populate_load_menu(self):
        print("populate load menu")
        self.load_menu.menu_items.clear()
        data_folder_path = os.path.join(os.path.dirname(__file__), 'TypeWrytes')
        try:
            # List all files in the data folder
            files = [f for f in os.listdir(data_folder_path) if os.path.isfile(os.path.join(data_folder_path, f)) and f.endswith('.txt')]
            # Sort files by modification time
            files.sort(key=lambda x: os.path.getmtime(os.path.join(data_folder_path, x)), reverse=True)

            self.load_menu.addItem("Back", self.hide_child_menu)

            # Add each file to the load menu
            for filename in files:
                self.load_menu.addItem(filename, lambda f=filename: self.load_file_into_previous_lines())
        except Exception as e:
            print(f"Failed to list files in {data_folder_path}: {e}")

    def hide_menu(self):
        print("hiding menu")
        self.menu_mode = False
        self.update_display()

    def show_menu(self):
        print("show menu")
        self.menu_mode = True
        self.menu.display()

    def show_server_menu(self):
        print("showing server menu")
        self.parent_menu = self.menu

        self.menu = self.server_menu
        self.menu.display()

    def menu_up(self):
        self.menu.up()
    
    def menu_down(self):
        self.menu.down()

    def ensure_sub_dirs(self):
        self.typewrytes_dir = os.path.join(os.getcwd(), "TypeWrytes")
        if not os.path.exists(self.typewrytes_dir):
            os.makedirs(self.typewrytes_dir)
            return self.typewrytes_dir
    
    def get_word_count(self, file_path):
        try:
            with open(file_path, 'r') as file: # open the current file
                self.content = file.read() #read in contents
                self.words = self.content.split() # split it into single words
                return len(self.words) # return length.
        except IOError as e:
            self.console_message = f"[Error getting wordcount]"
            print("Failed to WC:", e)

    # This is almost an exact copy of load_file_into_previous_lines() - I'll combine the functions at some point.
    def load_manual(self):
        try:
            with open(self.manual, 'r') as file:
                lines = file.readlines()
                self.previous_lines = [line.strip() for line in lines]

                # Clear the main display area -- also clears input line (270-300)
                self.display_draw.rectangle((0, 0, 400, 300), fill=255)
                
                # Display the previous lines
                y_position = 280 - self.line_spacing  # leaves room for cursor input

                #Make a temp array from previous_lines. And then reverse it and display as usual.
                current_line=max(0,len(self.previous_lines)-self.lines_on_screen*self.scrollindex)
                temp=self.previous_lines[current_line:current_line+self.lines_on_screen]

                for line in reversed(temp[-self.lines_on_screen:]):
                    self.display_draw.text((10, y_position), line[:self.chars_per_line], font=self.font13, fill=0)
                    y_position -= self.line_spacing
                
                #generate display buffer for display
                self.partial_update_buffer()

                self.last_display_update = time.time()
                self.display_updating = False
                self.needs_display_update = False

        except Exception as e:
            self.console_message = f"[Error loading file]"
            print(f"Failed to load file {self.manual}: {e}")
            self.update_display()
            time.sleep(1)
            self.console_message = ""
            self.update_display()
        finally:

            self.menu = self.parent_menu
            self.hide_menu()

    def new_file(self):
        #save the cache first
        self.fname,self.short_name = get_random_name()
        self.filename = os.path.join(os.path.dirname(__file__), 'TypeWrytes', f'{self.fname}.txt')
        self.save_previous_lines(self.filename, self.previous_lines)
        
        #create a blank doc
        self.previous_lines.clear()
        self.input_content = ""

        self.console_message = f"[New] - {self.short_name}"
        self.update_display()
        time.sleep(1)
        self.console_message = ""
        self.update_display()

    def power_down(self):
        #run powerdown script
        self.display_draw.rectangle((0, 0, 400, 300), fill=255)  # Clear display
        self.display_draw.text((55, 150), "TypeWryter Powered Down.", font=self.font13, fill=0)
        self.partial_update_buffer()
        time.sleep(3)
        subprocess.run(['sudo', 'poweroff', '-f'])
        
        self.needs_display_update = True
        self.needs_input_update = True

    def update_TypeWryter(self):
        print("updating TypeWryter")
        self.console_message = f"[Updating]"
        self.update_display()

        completed_process = subprocess.run(['git', 'pull'])
        if completed_process.returncode != 0:
            print(completed_process.stdout)
            print(completed_process.stderr)
            self.console_message = f"[Error updating]"
            self.update_display()
            time.sleep(1)
            self.console_message = ""
            self.update_display()
            return
        self.console_message = f"[Updated]"
        self.update_display()
        time.sleep(1)
        self.console_message = "Rebooting"
        self.update_display()
        self.reboot()

    def reboot(self):
        print("rebooting")
        subprocess.run(['sudo', 'reboot', '-f'])

    def load_file_into_previous_lines(self):
        #self.file_path = os.path.join(os.path.dirname(__file__), 'TypeWrytes', filename)
        try:
            with open(self.filename, 'r') as file:
                lines = file.readlines()
                self.previous_lines = [line.strip() for line in lines]
                self.input_content = ""
                self.cursor_position = 0
                self.console_message = f"[Loaded {self.short_name}]"
                self.update_display()
                time.sleep(1)
                self.console_message = ""
                self.update_display()
                print("loaded: " + self.filename)
        except Exception as e:
            self.console_message = f"[Error loading file]"
            print(f"Failed to load file {self.filename}: {e}")
            self.update_display()
            time.sleep(1)
            self.console_message = ""
            self.update_display()
        finally:
            self.menu = self.parent_menu
            self.hide_menu()

    def load_previous_lines(self):
        try:
            with open(self.cache_file_path, 'r') as file:
                print(self.cache_file_path)
                lines = file.readlines()
                return [line.strip() for line in lines]
        except FileNotFoundError:
            print("error")
            return []

    def save_previous_lines(self, file, lines):
      try:
          # Ensure the directory exists
          os.makedirs(os.path.dirname(self.filename), exist_ok=True)
          # Check if the file is writable or create it if it doesn't exist
          with open(self.filename, 'a') as file:
              pass
          # Clear the file content before writing
          with open(self.filename, 'w') as file:
              print("Saving to file:", self.filename)
              for line in lines:
                  #file.write(line + '\n')
                  file.write(line)
      except IOError as e:
          self.console_message = f"[Error saving file]"
          print("Failed to save file:", e)

    def start_file_server(self):
        # get local IP
        local_ip = get_local_ip_address()
        url = f"http://{local_ip}:5000" # generate full url string
        flask_pass = start_server() 
        message1 = f"Scan QR, or visit: {url}"
        message2 = f"password: {flask_pass}"

        #Generate QR Code
        qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=2,
                border=4,)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')

        # Convert QR code image to match the display's image mode
        qr_img_converted = qr_img.convert('1')

        # Save QR code to the filesystem
        qr_img_save_path = os.path.join(os.path.dirname(__file__), 'data', 'qr_code.png')
        qr_img.save(qr_img_save_path)
        print(f"QR code saved to {qr_img_save_path}")

        # Calculate position to center QR code on the display
        qr_x = (self.epd.width - qr_img_converted.width) // 2
        qr_y = (self.epd.height - qr_img_converted.height) // 2

        # Clear the current display image
        self.display_draw.rectangle((0, 0, 400, 300), fill=255)
        
        # Display messages
        self.display_draw.text((30, 90),message1, font=self.font13, fill=0)
        self.display_draw.text((75, 105),message2, font=self.font16, fill=0)

        # Paste the QR code onto the display image
        self.display_image.paste(qr_img_converted, (qr_x, qr_y))

        # Update the display with the new image
        self.partial_update_buffer()

    def stop_file_server(self):
        #stop Flask server
        stop_server()
        print("File Server Stopped")

        self.display_draw.rectangle((0, 0, 400, 300), fill=255)  # Clear display
        
        # Show a message shutting down file server
        self.display_draw.text((30, 100),"Shutting Down FileServer", font=self.font13, fill=0)

        # Update the display with the new image
        partial_buffer = self.epd.getbuffer(self.display_image)
        self.epd.display_Partial(partial_buffer)

        self.hide_child_menu()


    def update_display(self):
        self.display_updating = True

        # Clear the main display area -- also clears input line (270-300)
        self.display_draw.rectangle((0, 0, 400, 300), fill=255)
        
        # Display the previous lines
        y_position = 280 - self.line_spacing  # leaves room for cursor input

        #Make a temp array from previous_lines. And then reverse it and display.
        current_line=max(0,len(self.previous_lines)-self.lines_on_screen*self.scrollindex)
        temp=self.previous_lines[current_line:current_line+self.lines_on_screen]
        # print(temp)# to debug if you change the font parameters (size, chars per line, etc)

        for line in reversed(temp[-self.lines_on_screen:]):
          self.display_draw.text((0, y_position), line[:self.chars_per_line], font=self.font13, fill=0)
          y_position -= self.line_spacing

        #Display Console Message
        if self.console_message != "":
            self.display_draw.rectangle((180, 280, 400, 300), fill=255)
            self.display_draw.text((150, 280), self.console_message, font=self.font13, fill=0)
            self.console_message = ""
        
        #generate display buffer for display
        self.partial_update_buffer()

        self.last_display_update = time.time()
        self.display_updating = False
        self.needs_display_update = False

    def update_input_area(self):
        cursor_index = self.cursor_position
        self.display_draw.rectangle((0, 280, 400, 300), fill=255)  # Clear display
        
        #add cursor
        temp_content = self.input_content[:cursor_index] + "|" + self.input_content[cursor_index:]

        #draw input line text
        self.display_draw.text((0, 280), str(temp_content), font=self.font13, fill=0)
        
        #generate display buffer for input line
        self.updating_input_area = True
        self.partial_update_buffer()
        self.updating_input_area = False

    def insert_character(self, character):
        cursor_index = self.cursor_position
        
        if cursor_index <= len(self.input_content):
            # Insert character in the text_content string
            self.input_content = self.input_content[:cursor_index] + character + self.input_content[cursor_index:]
            self.cursor_position += 1  # Move the cursor forward
        
        self.needs_input_update = True

    def delete_character(self):
        if self.cursor_position > 0:
            # Normal backspace functionality
            self.input_content = self.input_content[:self.cursor_position - 1] + self.input_content[self.cursor_position:]
            self.cursor_position -= 1
            self.needs_input_update = True
        elif self.previous_lines:
            # Pull the last line from previous_lines if cursor is at the start of the input content
            last_line = self.previous_lines.pop()
            self.input_content = last_line + self.input_content
            self.cursor_position = len(last_line)  # Position cursor at the end of the pulled line
            self.needs_display_update = True

    def handle_key_down(self, e):
        if e.name == 'shift': #if shift is released
            self.shift_active = True
        if e.name == 'ctrl': #if shift is released
            self.control_active = True
    
    #the delete word function works, but seems unstable. Crashes if you do it too quickly
    def delete_previous_word(self):
        # Split the current input content into words
        words = self.input_content.split(' ')
        if words:
            words = words[:-1]  # Remove the last word
        self.input_content = ' '.join(words) # replace last word with a ' '
        self.cursor_position = len(self.input_content)#update the cursor position
        self.update_display()

    def handle_key_press(self, e):
        if e.name== "s" and self.control_active:
            if not (self.menu_mode):
                self.save_previous_lines(self.filename, self.previous_lines)
                
                self.console_message = f"[Saved] - {self.short_name}"
                self.update_display()
                time.sleep(2)
                self.console_message = ""
                self.update_display()
        
        if e.name == "m" and self.control_active: #ctrl+m
            self.show_menu()

        if e.name == "w" and self.control_active: #ctrl+w
            if not (self.menu_mode):
                wc = self.get_word_count(self.filename)
                print("Word Count: " + str(wc))
                self.console_message = "Word count: " + str(wc)
                self.update_display()
                time.sleep(2)
                self.console_message = ""
                self.update_display()

        #new file (clear) via ctrl + n
        if e.name== "n" and self.control_active: #ctrl+n
            if not (self.menu_mode):
                self.new_file()

        if e.name== "down" or e.name== "right":
          if (self.menu_mode):
            self.menu_down()
            return

        if e.name== "up" or e.name== "left":
          if (self.menu_mode):
            self.menu_up()
            return

        if e.name == 'esc':
            if (self.menu_mode):
                self.hide_menu()
                return

        if e.name == "esc" and self.control_active: #ctrl+esc
            self.power_down()
            pass

        if e.name == "r" and self.control_active: #ctrl+r
            self.epd.init()
            self.epd.Clear()
            self.update_display()
            
        if e.name == "tab":
            if not (self.menu_mode): 
                #just using two spaces for tab
                self.insert_character(" ")
                self.insert_character(" ")
                self.insert_character(" ")
            
                # Check if adding the character exceeds the line length limit
                if self.cursor_position > self.chars_per_line:
                    self.previous_lines.append(self.input_content)                
                    # Update input_content to contain the remaining characters
                    self.input_content = ""
                    self.needs_display_update = True #trigger a display refresh
                # Update cursor_position to the length of the remaining input_content
                self.cursor_position = len(self.input_content)
                
                self.needs_input_update = True
            
        if e.name == "backspace":
            if not (self.menu_mode):
                print('backspace')
                self.delete_character()
                self.needs_input_update = True

        if e.name == "backspace" and self.control_active:
            if not (self.menu_mode):
                self.delete_previous_word()
                self.needs_input_update = True

        elif e.name == "space": #space bar
            if not (self.menu_mode):
                self.insert_character(" ")
            
                # Check if adding the character exceeds the line length limit
                if self.cursor_position > self.chars_per_line:
                    self.previous_lines.append(self.input_content)                
                    self.input_content = ""
                    self.needs_display_update = True
                # Update cursor_position to the length of the remaining input_content
                self.cursor_position = len(self.input_content)
            
                self.needs_input_update = True
        
        elif e.name == "enter":
            if (self.menu_mode):
                self.menu.select()
                return

            else:
                self.insert_character("\n") #a newline is only inserted when the user hits enter. 
                # Add the input to the previous_lines array
                self.previous_lines.append(self.input_content)
                self.input_content = "" #clears input content
                self.cursor_position=0
                #save the file when enter is pressed
                self.save_previous_lines(self.filename, self.previous_lines)
                self.needs_display_update = True
            
        if e.name == 'ctrl': #if control is released
            self.control_active = False 

        if e.name == 'shift': #if shift is released
            self.shift_active = False

        if len(e.name) == 1 and self.control_active == False:  # letter and number input
            if self.shift_active:
                char = keymaps.shift_mapping.get(e.name, e.name)  # Default to e.name if no mapping
                self.input_content += char
            else:
                self.input_content += e.name

            self.cursor_position = len(self.input_content)
            self.needs_input_update = True

            # Check if adding the character exceeds the line length limit
            if len(self.input_content) > self.chars_per_line:
                # Cut off the part of the input_content that exceeds chars_per_line
                sentence = self.input_content[:self.chars_per_line]
                self.previous_lines.append(sentence)

                # Update input_content to start with the next line
                self.input_content = self.input_content[self.chars_per_line:]
                self.cursor_position = len(self.input_content)

                self.needs_display_update = True

                
        # Update cursor_position to the length of the remaining input_content
        #self.cursor_position = len(self.input_content)                

        self.typing_last_time = time.time()
        self.needs_input_update = True

    def handle_interrupt(self):
      self.keyboard.unhook_all()
      self.epd.init()
      self.epd.Clear()
      exit(0)

    def loop(self):
        if self.needs_display_update and not self.display_updating:
            print("updating display")
            self.update_display()
            self.update_input_area()
            self.needs_diplay_update=False
            self.typing_last_time = time.time()

            # pulling this out for the time being because this actually breaks the file server when the refresh happens
            '''# If the user hasn't typed in over 30 seconds do a full clear and refresh of the screen.
            if (time.time()-self.typing_last_time) > (30):
            self.epd.init()
            self.epd.Clear()
            self.update_display()
            self.update_input_area()
            self.needs_diplay_update=False
            keyboard.read_key()'''
            
        elif (time.time()-self.typing_last_time)<(.75): #if not doing a full refresh, do partials
            print("updating display partial")
            #the screen enters a high refresh mode when there has been keyboard input
            if not self.updating_input_area and self.scrollindex==1:
                self.update_input_area()

    def run(self):
        while True:
            self.loop()