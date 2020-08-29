# ABC - Automatic Burndown Chart Maker

## What Problem is this Solving?
I had a faced a problem many months ago that I wasn't able to finish my projects at the time that I required them. I would set a due date, but I would always overestimate the amount of work that I had to do, so I would waste more time leading up to the due date

James clear says in his book Atomic Habits, 

>"Many people think they lack motivation when what they really lack is clarity. It is not always obvious when and where to take action" This is the reason why this project was made. 

The automatic burndown chart will give you consistent feedback on how much work is **to be** done, how much work **has** been done, how **fast** you are working and your **expected date of completion**, given how fast you work. If you have this burndown chart update continuously, the feedback will give you clarity on how behind you are, how ahead you are, etc.

### Description
- The program pulls a list of ordered actions, as well as their ETA. Then depending on whether priority of tasks matters, it uses a greedy algorithm to optimize for a 8 hour workday (or however long you work for). Then a scrum-style burndown chart is created (see below) and an expected date of termination will be provided. (in this case it is 2020-07-14)

- This program can also track progress of those tasks by reading a column of "Completed" tasks and superimposing a line graph of current progress. (The red line in the picture)

- This program also has an burndown velocity line that takes the slope of the volume of previous completed tasks, and gives the 'estimated real time of completion'. This can extend past the due date, or before. It is meant to visually show one's progress. (This is the dotted black line)

- **This tool personally helped me achieve deadlines faster because I had it live on a monitor and it would give me continuous feedback.**

![](https://github.com/haseab/ABC/blob/master/image.png)

The x-axis represents the work dates, and the y-axis represents the aggregate hours left in a project


### The Different Classes

- **Datahandler**
  class that is able to 
  - read a table from a file
  - saves updated tasks to csv
  - read the latest saved file without referencing the file directly
  - tracks **any** and **all** changes that are made to the task list

  
- **BurndownChart** 
  class that is able to
  - Create a plan to complete tasks, by sectioning off tasks into day blocks
  - Save the plan to a directory
  - Get the latest plan without referencing file directly
  - Create a visual representation of the plan (burndown chart)
  - Check plan progress
  - Check burndown chart progress (Superimposed line)


### Caution
- In order for this code to work, all generated files must be in the same directory as the .py files
- To see the tables properly, it is recommended to see the outputs on an IDE that can show tables nicely (i.e. Jupyter)

## Example
The following below follows the example.py code, so if you have any issues, refer to that file

### Initial Conditions
To start, you need to choose a few initial conditions:
1. <code>file</code> name. This file should reference the to-do list you use all the time (this can be outsourecd to an app as well). An example of a file name is <code>r"C:\Users\owner\Desktop\sample_todo_list.csv" </code>
2. The max number of hours that you are willing to put in per day. Assign an integer to variable (<code>max_hours</code>)
3. The start date of your project. Assign an string in format "YYYY-MM-DD" to the variable <code>start_date</code>
4. Your to-do list. It should have 4 main columns: <code> ['Completed', 'Task', 'ETA', 'Day']</code>
    - **Completed**: <code>bool</code> - Whether you completed the task or not
    - **Task**     : <code>str</code>  - The task name
    - **ETA**      : <code>int</code>  - The Estimated Time of Completion of the task (use discrete numbers such as 1,2,3,4 etc.) Always overestimate ETA
    - **Day**      : <code>str</code>  - If the task is completed, it should be the date it was completed, if it is not completed, then it will show an empty string 

### Instantiation
After that it is done, just instantiate the two classes
<pre>
bdc = BurndownChart()
dhand = DataHandler()
</pre>

### Reading To-Do List
Now you can start to read the to-do list by using the <code>dhand</code> instance

<pre>
df = dhand.get_tasks_file(file)
</pre>

My to-do list looks like this:

![](https://github.com/haseab/ABC/blob/master/images/Github_todo.png) 


### Checking for Changes
If at any point you need to check changes that were made since the last time you used this program, use the following command

<pre>
dhand.update_tasks(file)
</pre>

If there are no changes you should see <code>Data is identical. No Data changed</code>

However if there **are** changes, then the following example will be seen:

![](https://github.com/haseab/ABC/blob/master/images/Github_datachange.png) 


### Creating/Getting Project Plan
In order to create a plan, you need the to-do-list, <code>df</code> as well as the <code>start_date</code>

<pre>
plan = bdc.see_new_plan(df,start_date)
print(plan)
</pre>

This plan will be a mult-indexed dataframe. It will show exactly what needs to be done each day and how many hours will be left as each task get's completed

An example of the project plan looks like below

![](https://github.com/haseab/ABC/blob/master/images/Github_projectplan.png) 

If you ever needed to get this project plan again, but don't want to go through all of the steps again, just call it using the following code:
<pre>
bdc.get_latest_plan(dhand)
</pre>


### Creating Initial Burndown Chart
The burndown chart just needs one input: the plan. It will read the table and will plot it on a bar graph shown below 
<pre>
bdc.create_burndown_chart(plan)
</pre>

![](https://github.com/haseab/ABC/blob/master/images/Github_bdc.png) 


### Check Progress
After you start to do some work, you will start to mark this as complete on the to-do list, the program will notice this and will update the progress of you project plan, <code> plan </code>
The interesting part is in the graph, a red line will be superimposed onto the previously created burndown chart, showing the progress

<pre>
progress = bdc.check_plan_progress(dhand)
bdc.check_bdc_progress(dhand)
</pre> 

And if you did everything right, the following graph should be shown:


![](https://github.com/haseab/ABC/blob/master/images/Github_bdcprog.png)
