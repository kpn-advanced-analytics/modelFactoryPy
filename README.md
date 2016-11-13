# modelFactoryPy
Python package for Model Factory created by Advanced Analytics team at KPN.

**How to get started with your own ModelFactory:**

1) First of all, you need PostgresSQL. If you do not have it and want to play with modelfactory, install PostgresSQL on your laptop or use Amazon RDS (it allows a one year free trial).

2) After PostgresSQL is installed, create MODELFACTORY environmental variable. On Windows it can be tricky, you need to do the following:
   
      -add a system environment variable MODELFACTORY with value of folder of your choice, for example: C:\Projects;
      
      -add the following line to PATH system environment variable: %MODELFACTORY%\bin;
      
      -in command line call echo %MODELFACTORY% -> this should return the specified path
      
2) Copy the config.yaml file that you can find in the repository in folder specified in MODELFACTORY (e.g., C:\Projects). Fill in the config.yaml file with the username, password and host you use to connect to PostgresSQL.

3) We are almost there. You have to install SQLAlchemy (http://pythoncentral.io/how-to-install-sqlalchemy/) and psycopg2 package.

4) You should be able to run the template file without any errors.
