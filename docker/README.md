##Docker is only tested on Ubuntu!

In order to test the docker, do the following:

  1. Run the command: docker run -it -p 8888:8888 -p 8080:8080 -p 5432:5432 kpnadvancedanalytics/modelfactory
  2. Go to http://localhost:8888/tree -> Template and run Template.ipynb
  3. Go to http://localhost:8080 -> log in with username **modelfactory** and password **modelfactory** -> view the modelfactory job
