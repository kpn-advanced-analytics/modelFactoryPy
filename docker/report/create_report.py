
## import libraries
from modelFactoryPy import main
from modelFactoryPy import pull
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

## define connection
main.getConnection()

## import session_id
session_id = open('output.txt', 'r').read() 

## save run information
run = pd.read_sql(
    "SELECT * FROM model_factory.model_overview o JOIN model_factory.run_history r ON o.model_id = r.model_id WHERE r.session_id = '"+session_id+"'", main.engine).transpose()
run.to_html("run.html", header = False)

## save summary information
summary = pull.pullSummary(session_id)
for var in ["mean","sd","median","min","max"]:
    summary[var] = summary[var].apply(lambda x: "%.2f" % x)
summary.to_html("summary.html", index = False)

## get ROC & liftchart
roc = pull.pullROC(session_id)
liftchart = pull.pullLiftChart(session_id)

## save liftchart
fg = plt.figure(figsize=(5,5))
l1 = plt.plot(liftchart.population, liftchart.target_population)
tl = plt.title("Liftchart")

plt.savefig("lift.png")

## save ROC
fg = plt.figure(figsize=(5,5))
l1 = plt.plot(roc.false_positive_rate, roc.true_positive_rate)
tl = plt.title("ROC curve")

plt.savefig("ROC.png")

c_matrix = pull.pullConfMatrix(session_id,float(run[0].tolist()[[e for e,y in enumerate(run.index) if y=='threshold_value'][0]])
                                    ,run[0].tolist()[[e for e,y in enumerate(run.index) if y=='threshold_type'][0]])
c_matrix.to_html("c_matrix.html")

acc = pd.DataFrame({"Accuracy":[pull.pullAccuracy(session_id,float(run[0].tolist()[[e for e,y in enumerate(run.index) if y=='threshold_value'][0]])
                                    ,run[0].tolist()[[e for e,y in enumerate(run.index) if y=='threshold_type'][0]])]})
acc.to_html("acc.html", index = False)

