Docker is only tested on Ubuntu 16.04!

In order to run docker, do the following:
  1) clone modelFactoryPy locally. For example, to /Projects/modelFactoryPy
  2) go to docker folder inside the project folder. For example, cd /Projects/modelFactoryPy/docker
  3) run the command: docker build -f Dockerfile .
  4) run the command: docker run -it -p 8888:8888 -p 5432:5432 {container_id}
  5) after the image is running, go to browser on your machine and go to http://localhost:8888/tree
  6) go to Template folder and run Template.ipynb


To be done: Jenkins for scheduling
