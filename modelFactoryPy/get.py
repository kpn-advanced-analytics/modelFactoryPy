
import sqlalchemy
import pandas as pd
import numpy as np
import main


def getSummary(df):
    n_na = []
    a = df.describe().transpose()[["mean","std","50%","min","max","count"]]
    a = a.rename(columns = {'std':'sd','50%':'median','count':'n'})
    for i in a.index:
        n_na.append(len(df[i])-df[i].count())
    a["n_na"] = n_na
    a["n"] = a["n"].apply(lambda x: int(x))
    a["variable"] = a.index
    return a.reset_index(drop = True)


def getTestResults(scores,labels):
    a = pd.DataFrame(zip(scores,labels),columns=['score','label'])
    a = a.sort('score', ascending = 0)
    a = a.reset_index(drop = True)
    a["population"]=(a.index+1)/float(len(a))
    a["target_population"] = np.cumsum(a["label"])/sum(a["label"])
    a["true_positives"] = np.cumsum(a["label"])
    a["false_positives"] = a.index+1 - a["true_positives"]
    a["true_negatives"] = len(a) - sum(a["label"]) - a["false_positives"]
    a["false_negatives"] = sum(a["label"]) - np.cumsum(a["label"])
    return a


def getROC(scores,labels):
    tr = getTestResults(scores,labels)
    tr["true_positive_rate"] = (tr["true_positives"])/(tr["true_positives"]+tr["false_negatives"])
    tr["false_positive_rate"] = (tr["false_positives"])/(tr["false_positives"]+tr["true_negatives"])
    roc_line = tr[["population","true_positive_rate","false_positive_rate"]]
    return roc_line


def getLiftChart(scores,labels):
    tr = getTestResults(scores,labels)
    lift_chart = tr[["population","target_population"]]
    return lift_chart


def getConfMatrix(scores, labels, threshold_value, threshold_type):
    tr = getTestResults(scores,labels)
    if threshold_type == "population":
        tr = tr[tr.population <= threshold_value].tail(1)
    if threshold_type == "probability":
        tr = tr[tr.score >= threshold_value].tail(1)
    conf_m = pd.DataFrame(zip(tr.true_positives.tolist()+tr.false_positives.tolist(),
                              tr.false_negatives.tolist()+tr.true_negatives.tolist()),
                          columns = ['predicted_positives','predicted_negatives'])
    conf_m.index = ['actual_positives','actual_negatives']
    return conf_m


def getAccuracy(scores, labels, threshold_value, threshold_type):
    tr = getTestResults(scores,labels)
    if threshold_type == "population":
        tr1 = tr[tr.population <= threshold_value].tail(1)
    if threshold_type == "probability":
        tr1 = tr[tr.score >= threshold_value].tail(1)
    accuracy = float(tr1["true_positives"]+tr1["true_negatives"])/len(tr)
    return accuracy
