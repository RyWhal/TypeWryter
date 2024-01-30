import os
import curses
from datetime import datetime
import re
from local_file_browser import start_server, stop_server

class FileManager:
    def __init__(self, directory):
        self.directory = directory
        self.folder_name = "TypeWrytes"
        self.create_save_folder(self.folder_name)

    def ensure_typewrytes_directory():
        typewrytes_dir = os.path.join(os.getcwd(), "TypeWrytes")
        if not os.path.exists(typewrytes_dir):
            os.makedirs(typewrytes_dir)
            return typewrytes_dir

    def view_free_writes(self, screen):
        height, width = screen.getmaxyx()  # Adjust the size as needed
        start_y, start_x = 0, 0  # Adjust the position as needed

        stats_win = curses.newwin(height, width, start_y, start_x)
        stats_win.box()
        stats_win.keypad(True)  # Enable keypad mode for scrolling

        # Now call the file_manager's list_files method
        self.list_files(stats_win)

    def list_files(self, window):
        max_height, max_width = window.getmaxyx()
        top_line = 0 
        files = sorted([f for f in os.listdir(self.directory) if f.endswith('.txt')]) # List .txt files and sort alphabetically
        window.clear()

        #window.addstr(0,0, "   [FILENAME]   |  [CREATED]  |  [MODIFIED]  |  [SIZE]  |  [WORDCOUNT]   ")
        #window.refresh()
        while True:
            window.clear()
            for i, filename in enumerate(files[top_line:top_line + max_height - 2]):
                file_info = self.get_file_info(filename, max_width)
                window.addstr(i + 1, 1, file_info[:max_width-2])  # Truncate to fit the window

            window.refresh()
            key = window.getch() # listen for key press
            # Scroll handling
            if key == curses.KEY_UP and top_line > 0:
                top_line -= 1
            elif key == curses.KEY_DOWN and top_line < len(files) - (max_height - 2):
                top_line += 1
            elif key == 27:  # ESC key to exit
                break

        
        window.clear()
        window.refresh()

    def get_file_info(self, filename, max_width):
        filepath = os.path.join(self.directory, filename)
        stats = os.stat(filepath)
        creation_date = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d')
        modified_date = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d')
        size = stats.st_size
        word_count = self.get_word_count(filepath)

        file_info = f"{filename} | Created: {creation_date} | Modified: {modified_date} | Size: {size} bytes | Word Count: {word_count}"
        
        return file_info

    def get_word_count(self, filepath):
        with open(filepath, 'r') as file:
            content = file.read()
            words = content.split()
            return len(words)

    def select_file(self, window):
        window.clear()
        window.refresh()
        files = sorted([f for f in os.listdir(self.directory) if f.endswith('.txt')])
        current_row = 0

        def print_files():
            window.clear()
            for idx, filename in enumerate(files):
                if idx == current_row:
                    window.attron(curses.color_pair(1))  # Highlighted
                    window.addstr(idx, 0, filename)
                    window.attroff(curses.color_pair(1))
                else:
                    window.addstr(idx, 0, filename)  # Normal
            window.refresh()

        while True:
            print_files()
            key = window.getch()
            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(files) - 1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return files[current_row]  # Return the selected filename
            elif key == 5 or key == 27: # CTRL+E or ESC key to exit
                break

        return None

    def read_file(self, filename):
        # Open and display the content of the file in read-only mode
        pass

    def rename_file(self, screen):
        # enumerate files
        files = sorted([f for f in os.listdir(self.directory) if f.endswith('.txt')])
        self.check_freewrites_not_empty(files) # Check to see if the directory is empty

        # Select the file to rename
        filename_to_rename = self.select_file(screen)
        if not filename_to_rename:
            return  # No file selected

        # Prompt for a new name
        screen.clear()
        screen.addstr(0, 0, "Enter the new name for the file (without extension): ")
        screen.refresh()
        curses.echo()  # Echo user input to the screen
        new_name_bytes = screen.getstr(0, 53, 25)  # Limit new name to 25 characters
        curses.noecho()
        new_name = new_name_bytes.decode('utf-8')  # Decode to a string

        if new_name and new_name + ".txt" not in os.listdir(self.directory):
            pass
        else:
            screen.clear
            screen.addstr(0, 0, "Filename already exists or is invalid. Please enter a different name.")
            while new_name + ".txt" in os.listdir(self.directory):
                # Prompt for a new name
                screen.refresh()
                screen.addstr(1, 0, "Enter the new name for the file (without extension): ")
                curses.echo()  # Echo user input to the screen
                new_name_bytes = screen.getstr(1, 53, 25)  # Limit new name to 25 characters
                curses.noecho()
                new_name = new_name_bytes.decode('utf-8')  # Decode to a string
            screen.getch()  # Wait for keypress before asking again
            

        # verify that characters are aplphanumeric or - _ = + 
        if not re.match("^[A-Za-z0-9-_+=]+$", new_name):
            screen.addstr(3, 0, "Invalid filename. Only alphanumeric and -_+= are allowed.")
            screen.refresh()
            screen.getch()
            return

        # Confirm rename
        screen.addstr(3, 0, f"Are you sure you want to rename '{filename_to_rename}' to '{new_name}'? (y/n): ")
        screen.refresh()
        key = screen.getch()
        if key in [ord('y'), ord('Y')]:
            old_filepath = os.path.join(self.directory, filename_to_rename)
            new_filepath = os.path.join(self.directory, new_name + ".txt")
            os.rename(old_filepath, new_filepath)
            screen.addstr(5, 0, "File renamed successfully.")
        else:
            screen.addstr(5, 0, "Rename cancelled.")

        screen.refresh()
        screen.getch()  # Wait for key press

    def delete_file(self, window):
        # Check if there are files to rename
        files = sorted([f for f in os.listdir(self.directory) if f.endswith('.txt')])
        self.check_freewrites_not_empty(files)

        filename_to_delete = self.select_file(window)

        if filename_to_delete:
            # Clear window and ask for confirmation
            window.clear()
            window.addstr(0, 0, "Are you sure you want to delete {}? (y/n): ".format(filename_to_delete))
            window.refresh()
            key = window.getch()
            if key in [ord('y'), ord('Y')]:
                os.remove(os.path.join(self.directory, filename_to_delete))
                window.addstr(1, 0, "File deleted successfully.")
                window.refresh()
                window.getch()
            else:
                window.addstr(1, 0, "Deletion cancelled.")
                window.refresh()
                window.getch()

    def cleanup_empty_files(self, window):
        # Find and delete all 0 size .txt files
        files = [f for f in os.listdir(self.directory) if f.endswith('.txt')]
        self.check_freewrites_not_empty(files)
       
        window.clear()
        window.addstr(0, 0, "Are you sure you want to clean up empty files? (y/n): ")
        window.refresh()
        key = window.getch() # Wait for input

        # If 'y' then clean 0 size files
        if key in [ord('y'), ord('Y')]:
            for filename in files:
                filepath = os.path.join(self.directory, filename)
                if os.path.getsize(filepath) == 0:
                    os.remove(filepath)
            window.addstr(1, 0, "Files Cleaned")
            window.refresh()
            window.getch()
        else:
            window.addstr(1, 0, "Aborted")
            window.refresh()
            window.getch()
        

    def show_file_management_menu(self, screen):
        
        file_menu_items = ["<List files>", "<Rename free write>", "<Delete free write>", 
                           "<Download Files>","<Clean-up blank free writes>" ]
        current_row = 0  # Current highlighted menu item
        # Function to print the menu
        def print_menu():
            screen.clear()
            for idx, item in enumerate(file_menu_items):
                if idx == current_row:
                    screen.attron(curses.color_pair(1))
                    screen.addstr(idx, 0, item)
                    screen.attroff(curses.color_pair(1))
                else:
                    screen.addstr(idx, 0, item)
            screen.refresh()

        while True:
            print_menu()
            key = screen.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(file_menu_items) - 1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_row == 0:
                    self.view_free_writes(screen)  # Logic to list and select files
                elif current_row == 1:
                    self.rename_file(screen)
                elif current_row == 2:
                    self.delete_file(screen)  # Call delete_file method
                elif current_row == 3:
                    start_server()  # This starts the Flask server in a separate thread
                    display_web_window(screen)
                    #wait_for_escape(screen.getch())
                    stop_server()
                elif current_row == 4:
                    screen.clear()
                    self.cleanup_empty_files(screen) # Logic to cleanup empty files
                    screen.refresh()
            elif key == 5 or key == 27:  # CTRL+E or ESC key to exit
                break