# Just reading in Daylio data for now

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

import seaborn as sns
from matplotlib import pyplot as plt

sns.set()
sns.set_context("poster")


mood_map = {
    'Love': 5,
    'Excited': 5,
    'Motivated': 5,
    'Content': 4,
    'Happy': 4,
    'Unmotivated': 3,
    'Bored': 3,
    'Anxious': 2,
    'Tired': 2,
    'Frustrated': 1,
    'Overwhelmed': 1,
    'Pissed': 1
}

drop_activities = ['clean']

daylio_export_file = 'data/daylio_export.csv'


# Main
data = pd.read_csv(daylio_export_file)[::-1]

# Fix date column and drop year and notes
data['date'] = pd.to_datetime(data['date'] + ' ' + data['year'].astype(str) + ' ' + data['time'])
data.drop(['year', 'note', 'time'], inplace=True, axis=1)

# Set index as date
data.set_index('date', inplace=True)
data.columns = ['weekday', 'mood_str', 'activities']


# One-hot for activities
for idx in data.index:
    acts = data.loc[idx].activities.split(' | ')
    if type(acts) == str:
        acts = [acts]
    for x in acts:
        x = x.replace(' ', '_')
        # Create new columns for activities
        if x not in data.columns:
            data[x] = 0

        # Add flag for feature
        data.set_value(idx, x, 1)

# Add DayofWeek
#data['day_of_week'] = data.index.dayofweek


# Mood mapping
data['mood'] = data.mood_str.map(mood_map)


# Model fitting
X = data.drop(['weekday', 'mood_str', 'mood', 'activities'] + drop_activities, axis=1)
model = LinearRegression()
model.fit(X, data.mood)

coefs = []  # [['intercept', model.intercept_]]
for x,y in zip(X.columns, model.coef_):
    coefs.append([x, y])

coefs = np.array(coefs)
coefs = coefs[coefs[:, 1].astype(float).argsort()[::-1]]

plt.figure()
sns.barplot(np.arange(len(coefs)), coefs[:, 1].astype(float))
plt.xticks(np.arange(len(coefs))-.3, coefs[:, 0], rotation=35)
plt.axhline(0, c='black')

plt.title('Baseline mood: {:.2f}'.format(model.intercept_))
plt.ylabel('Impact on Mood')
plt.xlabel('Activity')

plt.tight_layout()
plt.savefig('data/fig.png')
plt.show()

