# DOCKER NOTES

First, install Docker if it is not already on your machine. You can find the installation steps here: https://docs.docker.com/get-docker/ 

If you've never used Docker before, they actually have a pretty decent tutorial: https://docs.docker.com/get-started/

This document assumes a baseline understanding of what Docker is, how it works, and the basic vocabulary. However, it skews towards usability for the newcomer. 


## Building the Image

Next, build a docker image from the dockerfile in this folder. 

NOTE: you may have to pull the base image first, do so with:

```
docker pull ubuntu:18.04
```

Once cd'd into this directory, you can do so with:

```
docker build -t vrt_editor .
```

NOTE: the argument after the `-t` can be any name, as shown below with a generic option:

```
docker build -t <name> .
```


## Running the Container

Once the image is built, while in this directory, it can be run with:

```
docker run -it -d -v $PWD:/app vrt_editor bash
```

Here's a quick rundown of what all the commands are doing:

```
docker run: run a container

-it: allow the container to persist
NOTE: this is 100% necessary and NOT optional at all

-d: run detatched, exiting will NOT stop the container
NOTE: this option is NOT entirely necessary, but is useful. If you don't provide this option, you will be dropped directly into the container 

-v: volume mapping, sets current directory ($PWD) into /app folder of container 
NOTE: any changes you make from your local OR inside the container WILL be reflected in the other location immediately
You can use a full path instead of $PWD for your machine, like /path/to/directory:/app
Whatever path you provide (or your current directory if using $PWD) will be mapped into the container, so set this to whatever you want to have available. You can of course move things into it later

vrt_editor: this can be replaced with a generic <anme> option

bash: the command to run once inside the container
NOTE: if you want to use the jupyter notebook, do NOT add this line
```


### Getting Inside Containers

If you ran the above command with the `-d` option, you'll need to get the container ID to get inside the container. First run:

```
docker ps -a
```

This will show you all the containers. When I run it, it looks like this:

```
CONTAINER ID        IMAGE                 COMMAND                  CREATED             STATUS              PORTS                    NAMES
5cc2446ae147        vrt_editor            "bash"                   4 days ago          Up 4 days                                    sleepy_ellis
```

For me to get inside the container, first I copy the container ID `e3bc263754bb` for the `slingshot-edge` image, then run:

```
docker exec -it 5cc2446ae147 bash
```

Which drops me directly into the container. 

NOTE: be sure to replace `5cc2446ae147` with your container ID.


## Docker Closing Remarks

A few final notes on Docker. You can only get inside a running container. 

If your container status looks like `Exited (0) 2 seconds ago` it has been stopped. 

If the first part says `Exited (0)`, you can restart the container with `docker start <container ID>`

However, if you got a non-zero exit code, you won't be able to restart it.

You can stop a running container with `docker stop <container ID` and remove a (stopped) container with `docker rm <container ID>`


## Docker Troubleshooting

If you're having issues like "no space left on device," you can try cleaning things up with these commands (make sure to stop any running containers first):

```
docker rm $(docker ps -q -f 'status=exited')
docker rmi $(docker images -q -f "dangling=true")
docker volume rm $(docker volume ls -qf dangling=true)
```

If you REALLY want to take the "nuke it from orbit" approach (NOT recommended until you've tried the above approach):

```
docker system prune -af
```

