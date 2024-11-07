# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 17:42:58 2024

@author: jmitchell
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt; plt.close('all')
import datetime

board = 'ITCC'

# path of JIRA export file
file_path = f'C:\\Users\\jmitchell\\Downloads\\{board} All Tickets (Jira).csv'

# read in the data frame, change the format of dates and order by date created
df = pd.read_csv(file_path); keys = df.keys()
df['Created'] = pd.to_datetime(df['Created'], format='%d/%b/%y %I:%M %p')
df['Status Category Changed'] = pd.to_datetime(df['Status Category Changed'], format='%d/%b/%y %I:%M %p')
df = df.sort_values(by='Created')

# filtered dfs
df_backlog = df[df['Status'] == 'Backlog']
df_done = df[df['Status'] == 'Done']
df_on_board = df[df['Status'] != 'Backlog']; df_on_board = df_on_board[df_on_board['Status'] != 'Done']

## 1: story points completed over time
# oder done by change date to look at completion
df_done = df_done.sort_values(by='Status Category Changed')
resources = list(set(df_done['Assignee'])); print(resources)
# df_done = df_done[df_done['Assignee'] == 'Oliver Chappell-Holmes']
x = df_done['Status Category Changed']
y = df_done['Custom field (Story Points)']

# remove nan values and interpolate (1D)
y_value_indexes = np.where(~np.isnan(y))[0]
t = np.array(x)[y_value_indexes]
y_values = np.array(y)[y_value_indexes]

t_ints = ((t - np.datetime64('1970-01-01')) / np.timedelta64(1, 's')).astype(int)
coefficients = np.polyfit(t_ints, np.cumsum(y_values), 1)
p = np.poly1d(coefficients)
y_fit = p(t_ints)
gradient = round(coefficients[0]*60*60*24*30.437/(260/12),2)

# plot
plt.figure(figsize=(10,6))
plt.plot(t, np.cumsum(y_values), 'ks-')
plt.plot(t, y_fit, 'r--')

plt.ylabel('Date')
plt.ylabel('Story Points Completed')
plt.title(f'{board}: Completed')
text = plt.text(t[int(len(t)/20)], y_fit[int(19*len(y_fit)/20)], f'SPs/day = {gradient}')
text.set_bbox(dict(facecolor='white', alpha=1.0, edgecolor='k'))

plt.grid()

# single person plots
df_done_oli = df_done[df_done['Assignee'] == 'Oliver Chappell-Holmes']
x = df_done_oli['Status Category Changed']
y = df_done_oli['Custom field (Story Points)']

# remove nan values and interpolate (1D)
y_value_indexes = np.where(~np.isnan(y))[0]
t = np.array(x)[y_value_indexes]
y_values = np.array(y)[y_value_indexes]
plt.plot(t, np.cumsum(y_values), '-', label='Oli')

df_done_karen = df_done[df_done['Assignee'] == 'Karen McGaul']
x = df_done_karen['Status Category Changed']
y = df_done_karen['Custom field (Story Points)']

# remove nan values and interpolate (1D)
y_value_indexes = np.where(~np.isnan(y))[0]
t = np.array(x)[y_value_indexes]
y_values = np.array(y)[y_value_indexes]
plt.plot(t, np.cumsum(y_values), '-', label='Karen')
plt.legend()

## 2: burn down
person_efficiency = 0.8
story_points_backlog_sum = np.sum(df_backlog['Custom field (Story Points)'])
resources = 2
days_to_complete = (story_points_backlog_sum/(person_efficiency*(5/7)))/resources
final_date = datetime.datetime.today() + datetime.timedelta(days = days_to_complete)
t = pd.date_range(
    start = datetime.datetime.today(),
    end = final_date,
    periods=2
)

# plot
plt.figure(figsize=(10,6))
plt.axhline(y=story_points_backlog_sum, color='k', linestyle='--', linewidth=2.0)

plt.plot([t[0], t[-1]], [0, story_points_backlog_sum], 'b-', linewidth=2.0, label = 'nomional (resource=2)')

resources = 3
days_to_complete = (story_points_backlog_sum/(person_efficiency*(5/7)))/resources
final_date = datetime.datetime.today() + datetime.timedelta(days = days_to_complete)
t = pd.date_range(
    start = datetime.datetime.today(),
    end = final_date,
    periods=2
)
plt.plot([t[0], t[-1]], [0, story_points_backlog_sum], 'g-', linewidth=2.0, label = 'accelerated (resource=3)')
first_day_of_current_month = datetime.datetime.today().replace(day=1) + datetime.timedelta(days = -1)
plt.xlim([first_day_of_current_month, first_day_of_current_month + datetime.timedelta(days = 12*31)])

person_efficiency = 0.95/2
resources = 2
days_to_complete = (story_points_backlog_sum/(person_efficiency*(5/7)))/resources
final_date = datetime.datetime.today() + datetime.timedelta(days = days_to_complete)
t = pd.date_range(
    start = datetime.datetime.today(),
    end = final_date,
    periods=2
)
plt.plot([t[0], t[-1]], [0, story_points_backlog_sum], 'r-', linewidth=2.0, label = 'measured efficiency')
first_day_of_current_month = datetime.datetime.today().replace(day=1) + datetime.timedelta(days = -1)
plt.xlim([first_day_of_current_month, first_day_of_current_month + datetime.timedelta(days = 12*31)])

plt.ylabel('Date')
plt.ylabel('Backlog Story Points')
plt.title(f'{board}: Burn-down')

plt.legend(loc='lower right')
plt.grid()

# pies
plt.figure()
resources = list(set(df_on_board['Assignee']))
status_values = list(set(df_on_board['Status']))
df_filter = df_on_board[df_on_board['Assignee']== resources[3]]

ticket_no_log = []
for status in status_values:
    df_filter_status = df_filter[df_filter['Status']==status]
    ticket_no_log.append(len(df_filter_status['Custom field (Story Points)']))
    
plt.pie(ticket_no_log, labels=status_values)
plt.title(f'{resources[3]}')
