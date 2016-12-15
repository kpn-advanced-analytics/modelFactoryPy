## get base image
FROM ubuntu:14.04
#FROM openjdk:8-jdk

## install all needed apt packages
COPY apt_packages.txt /tmp/apt-packages.txt
RUN chmod a+r /tmp/apt-packages.txt && \
    apt-get update --fix-missing  && apt-get install build-essential -y && xargs -a /tmp/apt-packages.txt apt-get install -y

## install anaconda, jupyter, model fcatory, config, scripts
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/archive/Anaconda2-4.2.0-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /opt/conda && rm ~/anaconda.sh

ENV PATH /opt/conda/bin:$PATH
RUN /opt/conda/bin/conda install jupyter -y --quiet && mkdir /opt/notebooks/Template && \
    && mkdir /opt/notebooks/data 

COPY Template.ipynb /opt/notebooks/Template
RUN chmod a+r+x opt/notebooks/Template/Template.ipynb

COPY titanic.csv /opt/notebooks/data
RUN chmod a+r+x opt/notebooks/data/titanic.csv

COPY run_jupyter.sh /opt/conda/bin
RUN chmod a+r+x /opt/conda/bin/run_jupyter.sh
RUN pip install ruamel.yaml psycopg2 git+https://github.com/kpn-advanced-analytics/modelFactoryPy 

ENV MODELFACTORY=/opt/notebooks
COPY config.yaml /opt/notebooks
RUN chmod a+r opt/notebooks/config.yaml

EXPOSE 8888

## install postgres, create model factory schema and needed tables

RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update && apt-get install -y python-software-properties software-properties-common postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3

COPY create_schema.sql /
RUN chmod a+r create_schema.sql

RUN usermod -a -G sudo postgres
RUN echo "postgres ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER postgres
RUN  /etc/init.d/postgresql start && psql --command "CREATE USER modelfactory WITH SUPERUSER PASSWORD 'modelfactory';" && \
     psql -U postgres -a -q -w -f create_schema.sql

#RUN bridge_ip=$(ifconfig docker0 | grep "inet addr:" | awk '{print $2}' | sed "s/.*://")
# RUN docker_subnet="172.17.1.0/16"

#RUN sed -i.orig "s/^[#]\?listen_addresses .*/listen_addresses = '${bridge_ip}'/g" /etc/postgresql/9.3/main/postgresql.conf
#RUN echo "host    all             all             172.17.1.0/16            md5" >> /etc/postgresql/9.3/main/pg_hba.conf
#RUN ufw allow in from ${docker_subnet} to ${bridge_ip} port 5432

#
#RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.3/main/pg_hba.conf
#RUN echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf
#RUN sed -e "s/[#]\?listen_addresses = .*/listen_addresses = '*'/g" -i '/etc/postgresql/9.3/main/postgresql.conf'
#

RUN sed -i "/^#listen_addresses/i listen_addresses='*'" /etc/postgresql/9.3/main/postgresql.conf
RUN sed -i "/^# DO NOT DISABLE\!/i # Allow access from any IP address" /etc/postgresql/9.3/main/pg_hba.conf
RUN sed -i "/^# DO NOT DISABLE\!/i host all all 0.0.0.0/0 md5" /etc/postgresql/9.3/main/pg_hba.conf

EXPOSE 5432


## jenkins
#RUN wget -q -O - https://pkg.jenkins.io/debian/jenkins-ci.org.key | apt-key add -
#RUN sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
#RUN apt-get update
#RUN apt-get install jenkins -y
#EXPOSE 8080

## CMD
#CMD ["opt/conda/bin/run_jupyter.sh","/usr/lib/postgresql/9.3/bin/postgres", "-D", "/var/lib/postgresql/9.3/main", "-c", "config_file=/etc/postgresql/9.3/main/postgresql.conf"]
 CMD [ "/bin/bash" ]

