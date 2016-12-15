##Docker is only tested on Ubuntu 16.04!

In order to run docker, do the following:

  1. Clone modelFactoryPy locally. For example, to /Projects/modelFactoryPy
  2. Go to docker folder inside the project folder. For example, cd /Projects/modelFactoryPy/docker
  3. Run the command: docker build -f Dockerfile .
  4. Run the command: docker run -it -p 8888:8888 -p 5432:5432 {container_id}
  5. After the image is running, go to browser on your machine and go to http://localhost:8888/tree
  6. Go to Template folder and run Template.ipynb


To be done: get Jenkins working for scheduling (at the moment he is installed, but is not configured and is not running)
