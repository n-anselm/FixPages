#!/usr/bin/python

# Author: n-anselm
# Description: Create a zip archive of every folder whose name ends
# in ".pages". Move the original folders to system trash and rename
# the zip archives to *.pages. Platform independent.
# Date created: 221128
# Date modified: 221222
# License: GPL v3.0

import os, sys, platform, send2trash
from zipfile import ZipFile

from PyQt6.QtWidgets import (QApplication, QMainWindow)
from main_window import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.path = ""
        self.pages_folders = []  # Create an empty list to store dir names ending in ".pages"
        self.dir_path_valid = True
        self.dir_path_exists = True
        self.cwd_name_valid = True

        self.ui.btnFix.clicked.connect(self.fix)  # Call fix() when fix btn is clicked

    # Get all folders with names ending in ".pages" and add to pages_folders
    # Also checks for input errors
    def get_pages_folders(self):

        host_platform = str(platform.system())  # Get the platform that the app is running on

        self.ui.lbMessage.setText("Getting all .pages folders...")

        try:
            self.path = self.ui.lePath.text()  # Get the path from the user path input
            # print("PATH: " + self.path)  # DEBUG

            # Remove the forward/backward slash because the next code part grabs the last part of
            # the dir path up to the slash to check if the dir name contains a space
            if self.path.endswith('/') or self.path.endswith('\\'):
                self.path = self.path[:-1]  # Remove the last char (which is going to be '/' or '\')

            # Check if working directory name has spaces (if it has spaces, the program won't work correctly)
            # Not allowed: "/home/user/docs/working dir"
            # Allowed: "/home/user/docs/workingdir"
            # Allowed: "/home/user/my docs/workingdir"
            # If running on Unix system
            if host_platform == "Linux" or host_platform == "Darwin":
                cwd_name = self.path[self.path.rindex('/') + 1:]
            else:  # Else on Windows
                cwd_name = self.path[self.path.rindex('\\') + 1:]

            # print("Current working dir name: " + cwd_name)  # DEBUG

            # If the path is not empty and the cwd does not have a space in name
            if self.path != "" and not " " in cwd_name:

                os.chdir(self.path)  # Change cwd to the one that was specified by user

                all_folders = [f for f in os.listdir('.') if os.path.isdir(f)]  # Get all dirs in cwd

                # DEBUG
                # print("----- List of all folders -----")
                # for i in all_folders:
                #     print(i)

                # Add all folders ending in ".pages" to pages_folders
                for f in all_folders:
                    if f.endswith(".pages"):
                        self.pages_folders.append(f)

                # DEBUG
                # print("----- List of folders ending in .pages -----")
                # for i in self.pages_folders:
                #     print(i)

                all_folders.clear()  # Clear the list (not essential)
            elif " " in cwd_name:
                self.cwd_name_valid = False
            else:
                self.dir_path_valid = False
        except:
            self.dir_path_exists = False

    # Recursively get all dir contents/filepaths
    def get_all_file_paths(self, directory):

        file_paths = []  # Create empty file paths list

        # Crawl through directory and subdirs
        for root, directories, files in os.walk(directory):
            for filename in files:
                # Join the two strings in order to form the full filepath
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)

        # Return file paths
        return file_paths

    # Create zip files from all folders ending in ".pages"
    def zip(self):
        self.ui.lbMessage.setText("Creating zip archives of folders...")
        for folder in self.pages_folders:
            # print(folder)  # DEBUG

            # Create the name to be used for the zip
            zipname = folder[:-6] + ".zip"

            # Get all file paths in the directory to zip
            file_paths = self.get_all_file_paths(folder)

            # DEBUG
            # Print all files to be zipped
            # print('The following files will be zipped:')
            # for file_name in file_paths:
            #     print(file_name)

            # Create the zip file
            with ZipFile(zipname, 'w') as zipp:
                # Write each file one by one
                for file in file_paths:
                    zipp.write(file)

        # print("All files zipped successfully!")  # DEBUG

    # Delete dirs ending in ".pages"
    def delete(self):
        self.ui.lbMessage.setText("Deleting original folders...")
        for f in self.pages_folders:
            # Send to trash (for optional recovery)
            folder = os.path.normpath(f)
            send2trash.send2trash(folder)

    # Rename the zip files from *.zip to *.pages
    def rename(self):
        self.ui.lbMessage.setText("Renaming from zip to pages...")
        for item in self.pages_folders:
            os.rename((item[:-6] + ".zip"), item)

    # Method called by fix button
    def fix(self):
        self.get_pages_folders()  # Get folders ending in ".pages"
        if self.dir_path_valid and self.cwd_name_valid and self.dir_path_exists:
            self.zip()
            self.delete()
            self.rename()
            self.ui.lbMessage.setText("Completed.")
        elif not self.cwd_name_valid:
            # Show error msg if cwd name has spaces
            self.ui.lbMessage.setText("Error: Current directory name should not contain spaces!")
            self.cwd_name_valid = True  # Reset
            # Show error msg if dir does not exist
        elif not self.dir_path_exists:
            self.ui.lbMessage.setText("Error: Directory does not exist!")
            self.dir_path_exists = True # Reset
        else:
            # Show error msg if dir path is invalid
            self.ui.lbMessage.setText("Error: Directory path is invalid!")
            self.dir_path_valid = True # Reset


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
