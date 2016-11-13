
import sqlalchemy
import pandas as pd
from main import *

def storeSummary(summary):
    summary["session_id"] = session_id
    summary.to_sql("model_summary", engine,  schema="model_factory", if_exists='append', index = False) ## it will add rows to model_summary table


def storeTestResults(test_results):
    test_results["session_id"] = session_id
    test_results.to_sql("model_test_results", engine,  schema="model_factory", if_exists='append', index = False)
    ## it will add rows to model_test_results


def storeModelScores(ids, scores):
    scores_df = pd.DataFrame(zip(ids, scores),columns=['id','scores'])
    scores_df["session_id"] = session_id
    scores_df.to_sql("model_scores", engine,  schema="model_factory", if_exists='append', index = False) ## it will add rows to model_scores
