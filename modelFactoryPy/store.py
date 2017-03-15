
import pandas as pd
import main
import cPickle as pickle
import base64


def storeSummary(summary):
    summary["session_id"] = main.session_id
    summary.to_sql("model_summary", main.engine,  schema="model_factory", if_exists='append', index = False) ## it will add rows to model_summary table


def storeTestResults(test_results):
    test_results["session_id"] = main.session_id
    test_results.to_sql("model_test_results", main.engine,  schema="model_factory", if_exists='append', index = False)
    ## it will add rows to model_test_results


def storeModelScores(ids, scores):
    scores_df = pd.DataFrame(zip(ids, scores),columns=['id','scores'])
    scores_df["session_id"] = main.session_id
    scores_df.to_sql("model_scores", main.engine,  schema="model_factory", if_exists='append', index = False) ## it will add rows to model_scores

def storeModel(model):
    model_string = pickle.dumps(model, 0)
    encoded = base64.b64encode(model_string)
    df = pd.DataFrame({"session_id": [main.session_id, 'test'], "model": [encoded, 'test']})
    df.to_sql("model_store", main.engine, schema="model_factory", if_exists='append', index=False)
    connection = main.engine.connect()
    connection.execute("delete from model_factory.model_store where session_id='test'")
    connection.close()