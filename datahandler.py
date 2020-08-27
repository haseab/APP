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
        dt = datetime.now()
        file = f"Tasks {dt.year}_{dt.month}_{dt.day}_{dt.hour}.txt"
        df.to_csv(file, index=False)
        string = "Saved Data as: " + file
        self.file = file
        print(string)
        return file

    def get_tasks_file(self, file=None):
        if file == None:
            print("Please indicate the file location!")
            return None
        df = pd.read_csv(file)
        df["Completed"] = [True if i == "Yes" else False for i in df["Completed"]]
        df = pd.concat([df[df["Completed"] == True], df[df["Completed"] == False]]).reset_index(drop=True)
        return df

    def get_latest_tasks_file(self, file=None):
        file = self._get_latest_file("Tasks")
        df = pd.read_csv(file)
        return df

    def update_tasks(self, file=None):
        if file == None:
            print("Please enter the file you want for updates")
            return None
        df = self.get_latest_tasks_file().fillna('')
        ndf = self.get_tasks_file(file)
        df2 = df.set_index("Task")
        ndf2 = ndf.set_index("Task")
        totalcount, counter2 = 0, 0

        # Dataframes without task as index
        dftrue = df2[df2["Completed"] == True]
        ndftrue = ndf2[ndf2["Completed"] == True]
        dffalse = df2[df2["Completed"] == False]
        ndffalse = ndf2[ndf2["Completed"] == False]

        # Dataframes with task as index

        for i in dffalse.index:
            if i not in ndffalse.index and i in ndftrue.index:
                print(f"Task Completed: {i}")
                counter2 += 1
            if i not in ndffalse.index and i not in ndftrue.index:
                print(f"Task Removed from To-Do: {i}")
                counter2 += 1

        for i in dftrue.index:
            if i not in ndftrue.index and i in ndffalse.index:
                print(f"Task Uncompleted: {i}")
                counter2 += 1
            if i not in ndffalse.index and i not in ndftrue.index:
                print(f"Task Removed from Completed: {i}")
                counter2 += 1

        for i in ndffalse.index:
            if i not in dffalse.index and i not in dftrue.index:
                print(f"Task added to to-do list: {i}")
                counter2 += 1
        for i in ndftrue.index:
            if i not in dffalse.index and i not in dftrue.index:
                print(f"Task added to completed without being on to-do list: {i}")
                counter2 += 1

        taskdf, counter = self._data_change_tracker(df, ndf)

        totalcount = counter + counter2
        if totalcount == 0:
            print("\nNothing happened")
            return df, 1
        else:
            inputs = input("Are you sure you want to continue with the above changes? y/n")
            if inputs in ["Y", "y", "yes", "Yes", "YES", "YEs"]:
                print("Items added to new list!")
                # Resetting indices
                dftrue = dftrue.reset_index()
                ndftrue = ndftrue.reset_index()
                dffalse = dffalse.reset_index()
                ndffalse = ndffalse.reset_index()

                df3 = ndffalse.merge(ndftrue, how="outer").reset_index(drop=True).drop_duplicates(subset="Task")
                return df3, 0

            else:
                print("Returning original dataset")
                return df, 1

    def update_tasks_to_csv(self, file=None):
        df, count = self.update_tasks(file)
        if count == 1:
            print("Nothing was saved")
            return None
        text = self.save_data(df)
        return df, count

    def _data_change_tracker(self, df, ndf):
        if "Completed_x" in df.columns:
            taskdf = df.merge(ndf, how="inner", on="Task").set_index("Task").drop(["Completed_x", "Completed_y", "Score_x", "Score_y"], axis=1)
        else:
            taskdf = df.merge(ndf, how="inner", on="Task").set_index("Task")
        col = taskdf.columns.values
        counter = 0
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
        list_of_files = glob.iglob(path)  # * means all if need specific format then *.csv
        latest_file = sorted(list_of_files, key=os.path.getctime)
        latest_file = [i.split("\\")[1] for i in latest_file]
        latest_file = [i for i in latest_file if i.split()[0] == first_word]
        #         inputs = input(f"File read was {latest_file[-1]}. Proceed? (y/n): ")
        #         if inputs in ["Y","y","yes","Yes","YES", "YEs"]:
        #             return latest_file[-1]
        #         else:
        #             return "Canceled operation"

        if len(latest_file) == 0:
            return f"No files of word {first_word} in the path {path}"
        return latest_file[-1]

    def _get_updated_path(self, first_word, start_date, path='/Users/owner/Desktop/Datasets/TaskIntegrator/*'):
        # Get proper naming
        paths = self._get_latest_file("Proposed", path)

        if paths[-7:-5] != " v":
            return "There is an issue with naming the file. There is no version label (vx)"
        if paths[-4:] == ".txt":
            extension = ".txt"
        if paths[-4:] == ".csv":
            extension = ".csv"

        assert len(
            pd.Series([i if str(datetime.now().year) in i else "Invalid" for i in paths.split(' ')]).drop_duplicates(
                keep=False)) != 0, "Invalid Date Time on file"
        file_date = pd.Series(
            [i if str(datetime.now().year) in i else "Invalid" for i in paths.split(' ')]).drop_duplicates(keep=False)

        position, file_date = file_date.index[0], file_date.values[0]

        file_datetime = datetime.strptime(file_date, "%Y-%m-%d")
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")

        if start_datetime == file_datetime:
            newpaths = paths[:-5] + str(int(paths[-5]) + 1) + extension
            return newpaths
        elif start_datetime > file_datetime:
            pathslst = paths.split(' ')
            pathslst[position] = start_date
            pathslst[-1] = "v1" + extension
            newpaths = ' '.join(pathslst)
            return newpaths
        elif start_datetime < file_datetime:
            return "There is apparently a more recent proposed plan"



