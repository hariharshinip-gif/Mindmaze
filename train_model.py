import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import pickle

# Generate sample PHQ9 dataset
data = []

for i in range(500):
    responses = np.random.randint(0,4,9)
    score = responses.sum()

    if score <= 4:
        label = "Minimal"
    elif score <= 9:
        label = "Mild"
    elif score <= 14:
        label = "Moderate"
    elif score <= 19:
        label = "Moderately Severe"
    else:
        label = "Severe"

    row = list(responses) + [label]
    data.append(row)

columns = ["q1","q2","q3","q4","q5","q6","q7","q8","q9","label"]

df = pd.DataFrame(data,columns=columns)

X = df.drop("label",axis=1)
y = df["label"]

model = DecisionTreeClassifier()
model.fit(X,y)

pickle.dump(model,open("model.pkl","wb"))

print("Model trained and saved!")