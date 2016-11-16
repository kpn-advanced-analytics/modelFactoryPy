# modelFactoryPy
Python package for Model Factory created by Advanced Analytics team at KPN.

Presentation about Model Factory can be found there: http://www.slideshare.net/MariaVechtomova/model-factory-presentation-meetup
Detailed overview will follow soon.

**How to get started with your own ModelFactory:**

1) First of all, you need PostgresSQL. If you do not have it and want to play with modelfactory, install PostgresSQL on your laptop or use Amazon RDS (it allows a one year free trial).

2) After PostgresSQL is installed, create MODELFACTORY environmental variable. On Windows it can be tricky, you need to do the following:
   
      -add a system environment variable MODELFACTORY with value of folder of your choice, for example: C:\Projects;
      
      -add the following line to PATH system environment variable: %MODELFACTORY%\bin;
      
      -in command line call echo %MODELFACTORY% -> this should return the specified path
      
3) Copy the config.yaml file that you can find in the repository in folder specified in MODELFACTORY (e.g., C:\Projects). Fill in the config.yaml file with the username, password and host you use to connect to PostgresSQL.

4) Run postgres_create_tables.sql file in PostgresSQL to create correct schema and tables.

5) We are almost there. You have to install SQLAlchemy (http://pythoncentral.io/how-to-install-sqlalchemy/) and psycopg2 package.

6) Install the package (by downloading or cloning it locally and calling the following from cmd: pip install -e path-to-folder-with-package

7) You should be able to run the template file without any errors (it uses the dataset titanic.csv, which is located in folder data)
