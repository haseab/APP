# ABC
ABC - Automatic Burndown Chart

### What is this Code about?
- The main purpose of this program is to be used as a project planner. Please refer to the image below as a reference

- The program pulls a list of ordered actions, as well as their ETA. Then depending on whether priority of tasks matters, it uses a greedy algorithm to optimize for a 8 hour workday (or however long you work for). Then a scrum-style burndown chart is created (see below) and an expected date of termination will be provided. (in this case it is 2020-07-14)

- This program can also track progress of those tasks by reading a column of "Completed" tasks and superimposing a line graph of current progress. (The red line in the picture)

- This program also has an burndown velocity line that takes the slope of the volume of previous completed tasks, and gives the 'estimated real time of completion'. This can extend past the due date, or before. It is meant to visually show one's progress. (This is the dotted black line)

- **This tool personally helped me achieve deadlines faster because I had it live on a monitor and it would give me continuous feedback.**

![](https://github.com/haseab/ABC/blob/master/image.png)

The x-axis represents the work dates, and the y-axis represents the aggregate hours left in a project


### The Different Classes

- **Datahandler** - class that is able to read data, save data, check for changes in data, etc.
- **BurndownChart** - class that creates a day by day plan of tasks to do, as well as creates a burndown chart, as well as updates the burndown chart


## Example
