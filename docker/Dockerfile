## get base image
FROM ubuntu:14.04
#FROM openjdk:8-jdk

## install all needed apt packages
COPY apt_packages.txt /tmp/apt-packages.txt
RUN chmod a+r /tmp/apt-packages.txt && \
    apt-get update --fix-missing  && apt-get install build-essential -y && xargs -a /tmp/apt-packages.txt apt-get install -y

## install anaconda & jupyter
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/archive/Anaconda2-4.2.0-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /opt/conda && rm ~/anaconda.sh

ENV PATH /opt/conda/bin:$PATH
RUN /opt/conda/bin/conda install jupyter -y --quiet && mkdir /opt/notebooks 

COPY run_jupyter.sh /opt/conda/bin
RUN chmod a+r+x /opt/conda/bin/run_jupyter.sh

## clean
#RUN TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
#    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
#    dpkg -i tini.deb && rm tini.deb && \
#    apt-get clean 

## install postgres, create model factory schema and needed tables

RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update && apt-get install -y python-software-properties software-properties-common postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3

COPY create_schema.sql /
RUN chmod a+r create_schema.sql

USER postgres
RUN  /etc/init.d/postgresql start && psql -U postgres -a -q -w -f create_schema.sql

## jenkins
USER root
RUN wget -q -O - https://pkg.jenkins.io/debian/jenkins-ci.org.key | apt-key add -
RUN sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
RUN apt-get update
RUN apt-get install jenkins -y

## CMD
EXPOSE 8888
#ENTRYPOINT ["/usr/bin/tini","--"]
#CMD ["sh","opt/conda/bin/run_jupyter.sh"]
CMD [ "/bin/bash" ]

