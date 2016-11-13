
import sqlalchemy
import pandas as pd
from main import *

def pullSummary(session_id):
    if type(session_id) == list:
        session_id = str(session_id).replace('[','').replace(']','')
        check_session_id = pd.read_sql("select * from model_factory.model_summary where session_id in ("+session_id+")", engine)
    if type(session_id) == str:
        check_session_id = pd.read_sql("select * from model_factory.model_summary where session_id in ('"+session_id+"')", engine)
    else:
        raise ValueError('Session id must be of type list or str')
    if len(check_session_id) > 0:
        return check_session_id       
    else:
        raise ValueError('Given session_id is not present in model_factory.model_summary table')   

def pullTestResults(session_id):
    if type(session_id) == list:
        session_id = str(session_id).replace('[','').replace(']','')
        check_session_id = pd.read_sql("select * from model_factory.model_test_results where session_id in ("+session_id+")", engine)
    if type(session_id) == str:
        check_session_id = pd.read_sql("select * from model_factory.model_test_results where session_id in ('"+session_id+"')", engine)
    else:
        raise ValueError('Session id must be of type list or str')
    if len(check_session_id) > 0:
        return check_session_id       
    else:
        raise ValueError('Given session_id is not present in model_factory.model_test_results table')  


def pullROC(session_id):
    tr = pullTestResults(session_id)
    tr["true_positive_rate"] = (tr["true_positives"])/(tr["true_positives"]+tr["false_negatives"])
    tr["false_positive_rate"] = (tr["false_positives"])/(tr["false_positives"]+tr["true_negatives"])
    roc_line = tr[["population","true_positive_rate","false_positive_rate","session_id"]]
    return roc_line


def pullLiftChart(session_id):
    tr = pullTestResults(session_id)
    lift_chart = tr[["population","target_population","session_id"]]
    return lift_chart


def pullConfMatrix(session_id, threshold_value, threshold_type):
    if type(session_id) != str:
         raise ValueError('Session id must be of type str')
    else:    
        check_session_id = pd.read_sql("select * from model_factory.model_test_results where session_id in ('"+session_id+"')", engine)
    if len(check_session_id) > 0:
        tr = check_session_id       
    else:
        raise ValueError('Given session_id is not present in model_factory.model_test_results table') 
    if threshold_type == "population":
        tr = tr[tr.population <= threshold_value].tail(1)
    if threshold_type == "probability":
        tr = tr[tr.score >= threshold_value].tail(1)
    conf_m = pd.DataFrame(zip(tr.true_positives.tolist()+tr.false_positives.tolist(),
                              tr.false_negatives.tolist()+tr.true_negatives.tolist()),
                          columns = ['predicted_positives','predicted_negatives'])
    conf_m.index = ['actual_positives','actual_negatives']
    return conf_m


def pullAccuracy(session_id, threshold_value, threshold_type):
    if type(session_id) != str:
         raise ValueError('Session id must be of type str')
    else:    
        check_session_id = pd.read_sql("select * from model_factory.model_test_results where session_id in ('"+session_id+"')", engine)
    if len(check_session_id) > 0:
        tr = check_session_id       
    else:
        raise ValueError('Given session_id is not present in model_factory.model_test_results table') 
    if threshold_type == "population":
        tr1 = tr[tr.population <= threshold_value].tail(1)
    if threshold_type == "probability":
        tr1 = tr[tr.score >= threshold_value].tail(1)
    accuracy = float(tr1["true_positives"]+tr1["true_negatives"])/len(tr)
    return accuracy


def pullModelScores(session_id):
    if type(session_id) == list:
        session_id = str(session_id).replace('[','').replace(']','')
        check_session_id = pd.read_sql("select * from model_factory.model_scores where session_id in ("+session_id+")", engine)
    if type(session_id) == str:
        check_session_id = pd.read_sql("select * from model_factory.model_scores where session_id in ('"+session_id+"')", engine)
    else:
        raise ValueError('Session id must be of type list or str')
    if len(check_session_id) > 0:
        return check_session_id       
    else:
        raise ValueError('Given session_id is not present in model_factory.model_scores table')   

