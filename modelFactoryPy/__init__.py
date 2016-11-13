
import os
import sqlalchemy
import ruamel.yaml as yaml
import pandas as pd
import time
import datetime
from random import randint
import getpass


def getConnection():
    global config
    global engine
    config = yaml.load(open(os.environ['MODELFACTORY']+"\\config.yaml")) ## needs to be changed
    engine = sqlalchemy.create_engine("postgresql://"+config.get('postgres').get('username')+":"+
                                      config.get('postgres').get('password')+"@"+config.get('postgres').get('host')+"/postgres")
    return engine
## here add extra options (getConnection to TD/postgressql; if statements: Jenkins user or normal user; streamAPI option)
#getpass.getuser()


def addModelId(model_id, model_description, score_id_type):
    check_model_id = pd.read_sql("select * from model_factory.model_overview where model_id='"+model_id+"'", engine)
    if len(check_model_id) > 0:
        raise ValueError('Given model_id is already present in model_factory.model_overview table')
    else:
        df = pd.DataFrame(zip([model_id], [model_description], [score_id_type])
             , columns=['model_id','model_description', 'score_id_type'])
        df.to_sql("model_overview", engine,  schema="model_factory", if_exists='append', index = False) ## it will add rows to model_overview table      


def deleteModelId(model_id):
    check_model_id = pd.read_sql("select * from model_factory.model_overview where model_id='"+model_id+"'", engine)
    if len(check_model_id) == 0:
        raise ValueError('Given model_id is already removed from model_factory.model_overview table')
    else:
        connection = engine.connect()
        connection.execute("delete from model_factory.model_overview where model_id='"+model_id+"'")
        connection.close()


def updateThreshold(model_id, threshold_value, threshold_type):
    check_model_id = pd.read_sql("select * from model_factory.model_overview where model_id='"+model_id+"'", engine)
    if len(check_model_id) == 0:
        raise ValueError('Given model_id is not present in model_factory.model_overview table. Please use function addModelId first')
    else:
        if (threshold_type != "probability" and threshold_type != "population"):
            raise ValueError('Given threshold type is not population or probability')
        else:
            connection = engine.connect()
            connection.execute("update model_factory.model_overview set threshold_value='"+threshold_value+"', threshold_type='"+
                               threshold_type+"' where model_id='"+model_id+"'")
            connection.close()


def getSessionId(model_id):
    global session_id
    ## check whether model_id is present in model_overview table -> throw an error if not
    check_model_id = pd.read_sql("select * from model_factory.model_overview where model_id='"+model_id+"'", engine)
    if len(check_model_id) == 0:
        raise ValueError('Given model_id is not present in model_factory.model_overview table. Please use function addModelId first')
    else:
        session_id = config.get('postgres').get('username')+"_"+model_id+"_"+datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d')+"_"+str(randint(1000, 1000000))
        df = pd.DataFrame(zip([session_id], [config.get('postgres').get('username')], [model_id], [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                 , columns=['session_id','user_id', 'model_id', 'start_time'])
        df.to_sql("run_history", engine,  schema="model_factory", if_exists='append', index = False) ## it will add rows to run_history table
        return session_id


def closeSession():
    connection = engine.connect()
    connection.execute("update model_factory.run_history  SET end_time ='"+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"' where session_id='"
                       +session_id+"'")
    connection.close()   
## add streamAPI option


def deleteSession(session_id):
    connection = engine.connect()
    try:
        connection.execute("delete from model_factory.model_summary WHERE session_id='"+session_id+"'")
    except:
        pass
    try:
        connection.execute("delete from model_factory.model_scores WHERE session_id='"+session_id+"'")
    except:
        pass
    try:
        connection.execute("delete from model_factory.model_test_results WHERE session_id='"+session_id+"'")
    except:
        pass
    try:
        connection.execute("delete from model_factory.model_backtesting WHERE session_id='"+session_id+"'")
    except:
        pass
    try:
        connection.execute("delete from model_factory.metadata_table WHERE session_id='"+session_id+"'")
    except:
        pass
    try:
        connection.execute("delete from model_factory.run_history WHERE session_id='"+session_id+"'")
    except:
        pass
    connection.close()


def renameModel(old_model_id, new_model_id):
    
    connection = engine.connect()
    
    check_old_model_id = pd.read_sql("select * from model_factory.model_overview where model_id='"+old_model_id+"'", engine)
    check_old_model_id1 = pd.read_sql("select * from model_factory.run_history where model_id='"+old_model_id+"'", engine)
    check_new_model_id = pd.read_sql("select * from model_factory.model_overview where model_id='"+new_model_id+"'", engine)
    
    if len(check_old_model_id) == 0:
        raise ValueError('Given old_model_id is not present in model_factory.model_overview table, therefore can not be renamed')
    if len(check_new_model_id) > 0:
        raise ValueError('Given new_model_id is already present in model_factory.model_overview table, therefore can not be used for renaming')
    if (len(check_old_model_id) > 0 and len(check_old_model_id1) == 0):
        try:
            connection.execute("Update model_factory.model_overview set model_id='"+new_model_id+"' where model_id="+old_model_id+"'")
        except:
            pass
    else:
        try:
            connection.execute("update model_factory.model_scores set session_id= replace(session_id,'_"
                               +old_model_id+"_','_"+new_model_id+"_') where session_id like '%_"+old_model_id+"_%'")
        except:
            pass
        try:
            connection.execute("update model_factory.metadata_table set session_id= replace(session_id,'_"
                               +old_model_id+"_','_"+new_model_id+"_') where session_id like '%_"+old_model_id+"_%'")
        except:
            pass
        try:
            connection.execute("update model_factory.model_backtesting set session_id= replace(session_id,'_"
                               +old_model_id+"_','_"+new_model_id+"_') where session_id like '%_"+old_model_id+"_%'")
        except:
            pass
        try:
            connection.execute("update model_factory.model_summary set session_id= replace(session_id,'_"
                               +old_model_id+"_','_"+new_model_id+"_') where session_id like '%_"+old_model_id+"_%'")
        except:
            pass
        try:
            connection.execute("update model_factory.model_store set session_id= replace(session_id,'_"
                               +old_model_id+"_','_"+new_model_id+"_') where session_id like '%_"+old_model_id+"_%'")
        except:
            pass
        try:
            connection.execute("update model_factory.model_test_results set session_id= replace(session_id,'_"
                               +old_model_id+"_','_"+new_model_id+"_') where session_id like '%_"+old_model_id+"_%'")
        except:
            pass
        try:
            connection.execute("update model_factory.model_varimp set session_id= replace(session_id,'_"
                               +old_model_id+"_','_"+new_model_id+"_') where session_id like '%_"+old_model_id+"_%'")
        except:
            pass
        try:
            connection.execute("insert into model_factory.run_history select replace(session_id,'_"
                               +old_model_id+"_','_"+new_model_id+"_') as session_id, user_id, '"+new_model_id+
                               "' as model_id, start_time, end_time, last_exported from model_factory.run_history where model_id='"+
                               old_model_id+"'")
        except:
            pass
        try:
            connection.execute("delete from model_factory.run_history where model_id='"+old_model_id+"'")
        except:
            pass
        try:
            connection.execute("update model_factory.model_overview set model_id='"+new_model_id+"' where model_id='"+old_model_id+"'")
        except:
            pass                                                                   


def getSummary(df):
    n_na = []
    a = df.describe().transpose()[["mean","std","50%","min","max","count"]]
    a = a.rename(columns = {'std':'sd','50%':'median','count':'n'})
    for i in a.index:
        n_na.append(len(df[i])-df[i].count())
    a["n_na"] = n_na
    a["variable"] = a.index
    return a.reset_index(drop = True)


def storeSummary(summary):
    summary["session_id"] = session_id
    summary.to_sql("model_summary", engine,  schema="model_factory", if_exists='append', index = False) ## it will add rows to model_summary table


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

		
def getTestResults(scores,labels):
    a = pd.DataFrame(zip(scores,labels),columns=['score','label'])
    a = a.sort('score', ascending = 0)
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


def storeTestResults(test_results):
    test_results["session_id"] = session_id
    test_results.to_sql("model_test_results", engine,  schema="model_factory", if_exists='append', index = False)
    ## it will add rows to model_test_results


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


def storeModelScores(ids, scores):
    scores_df = pd.DataFrame(zip(ids, scores),columns=['id','scores'])
    scores_df["session_id"] = session_id
    scores_df.to_sql("model_scores", engine,  schema="model_factory", if_exists='append', index = False) ## it will add rows to model_scores


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

