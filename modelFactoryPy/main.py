
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
