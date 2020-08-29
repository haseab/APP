import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import os


class BurndownChart:
    def __init__(self, max_hours):
        self.max_hours = max_hours
        self.path = os.getcwd() + "\\*"  # Getting the path to the current working directory
        self.file = "sample_todo_list.csv"

    def see_new_plan(self, df, start_date, max_hours=None):
        """Algorithm that takes all tasks and breaks them up into different 8 hour days
           The discrete size of these tasks are preserved and are not split into the next day

           The ETA column has a reverse cumulative sum setup so that hours are decreasing with
           every new line

           Parameters:
               max_hours: The maximum number of productive hours in a day
               start_date: The start date of the projects

            Returns:
                data: dataframe of the each task grouped by date
        """
        if max_hours is None:
            max_hours = self.max_hours

        # Filtering only the incomplete tasks
        incomplete_tasks = df[df["Completed"] == False].reset_index(drop=True)[["Day", "Task", "ETA", "Completed"]]
        # Calling algorithm to split the tasks into a day blocks (list of dataframes, one for each day)
        result = self._day_blocks(incomplete_tasks, max_hours)
        # Converting date argument into a datetime object
        date = pd.to_datetime(start_date).to_pydatetime()
        # Creating new DataFrame with initial line to show total sum of hours
        data = pd.DataFrame([["", 0, True, date.strftime('%Y-%m-%d')]], columns=["Task", "ETA", "Completed", "Day"])

        # Converting date_range into a list of strings
        dates = pd.date_range(date, date + timedelta(len(result) - 1)).to_pydatetime()
        dates = [datetime.strftime(i, '%Y-%m-%d') for i in dates]

        # Appending the entire dataset back together, but counting how many tasks were in each day
        count = []
        for i, j in zip(result, range(len(result))):
            count.append(len(i))
            data = data.append(i)

        # Multiplying the dates by how many tasks were in each day
        dates_list = [dates[0]]
        for i, j in zip(dates, range(len(count))):
            dates_list.extend([i] * count[j])

        # Adding list to date column
        data['Day'] = dates_list

        data = data.set_index(["Day", "Task"])
        # Creating Reverse cumulative series on ETA column
        data["Amount Left"] = list(data["ETA"].loc[::-1].cumsum().shift(1).fillna(0))[::-1]
        return data

    def save_new_plan(self, datahandler, plan):
        """
        function 'new_plan' must be run first in order to run this function. This is a wrapper to save it

        Paramaters:
            plan - multi-index dataframe. Obtained from the 'new_plan' output

        Returns:
            str - string explain the filename of saved csv
        """
        start_date = plan.index.levels[0][0]
        # Searching for any file that might have a duplicate name
        new_path = self._get_updated_path(datahandler, "Proposed", plan.index[0][0])
        # Asking if you want to save
        inputs = input(f"File is about to be written as '{new_path}'. OK? (y/n):  ")
        if inputs in ["Y", "y", "yes", "Yes", "YES", "YEs"]:
            plan.reset_index().to_csv(new_path, index=False)
            df = datahandler.get_tasks_file(self.file)
            df.to_csv(f"Progress on Project started on {start_date}.txt", index=False)
            print(f"Saved {new_path} as well as 'Progress on Project started on {start_date}.txt'")
            return plan.reset_index()
        else:
            raise Exception("Canceled operation")

    def get_latest_plan(self, datahandler):
        # Searches for most recently modified file with first word "Proposed"
        new_path = datahandler._get_latest_file("Proposed")
        # loading csv
        original = pd.read_csv(new_path).fillna('')
        # Returning it back in the original form 'see_new_plan' function had
        original = original.groupby(by=["Day", "Task"]).mean()
        # new_path = self._get_updated_path("CSV", start_date)
        #         original.to_csv(f"CSV of Plan on {start_date} v{path[-5]}.csv")
        return original

    def create_burndown_chart(self, data, max_hours=None):
        if max_hours is None:
            max_hours = self.max_hours

        # Setting boundaries of matplotlib chart
        figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
        # x-values are the dates of the 'plan'
        xaxis = np.array(data.index.levels[0])
        # y-values are the cumulative sum of hours under the 'Amount Left' column
        yaxis = [data.loc[i].iloc[0]["Amount Left"] for i in xaxis]
        # labeling x-axis
        plt.xticks(rotation=90)
        # plotting bar graph
        plt.bar(xaxis, yaxis, color='lightgray')
        print(f"Below is the Proposed Plan from {xaxis[0]} to {xaxis[-1]}, Average Velocity: {max_hours} hours per day")
        print(f"Plan Proposed on {str(datetime.now())[:19]}")
        return plt.show()

    def check_plan_progress(self, datahandler):
        """
        Compares the active to do list, with the proposed plan of the project and tracks what tasks have been completed

        Parameter:
            datahandler - instance of DataHandler class

        Returns:
            df3 - dataframe that has a list of updated tasks that are completed

        """
        # Getting previous plan progress dataframe
        dfcompare = pd.read_csv(datahandler._get_latest_file("Proposed")).fillna('')[
            ["Task", "ETA", "Completed", 'Day']].drop(0).reset_index(drop=True)

        # Getting latest to-do list file
        df = datahandler.get_tasks_file(self.file)[["Task", "ETA", "Completed", "Day"]]

        # Filtering only 'completed' tasks to one variable
        dftrue = df[df["Completed"] == True]
        # Getting non-updated to-do list file
        df3 = datahandler.get_latest_tasks_file()[["Task", "ETA", "Completed", "Day"]]

        # Merging both lists to see what has been completed
        df3update = pd.merge(df, dfcompare, how='inner', on='Task').drop(['ETA_y', 'Completed_y'], axis=1)
        df3update = df3update.rename(
            columns={'ETA_x': 'ETA', 'Completed_x': 'Completed', 'Day_x': 'Day', 'Day_y': 'Proposed Day'})

        start_date = pd.read_csv(datahandler._get_latest_file("Proposed")).fillna('').loc[:, 'Day'][0]

        if '' in df3[df3['Completed'] == True]['Day'].values:
            raise Exception("Task marked as true but it does not have a completion date!")

        # Checking if there's no new completed tasks
        if len(df3update) == 0:
            raise Exception("Empty Dataset!")
        else:
            df3update.to_csv(f"Progress on Project started on {start_date}.txt", index=False)
            print("New progress file saved as 'Progress on Project started on 2020-09-10.txt'")
            return df3update

    def check_bdc_progress(self, datahandler):
        """
        This function superimposes a line on top of the original burndown chart to show visual progress

        -------------------------------------------------------------------

        Parameters:
            datahandler - instance of DataHandler class

        Returns:
            tuple - 4 arrays
                x values of bdc
                y values of bdc
                x values of progress line
                y values of progress line

        """
        # Getting progress dataframe
        df = pd.read_csv(datahandler._get_latest_file("Progress")).fillna('').drop('Proposed Day',axis=1)
        df['Day'] = [str(i)[:10] for i in pd.to_datetime(df['Day']).fillna('')]

        if set(df['Day']) == {''}:
            raise Exception('Empty Date of Completion, you have not completed anything yet')

        # Filtering only completed tasks and regrouping
        tasks_comp = df[df["Completed"] == True].groupby(by=["Day", "Task"]).mean()
        start_date = pd.read_csv(datahandler._get_latest_file("Proposed")).fillna('').loc[:, 'Day'][0]
        ######### PREPARING TO GRAPH #############

        # Adding column 'Amount Left' to show reverse cumulative sum of the tasks.
        tasks_comp["Amount Left"] = np.array(list(tasks_comp["ETA"].loc[::-1].cumsum().shift(1).fillna(0))[::-1])
        # Getting Proposed plan to see how the original burndown chart looked like
        export = pd.read_csv(datahandler._get_latest_file("Proposed")).fillna('').set_index(["Day", "Task"])
        # Adjusting all reverse cumulative sum values of 'tasks_comp' so it matches that of the proposed plan
        tasks_comp["Amount Left"] += export["ETA"].sum() - tasks_comp.iloc[0]["Amount Left"]

        ########### GRAPHING DATA ####################

        # Grabbing the dates of the plan on the burndown chart
        xaxis = [i.strftime("%Y-%m-%d") for i in pd.date_range(export.index.levels[0][0], export.index.levels[0][-1])]

        # y-axis values: Placeholder used to get the same work remaining if theres a day that has no assigned work
        yaxis = []
        placeholder = 0
        for i in xaxis:
            if i not in export.index.levels[0]:
                yaxis.append(placeholder)
            else:
                placeholder = export.loc[i, 'Amount Left'][0]
                yaxis.append(placeholder)

        # Setting x values of the completion line
        newXaxis = tasks_comp.index.levels[0].values

        # Getting corresponding y-values of line from x values
        newYaxis = [tasks_comp.loc[i].loc[:, 'Amount Left'][-1] for i in tasks_comp.index.levels[0].values]

        # Fitting the line according to the day the first task was completed
        ##Setting Datetimes of the line x values and of the start date
        xdatetime = [datetime.strptime(i, "%Y-%m-%d") for i in list(newXaxis)]
        startdatetime = datetime.strptime(start_date, "%Y-%m-%d")
        ##Getting how many days after starting date tasks got completed
        shift = (min(xdatetime) - startdatetime).days
        ##Getting total time since the start date
        ranged = (max(xdatetime) - min(xdatetime)).days

        # Converting x values (which were dates (str)) into numerical values
        numx = np.array(xdatetime) - xdatetime[0] + timedelta(days=shift)
        numx = [i.days for i in numx]

        # Start plotting

        ##Creating Burndown velocity: the line of best fit of all data points so far
        c = np.polyfit(numx, newYaxis, 1)
        x1 = np.array(range(ranged + shift, len(xaxis)))
        line = c[0] * x1 + c[1]

        # Plotting
        ##Determing window size of matplotlib
        fig = plt.figure(num=None, figsize=(10, 6), dpi=80, facecolor='w', edgecolor='k')
        plt.ylim(0, max(yaxis) + 10)
        plt.xticks(rotation=90, figure=fig)
        plt.bar(xaxis, yaxis, color='lightgray', figure=fig)
        plt.plot(newXaxis, newYaxis, linewidth=5, color="red", figure=fig)
        plt.plot(x1, line, color='black', linewidth=3, linestyle=':', figure=fig)
        # plt.plot(numx,newYaxis,'o', color='red', markersize =10)

        # Feedback on progess
        print(f"Below is the Current Progress for the dates {xaxis[0]} to {xaxis[-1]}")
        if newYaxis[len(newYaxis) - 1] < yaxis[len(newYaxis) - 1]:
            print(f"Good job!! You're ahead of schedule!")
        elif len(newYaxis) == 0:
            print("No data recorded yet!")
        elif newYaxis[len(newYaxis) - 1] == yaxis[len(newYaxis) - 1]:
            print("Right on time! Keep it up")
        else:
            print("We're behind! We have to work faster!")

        plt.show()

    def _day_blocks(self, df, max_hours=None):
        """
        Algorithm that takes tasks and fits them in an 8 hour workday. Tasks that do not fit are swapped with
        tasks that can be completed that day.

        Parameters:
            df - dataframe that needs splitting. Note that this dataframe must have a column called ['ETA']
            max_hours - max hours in a workweek

        Returns:
            lst2 - list of dataframes of tasks, one for each day
        """
        if max_hours is None:
            max_hours = self.max_hours

        lst2 = []
        freeze = 0
        a = df["ETA"]
        for i in range(len(a) + 1):
            df2 = df["ETA"].iloc
            ##Checking to see if the cumulative hours in a day surpasses the max
            if df2[freeze:i].sum() > max_hours:
                increment = 0
                ##Checking if the next element will be under the max hours
                if df2[freeze:i + increment + 1].drop(i - 1).sum() < max_hours:
                    ##Keeps adding tasks until it surpasses the max
                    while df2[freeze:i + increment + 1].drop(i - 1).sum() < max_hours:
                        check = df2[freeze:i + increment + 1].drop(i - 1)
                        increment += 1
                        if check.equals(df2[freeze:i + increment + 1].drop(i - 1)):
                            break
                    temp = df.iloc[i - 1]
                    ##Reorganizing the dataframe so that the block that was skipped gets added to the next set of data
                    df.iloc[i - 1:i + increment + 1] = df.iloc[i - 1:i + increment + 1].shift(-1).fillna(temp)
                    # print(df.iloc[i-1:i+increment+1])
                    ##Adding the entire set of tasks within the hour limit to a list
                    lst2.append(df.iloc[freeze:i + increment - 1])
                    freeze = i + increment - 1
                else:
                    lst2.append(df.iloc[freeze:i - 1])
                    freeze = i - 1
        ##Add the remaining tasks to the end of the list
        lst2.append(df.iloc[freeze:])
        return lst2

    def _get_updated_path(self, datahandler, first_word, start_date, path=None):
        """This function is used to make sure that naming is not duplicated. It searches for the last file
        that has the same name and increments the name by a value (v1, v2, ..) in order to avoid duplicates

        Parameters:
            datahandler - instance of DataHandler class
            start_date - start date
            path - The directory to be looking at

        Returns:
            str - If conditions are satisfied, it returns a string with a non-duplicate file name
        """
        if path is None:
            path = self.path

        # Get most recent file
        paths = datahandler._get_latest_file(first_word, path)

        # Looking for version number (v1,v2,v3)
        if paths.split(' ')[:2] == ['No', 'files']:
            print(f"Saving File as Proposed plan starting {start_date} v1.txt")
            return f"Proposed plan starting {start_date} v1.txt"
        if paths[-7:-5] != " v":
            return "There is an issue with naming the file. There is no version label (vx)"
        if paths[-4:] == ".txt":
            extension = ".txt"
        if paths[-4:] == ".csv":
            extension = ".csv"

        # Checking if dates are up to date
        assert len(
            pd.Series([i if str(datetime.now().year) in i else "Invalid" for i in paths.split(' ')]).drop_duplicates(
                keep=False)) != 0, "Invalid Date Time on file"
        file_date = pd.Series(
            [i if str(datetime.now().year) in i else "Invalid" for i in paths.split(' ')]).drop_duplicates(keep=False)

        # Getting position of file in series as well as the date on the name of the file
        position, file_date = file_date.index[0], file_date.values[0]

        # Turning date of file into a datetime object. Creating a datetime object out of the start_date too
        file_datetime = datetime.strptime(file_date, "%Y-%m-%d")
        start_datetime = pd.to_datetime(start_date).to_pydatetime()

        # If the dates are the same, increment the version by 1
        if start_datetime == file_datetime:
            newpaths = paths[:-5] + str(int(paths[-5]) + 1) + extension
            return newpaths
        # If the start date is after, create a new file name with version 1 (v1)
        elif start_datetime > file_datetime:
            pathslst = paths.split(' ')
            pathslst[position] = start_date
            pathslst[-1] = "v1" + extension
            newpaths = ' '.join(pathslst)
            return newpaths
        elif start_datetime < file_datetime:
            return "There is apparently a more recent proposed plan"