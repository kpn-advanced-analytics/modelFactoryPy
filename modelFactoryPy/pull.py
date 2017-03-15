
import sqlalchemy
import pandas as pd
import main
import warnings
import cPickle as pickle
import base64

def pullModel(session_id):
    connection = main.engine.connect()
    a = connection.execute("select * from model_factory.model_store where session_id='" + session_id + "'")
    b = a.fetchall()
    df = pd.DataFrame.from_records(b, columns=a.keys())
    model = pickle.loads(base64.b64decode(df.model[0]))
    connection.close()
    return model

def pullSummary(session_id):
    if type(session_id) == list:
        session_id = session_id
    else:
        session_id = [session_id]

    connection = main.engine.connect()
    a = connection.execute("select distinct session_id from model_factory.model_summary where session_id in ("+str(session_id).replace('[', '').replace(']', '')+")")
    b = a.fetchall()
    check_session_id = pd.DataFrame.from_records(b, columns=a.keys()).session_id.tolist()

    if len(check_session_id) < len(session_id):
        raise ValueError("The following session_id's are not present in model_factory.model_summary table: %s"
                         % str(list(set(session_id)-set(check_session_id))).replace('[', '').replace(']', ''))
        connection.close()
    else:
        a1 = connection.execute(
            "select * from model_factory.model_summary where session_id in (" + str(session_id).replace('[', '').replace(']', '') + ")")
        b1 = a1.fetchall()
        summary = pd.DataFrame.from_records(b1, columns=a1.keys())
        connection.close()
        return summary

def pullTestResults(session_id):
    if type(session_id) == list:
        session_id = session_id
    else:
        session_id = [session_id]

    try:
        test_results_dict
    except NameError:
        global test_results_dict
        test_results_dict = dict()

    known_session_id = [session_id[e] for e, i in enumerate(map(lambda x: test_results_dict.has_key(x), session_id)) if i == True]
    unknown_session_id = list(set(session_id) - set(known_session_id))

    if len(known_session_id) > 0:
        test_results = pd.concat([test_results_dict[k] for k in known_session_id if k in test_results_dict])
        warnings.warn("Test results for these sessions were already pulled and are being reused: %s"
                      % str(known_session_id).replace('[', '').replace(']', ''))
    else:
        test_results = pd.DataFrame()

    if len(unknown_session_id) > 0:
        connection = main.engine.connect()
        a = connection.execute("select distinct session_id from model_factory.model_test_results where session_id in ("
                               +str(unknown_session_id).replace('[', '').replace(']', '')+")")
        b = a.fetchall()
        check_session_id = pd.DataFrame.from_records(b, columns=a.keys()).session_id.tolist()

        if len(check_session_id) < len(unknown_session_id):
            raise ValueError("The following session_id's are not present in model_factory.model_test_results table: %s"
                             % str(list(set(unknown_session_id)-set(check_session_id))).replace('[', '').replace(']', ''))
            connection.close()
        else:
            a1 = connection.execute(
                "select * from model_factory.model_test_results where session_id in (" + str(unknown_session_id).replace('[',
                                                                                                            '').replace(']',
                                                                                                                        '') + ")")
            b1 = a1.fetchall()
            test_results1 = pd.DataFrame.from_records(b1, columns=a1.keys())
            connection.close()
            for i in unknown_session_id:
                test_results_dict[i] = test_results1[test_results1["session_id"] == i]
    else:
        test_results1 = pd.DataFrame()

    test_results = pd.concat([test_results1, test_results])

    return test_results


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
        tr = pullTestResults(session_id)
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
        tr = pullTestResults(session_id)
    if threshold_type == "population":
        tr1 = tr[tr.population <= threshold_value].tail(1)
    if threshold_type == "probability":
        tr1 = tr[tr.score >= threshold_value].tail(1)
    accuracy = float(tr1["true_positives"]+tr1["true_negatives"])/len(tr)
    return accuracy


def pullModelScores(session_id):
    if type(session_id) == list:
        session_id = session_id
    else:
        session_id = [session_id]

    connection = main.engine.connect()
    a = connection.execute("select distinct session_id from model_factory.model_scores where session_id in ("+str(session_id).replace('[', '').replace(']', '')+")")
    b = a.fetchall()
    check_session_id = pd.DataFrame.from_records(b, columns=a.keys()).session_id.tolist()

    if len(check_session_id) < len(session_id):
        raise ValueError("The following session_id's are not present in model_factory.model_scores table: %s"
                         % str(list(set(session_id)-set(check_session_id))).replace('[', '').replace(']', ''))
        connection.close()
    else:
        a1 = connection.execute(
            "select * from model_factory.model_scores where session_id in (" + str(session_id).replace('[',
                                                                                                        '').replace(']',
                                                                                                                    '') + ")")
        b1 = a1.fetchall()
        scores = pd.DataFrame.from_records(b1, columns=a1.keys())
        connection.close()
        return scores
