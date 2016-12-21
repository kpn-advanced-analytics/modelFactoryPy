
import os
import sqlalchemy
import ruamel.yaml as yaml
import pandas as pd
import time
import datetime
import sys
from random import randint
#import getpass


def getConnection(database = 'postgresql'):
    global config
    global engine
    config = yaml.load(open(os.environ['MODELFACTORY'].replace('\\','/')+"/config.yaml")).get(database) ## needs to be changed
    engine = sqlalchemy.create_engine(database+"://"+config.get('username')+":"+config.get('password')+"@"+
                                      config.get('host')+"/"+config.get('database'))
    return engine
## add streamAPI option + Jenkins
#getpass.getuser()


def addModelId(model_id, model_description, score_id_type):
    connection = engine.connect()
    a = connection.execute("select * from model_factory.model_overview where model_id='"+model_id+"'")
    b = a.fetchall()
    check_model_id = pd.DataFrame.from_records(b,columns = a.keys())
    if len(check_model_id) > 0:
        raise ValueError('Given model_id is already present in model_factory.model_overview table')
        connection.close()
    else:
        connection.execute("INSERT INTO model_factory.model_overview (model_id,model_description,score_id_type,experimental,production) VALUES ('%s', '%s', '%s', '%s', '%s')"
                          % (model_id, model_description, score_id_type, '1', '0'))
        connection.close()
        ## it will add rows to model_overview table


def deleteModelId(model_id):
    connection = engine.connect()
    a = connection.execute("select * from model_factory.model_overview where model_id='" + model_id + "'")
    b = a.fetchall()
    check_model_id = pd.DataFrame.from_records(b, columns=a.keys())
    if len(check_model_id) == 0:
        raise ValueError('Given model_id is already removed from model_factory.model_overview table')
        connection.close()
    else:
        connection.execute("delete from model_factory.model_overview where model_id='"+model_id+"'")
        connection.close()


def updateThreshold(model_id, threshold_value, threshold_type):
    connection = engine.connect()
    a = connection.execute("select * from model_factory.model_overview where model_id='" + model_id + "'")
    b = a.fetchall()
    check_model_id = pd.DataFrame.from_records(b, columns=a.keys())
    if len(check_model_id) == 0:
        raise ValueError('Given model_id is not present in model_factory.model_overview table. Please use function addModelId first')
        connection.close()
    else:
        if (threshold_type != "probability" and threshold_type != "population"):
            raise ValueError('Given threshold type is not population or probability')
        else:
            connection.execute("update model_factory.model_overview set threshold_value='"+str(threshold_value)+"', threshold_type='"+
                               threshold_type+"' where model_id='"+model_id+"'")
            connection.close()


def getSessionId(model_id):
    global session_id
    connection = engine.connect()
    a = connection.execute("select * from model_factory.model_overview where model_id='" + model_id + "'")
    b = a.fetchall()
    check_model_id = pd.DataFrame.from_records(b, columns=a.keys())
    if len(check_model_id) == 0:
        raise ValueError('Given model_id is not present in model_factory.model_overview table. Please use function addModelId first')
        connection.close()
    else:
        session_id = config.get('username')+"_"+model_id+"_"+datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d')+"_"+str(randint(1000, 1000000))
        connection.execute("INSERT INTO model_factory.run_history (session_id,  user_id, model_id, start_time) VALUES ('%s', '%s', '%s', '%s')"
                          % (session_id, config.get('username'), model_id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        connection.close()
        return session_id


def closeSession():
    connection = engine.connect()
    connection.execute("update model_factory.run_history  SET end_time ='"+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"' where session_id='"
                       +session_id+"'")
    sys.stdout.write(session_id)
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

    a1 = connection.execute("select * from model_factory.model_overview where model_id='"+old_model_id+"'")
    b1 = a1.fetchall()
    check_old_model_id = pd.DataFrame.from_records(b1, columns=a1.keys())

    a2 = connection.execute("select * from model_factory.run_history where model_id='" + old_model_id + "'")
    b2 = a2.fetchall()
    check_old_model_id1 = pd.DataFrame.from_records(b2, columns=a2.keys())

    a3 = connection.execute("select * from model_factory.model_overview where model_id='" + new_model_id + "'")
    b3 = a3.fetchall()
    check_new_model_id = pd.DataFrame.from_records(b3, columns=a3.keys())
    
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
