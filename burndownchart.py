import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure


class BurndownChart():
    def new_plan(self, df, max_hours, start_date):
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
        # Filtering only the incomplete tasks
        incompleteTasks = df[df["Completed"] == False].reset_index(drop=True)[["Day", "Task", "ETA", "Completed"]]
        # Calling algorithm to split the tasks into a day blocks (list of dataframes, one for each day)
        result = self._day_blocks(incompleteTasks, max_hours)
        # Converting date argument into a datetime object
        date = pd.to_datetime(start_date).to_pydatetime()
        # Creating new DataFrame with initial line to show total sum of hours
        data = pd.DataFrame([["", 0, True, date.strftime('%Y-%m-%d')]], columns=["Task", "ETA", "Completed", "Day"])
        # Iterating through the list of dataframes and adding consecutive days after the start date
        for i, j in zip(result, range(len(result))):
            i.loc[:, "Day"] = [(date + timedelta(days=j)).strftime('%Y-%m-%d')] * len(i)
            data = data.append(i)
        data = data.set_index(["Day", "Task"])
        # Creating Reverse cumulative series on ETA column
        data["Amount Left"] = list(data["ETA"].loc[::-1].cumsum().shift(1).fillna(0))[::-1]
        return data

    def update_plan(self, max_hours, start_date, current_date=str(datetime.today().date() + timedelta(days=1))):

        path = self._get_latest_file("Proposed")
        original = pd.read_csv(path).fillna('')
        original["Day"] = pd.to_datetime(original["Day"])
        original = original[original["Day"] < current_date]
        original["Day"] = [i.strftime("%Y-%m-%d") for i in original["Day"]]
        original = original.set_index('Task').drop("Amount Left", axis=1)

        df = self.get_tasks().fillna('').set_index('Task')

        for i in df.index:
            if i in original.index:
                df = df.drop(i)
        original = original.reset_index()
        df = df.reset_index()

        new = self.new_plan(df, max_hours, current_date).reset_index().drop("Amount Left", axis=1)[1:]

        original2 = original.append(new).reset_index(drop=True)
        original2 = original2.set_index(["Day", "Task"])[["ETA", "Completed"]]
        original2["Amount Left"] = list(original2["ETA"].loc[::-1].cumsum().shift(1).fillna(0))[::-1]

        newpath = self._get_updated_path("Proposed", start_date)
        inputs = input(f"File is about to be written to {newpath}. OK? (y/n):  ")
        if inputs in ["Y", "y", "yes", "Yes", "YES", "YEs"]:
            export = original2.reset_index().to_csv(newpath, index=False)
            return original2
        else:
            return "Canceled operation"
        export = original2.reset_index().to_csv(newpath, index=False)
        return original2

    def get_plan(self, instance, start_date):
        path = instance._get_latest_file("Proposed")
        original = pd.read_csv(path).fillna('')
        original = original.groupby(by=["Day", "Task"]).mean()
        # newpath = self._get_updated_path("CSV", start_date)
        original.to_csv(f"CSV of Plan on {start_date} v{path[-5]}.csv")
        return original

    def create_burndown_chart(self, data, max_hours=8, start_date=datetime.now().strftime("%Y-%m-%d")):
        figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
        xaxis = np.array(data.index.levels[0])
        yaxis = [data.loc[i].iloc[0]["Amount Left"] for i in xaxis]
        plt.xticks(rotation=90)
        plt.bar(xaxis, yaxis)
        print(f"Below is the Proposed Plan from {xaxis[0]} to {xaxis[-1]}, Average Velocity: {max_hours} hours per day")
        print(f"Plan Proposed on {str(datetime.now())[:19]}")
        # Creating CSV Compatible Data
        lst = [[i, j] for i, j in zip(xaxis, yaxis)]
        # export = pd.DataFrame(lst, columns = ["X-axis","Y-axis"]).to_csv(f"bdc data plan on {start_date} {str(time.time())[-3:-1]}.csv", index=False)
        return (xaxis, yaxis)

    def check_progress_bdc(self, start_date):
        # Pulling both completed tasks and previous task list
        # Checking what got completed and categorizing the changes

        df = self.update_tasks()[0]
        dffalse = df[df["Completed"] == False][["Task", "ETA", "Completed", "Day"]]
        df2 = df[df["Completed"] == True][["Task", "ETA", "Completed", "Day"]]
        df3 = self.get_tasks()[["Task", "ETA", "Completed", "Day"]]
        df2 = df2.set_index("Task")
        df3 = df3.set_index("Task")

        for i in df3.index:
            if i in df2.index:
                df3.loc[i, "Completed"] = True
                df3.loc[i, "Day"] = df2.loc[i, "Day"]

        df3.reset_index()
        tasks_left = df3[df3["Completed"] == False].reset_index().groupby(by=["Day", "Task"]).mean()
        df3 = df3[df3["Completed"] == True]

        df3["Day"] = pd.to_datetime(df3["Day"]).fillna('')
        date = datetime.strptime(start_date, "%Y-%m-%d")

        df3 = df3[df3["Day"] >= date]
        df3["Day"] = [i.strftime("%Y-%m-%d") for i in df3["Day"]]

        if len(df3) == 0:
            raise Exception("Empty Dataset!")
        df3 = df3.reset_index().groupby(by=["Day", "Task"]).mean()

        df3["Amount Left"] = np.array(list(df3["ETA"].loc[::-1].cumsum().shift(1).fillna(0))[::-1])

        export = pd.read_csv(self._get_latest_file("Proposed")).fillna('').set_index(["Day", "Task"])

        df3["Amount Left"] += export["ETA"].sum() - df3.iloc[0]["Amount Left"]

        figure(num=None, figsize=(18, 6), dpi=80, facecolor='w', edgecolor='k')

        xaxis = [i.strftime("%Y-%m-%d") for i in pd.date_range(export.index.levels[0][0], export.index.levels[0][-1])]

        yaxis = []
        placeholder = 0
        for i in xaxis:
            if i not in export.index.levels[0]:
                yaxis.append(placeholder)
            else:
                placeholder = export.loc[i].iloc[0]["Amount Left"]
                yaxis.append(placeholder)

        # yaxis = [export.loc[i].iloc[0]["Amount Left"] for i in xaxis]
        newXaxis = df3.index.levels[0].values

        # Fitting the line according to the day the first task was completed
        xdatetime = [datetime.strptime(i, "%Y-%m-%d") for i in list(newXaxis)]
        startdatetime = datetime.strptime(start_date, "%Y-%m-%d")
        shift = (min(xdatetime) - startdatetime).days
        ranged = (max(xdatetime) - min(xdatetime)).days

        numx = np.array(xdatetime) - xdatetime[0] + timedelta(days=shift)
        numx = [i.days for i in numx]
        newYaxis = [df3.loc[i].iloc[-1]["Amount Left"] for i in newXaxis]

        # Start plotting
        plt.ylim(0, max(yaxis) + 10)
        c = np.polyfit(numx, newYaxis, 1)
        x1 = np.array(range(ranged + shift, len(xaxis)))
        line = c[0] * x1 + c[1]

        plt.xticks(rotation=90)
        plt.bar(xaxis, yaxis, color='lightgray')
        plt.plot(newXaxis, newYaxis, linewidth=5, color="red")
        plt.plot(x1, line, color='black', linewidth=3, linestyle=':')
        # plt.plot(numx,newYaxis,'o', color='red', markersize =10)

        print(f"Below is the Current Progress for the dates {xaxis[0]} to {xaxis[-1]}")
        if newYaxis[len(newYaxis) - 1] < yaxis[len(newYaxis) - 1]:
            print(f"Good job!! You're ahead of schedule!")
        elif len(newYaxis) == 0:
            print("No data recorded yet!")
        elif newYaxis[len(newYaxis) - 1] == yaxis[len(newYaxis) - 1]:
            print("Right on time! Keep it up")
        else:
            print("We're behind! We have to work faster!")
        return (newXaxis, newYaxis, tasks_left)

    def _day_blocks(self, df, max_hours=8):
        lst2 = []
        freeze = 0
        a = df["ETA"]
        for i in range(len(a) + 1):
            df2 = df["ETA"].iloc
            if df2[freeze:i].sum() > max_hours:
                increment = 0
                if df2[freeze:i + increment + 1].drop(i - 1).sum() < max_hours:
                    while df2[freeze:i + increment + 1].drop(i - 1).sum() < max_hours:
                        check = df2[freeze:i + increment + 1].drop(i - 1)
                        increment += 1
                        if check.equals(df2[freeze:i + increment + 1].drop(i - 1)):
                            break
                    temp = df.iloc[i - 1]
                    df.iloc[i - 1:i + increment + 1] = df.iloc[i - 1:i + increment + 1].shift(-1).fillna(temp)
                    # print(df.iloc[i-1:i+increment+1])
                    lst2.append(df.iloc[freeze:i + increment - 1])
                    freeze = i + increment - 1
                else:
                    lst2.append(df.iloc[freeze:i - 1])
                    freeze = i - 1
        lst2.append(df.iloc[freeze:])
        return lst2

    def _get_updated_path(self, first_word, start_date, path='/Users/owner/Desktop/Datasets/TaskIntegrator/*'):
        """When making new copies of """
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