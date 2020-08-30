### Problems with BDC Code:
1.  [x] The start time is behind the completed tasks (so you can't filter properly)
2.  [x] I completed a task out of order, lets see what happens
3.  [x] bdc is flawed, it doesn't show the last bar
4.  [x] bdc line is not giving the right slope
5.  [ ] bdc.check_plan progess is not consistent
6.  [ ] dhand.update_tasks changes the df orientation for no reason
7.  [x] dhand.update_tasks_to_csv gives some next data changing
8.  [x] Fix date issue ("2020-05-10) vs 5/10/2020
9.  [x] bdc.see_new_plan has some warnings for pandas
11.  [x] Make sure path automatically updates with whatever location they are in
12.  [x] finish example.py
13.  [ ] Make sure outputs have spaces so you can read it properly
14.  [x] How to fix variables that need to be defined in the module
15.  [x] Have good PEP 8 Styling
16.  [ ] Progress file has DD/MM/YYYY format and not YYYY-MM-DD
17.  [ ] proposed plans should be compared before a new one is made (for the sake of redundancy)

### Ideas:
1. [ ] add option where the order of tasks is restricted so you cant swap
2. [ ] add option where tasks spill into the next day
3. [ ] allow the updating of a current burndown chart, in case more tasks are added in a given day
4. [ ] decorators for saving data?
5. [ ] make strptimes completely flexilbe and not rigid (so you can pass in anything without error)
