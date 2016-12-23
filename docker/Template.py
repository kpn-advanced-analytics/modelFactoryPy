
from modelFactoryPy import main
from modelFactoryPy import get
from modelFactoryPy import store
from modelFactoryPy import pull
import numpy as np
import pandas as pd
import random
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
import sys

# ## 1. Get connection; define model_id, get session id
main.getConnection()
model_id = 'titanic_training'
try:
    main.addModelId('titanic_training','Training on titanic data','passengerid')
except:
    pass
main.getSessionId(model_id)

# ## 2. Load the data
df = pd.read_csv('../data/titanic.csv')

# ## 3. Get and store the summary
summary = get.getSummary(df)
store.storeSummary(summary)


# ## 4. Create features matrix, train and test set, build a model on the training set -> predict
y = df['survived_int']
X = df[['sex','pclass','embarked','title','age','family']]
X.index = df["passengerid"].tolist()

def preprocess_features(X):
    
    # Initialize new output DataFrame
    output = pd.DataFrame(index = X.index)

    # Investigate each feature column for the data
    for col, col_data in X.iteritems():

        # If data type is categorical, convert to dummy variables
        if col_data.dtype == object:
            col_data = pd.get_dummies(col_data, prefix = col)  
        
        # Collect the revised columns
        output = output.join(col_data)    
    return output

X = preprocess_features(X)
random.seed(0)
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8,  random_state=0)

clf = RandomForestClassifier(random_state=0) # just a basic random forest model
clf.fit(X_train, y_train)

## predict on the test set:
probs = clf.predict_proba(X_test)
score=[probs[x][1] for x in range(len(probs)) ]

# ## 5. getTestResults; storeTestResults; pull some statistics
test_results = get.getTestResults(score, y_test)
store.storeTestResults(test_results)

threshold_value = 0.5 
threshold_type = "population"
main.updateThreshold(model_id, threshold_value, threshold_type)

# In[44]:

## as we can see, the data is actually stored
pull.pullTestResults(main.session_id).head()

# ## 6. Store the scores
store.storeModelScores(X_test.index, score)

# ## 7. Close the session
main.closeSession()
