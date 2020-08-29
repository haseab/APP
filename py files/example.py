import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import glob
import os
from burndownchart import BurndownChart
from datahandler import DataHandler



# # Initial Conditions
max_hours = 6  # Determine your own max hours
file = "sample_todo_list.csv"  # Insert your own todolist
start_date = "2020-09-10"  # Determine your own start date
path = os.getcwd() + "\\*" # Getting the path to the current working directory

bdc = BurndownChart(max_hours)
dhand = DataHandler(file)

""" The Following Should only be run for the first run to initialize all files, after that, all you need to really
do is just check your progress with the last two lines"""

# # Getting to-do list table
# df = dhand.get_tasks_file(file)
#
# # Saving current state of to-do list to a .txt file (for future reference)
# dhand.save_data(df)
#
# dhand.update_tasks_to_csv(file)  # First run should say 'Data is identical'
#
# # Creating a project plan from the to-do list
# plan = bdc.see_new_plan(df, start_date)
#
# bdc.save_new_plan(dhand, plan)  # First run: Will ask about saving Proposed plan. Say y/yes/YES
# bdc.get_latest_plan(dhand)  # This retrieves what you just saved
#
# bdc.create_burndown_chart(plan)  # Gives a chart of burndown chart

"""Run The following once you've actually accomplished some tasks"""

progress = bdc.check_plan_progress(dhand)  # First run: Will say no change in progress

bdc.check_bdc_progress(dhand) # First run: Will return same bdc as before
