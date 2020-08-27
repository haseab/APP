from notion.client import NotionClient
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import time
import glob
import os


class DataHandler():
    def __init__(self):
        pass

    def save_data(self, df):
        """
        Saves the dataframe to a csv in the same directory
        Parameters:
            df: dataframe
        Returns:
            str - file name
        """
        dt = datetime.now()
        file = f"Tasks {dt.year}_{dt.month}_{dt.day}_{dt.hour}.txt"
        df.to_csv(file, index=False)
        string = "Saved Data as: " + file
        self.file = file
        print(string)
        return file

    def get_tasks_file(self, file=None):
        """
        Reads the table from the file and sorts from Completed Tasks First
        Parameters:
            file - csv file that will be turned into a table

        Returns:
            df - dataframe object
        """
        # Check if file has been passed as an argument
        if file == None:
            print("Please indicate the file location!")
            return None
        # Reading of CSV
        df = pd.read_csv(file).fillna('')
        # Converting "Yes" and "No" Values into True and False Booleans instead
        df["Completed"] = [True if i == "Yes" else False for i in df["Completed"]]
        # Putting all Completed Tasks first and then followed by Not Completed Tasks
        df = pd.concat([df[df["Completed"] == True], df[df["Completed"] == False]]).reset_index(drop=True)
        return df

    def get_latest_tasks_file(self):
        """
        Instead of passing an argument of the file name, it uses the os module
        to deterine the most recently modified txt file in the folder and uses that

        Returns:
            df - dataframe
        """
        # Calling function to get most recent file
        file = self._get_latest_file("Tasks")
        # Reading csv and filling Na values with blank strings
        df = pd.read_csv(file).fillna('')
        return df

    def update_tasks(self, file=None):
        """
        There are two types of task files:
            1. CSV where changes are updated
            2. Cached Tasks list saved as a txt to be used as reference

        This function compares the two task lists and indicates what is different
        between the two lists and what specifically changed. The format is as follows

        >>> update_tasks()
        DATA CHANGED,
        Task:      Inspecting system
        Column:    Completed
        Old Value: False
        New Value: True
        Are you sure you want to continue with the above changes? y/n

        Returns:
            Original Dataset if nothing is changed
            tuple of dataset with a counter
        """
        # Checking for argument being passed
        if file == None:
            print("Please enter the file you want for updates")
            return None
        # Getting cached task list, df (datframe)
        df = self.get_latest_tasks_file().fillna('')
        # Getting updating task list, ndf (new dataframe)
        ndf = self.get_tasks_file(file)

        # Creating a copy of both dataframes
        # Setting the index of both dataframes as the task for easier coding
        # It will be changed back once the comparison is done
        df2 = df.set_index("Task")
        ndf2 = ndf.set_index("Task")
        totalcount, counter2 = 0, 0

        # Dataframes without task as index, split into completed and not completed
        dftrue = df2[df2["Completed"] == True]
        ndftrue = ndf2[ndf2["Completed"] == True]
        dffalse = df2[df2["Completed"] == False]
        ndffalse = ndf2[ndf2["Completed"] == False]

        # Iterating through originally to-do tasks
        for i in dffalse.index:
            # Checking if tasks went from to-do to completed
            if i not in ndffalse.index and i in ndftrue.index:
                print(f"Task Completed: {i}")
                counter2 += 1
            # Checking if tasks went from to-do to being removed completely
            if i not in ndffalse.index and i not in ndftrue.index:
                print(f"Task Removed from To-Do: {i}")
                counter2 += 1

        for i in dftrue.index:
            # Checking if task went from completed to to-do
            if i not in ndftrue.index and i in ndffalse.index:
                print(f"Task Uncompleted: {i}")
                counter2 += 1
            # Checking if tasks went from completed to being removed completely
            if i not in ndffalse.index and i not in ndftrue.index:
                print(f"Task Removed from Completed: {i}")
                counter2 += 1

        # Iterating through the new to-do list
        for i in ndffalse.index:
            # Checking to see any new to-do's that weren't in the original to-do
            if i not in dffalse.index and i not in dftrue.index:
                print(f"Task added to to-do list: {i}")
                counter2 += 1

        # Iterating through the new completed list
        for i in ndftrue.index:
            # Checking to see if anything got added to "completed" without being a to-do first
            if i not in dffalse.index and i not in dftrue.index:
                print(f"Task added to completed without being on to-do list: {i}")
                counter2 += 1

        # Calling function that sees if any values were changed
        taskdf, counter = self._data_change_tracker(df, ndf)

        # If any changes were made, the counters should have integer values
        totalcount = counter + counter2
        if totalcount == 0:
            print("\nNothing happened")
            return df, 1
        else:
            # The changes are shown in a printout, and the following question is asked
            inputs = input("Are you sure you want to continue with the above changes? y/n")
            if inputs in ["Y", "y", "yes", "Yes", "YES", "YEs"]:
                print("Items added to new list!")
                # Resetting the indices
                dftrue = dftrue.reset_index()
                ndftrue = ndftrue.reset_index()
                dffalse = dffalse.reset_index()
                ndffalse = ndffalse.reset_index()

                # Merging completed and to-do list
                df3 = ndffalse.merge(ndftrue, how="outer").reset_index(drop=True).drop_duplicates(subset="Task")
                return df3, 0

            else:
                print("Returning original dataset")
                return df, 1

    def update_tasks_to_csv(self, file=None):
        """
        Wrapper function of "update_tasks" function. This one saves changes as a csv
        """
        df, count = self.update_tasks(file)
        if count == 1:
            print("Nothing was saved")
            return None
        text = self.save_data(df)
        return df, count

    def _data_change_tracker(self, df, ndf):
        """Checks to see if any specific values of the table have been changed
           Parameters:
               df: old task list
               ndf: new task list

            Returns: Combined dataframe of both old and new dataframes
        """

        # Checking if dataset is a weighted table with format ['Completed','Task','ETA',Context','Subsprint','Score','Day Completed']
        # or if it is a regular table with format ['Completed','Task','ETA','Day Completed']
        if "Completed_x" in df.columns:
            taskdf = df.merge(ndf, how="inner", on="Task").set_index("Task").drop(
                ["Completed_x", "Completed_y", "Score_x", "Score_y"], axis=1)
        else:
            taskdf = df.merge(ndf, how="inner", on="Task").set_index("Task")
        col = taskdf.columns.values
        counter = 0
        #
        for i in range(int(len(col) / 2)):
            check = (taskdf[col[i]] == taskdf[col[i + int(len(col) / 2)]])
            if (check).all() == False:
                counter += 1
                for j in check.index:
                    if check[j] == False:
                        value = taskdf.loc[j][[col[i], col[i + int(len(col) / 2)]]].values
                        print(
                            f"\nDATA CHANGED,  \nTask:\t   {j} \nColumn:    {col[i][:-2]} \nOld Value: {value[0]} \nNew Value: {value[1]}")
        if counter == 0:
            print("\nData is identical. No Data changed")
        return taskdf, counter

    def _get_latest_file(self, first_word, path='/Users/owner/Desktop/Datasets/TaskIntegrator/*'):
        """Gets the name of the most recently modified .txt file in the directory.
            Parameters
                first_word - the first word of the file. This is to minimize risk of picking a the wrong
                            .txt file that happened to be modified recently
                path - the file directory you want to explore

            Returns:
                the last element (most recent) of the list of file names
        """
        list_of_files = glob.iglob(path)  # * means all if need specific format then *.csv
        latest_file = sorted(list_of_files, key=os.path.getctime)
        latest_file = [i.split("\\")[1] for i in latest_file]  # Slicing

        # Gathering list of files that are under the first name
        latest_file = [i for i in latest_file if i.split()[0] == first_word]
        #         inputs = input(f"File read was {latest_file[-1]}. Proceed? (y/n): ")
        #         if inputs in ["Y","y","yes","Yes","YES", "YEs"]:
        #             return latest_file[-1]
        #         else:
        #             return "Canceled operation"

        if len(latest_file) == 0:
            return f"No files of word {first_word} in the path {path}"
        return latest_file[-1]
