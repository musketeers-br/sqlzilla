#!/bin/bash
image_name_iris=sqlzilla-iris
container_name_iris=sqlzilla-iris-1

# # list the ID of container specified in container_name_iris variable
# container_name_iris_id=$(docker container ls -a | grep $container_name_iris | awk '{print $1}')
# # stop the container specified in container_name_iris_id variable
# docker container stop $container_name_iris_id
# # remove the container specified in container_name_iris_id variable
# docker container rm $container_name_iris_id

# stop the container
docker-compose down
# remove the image specified in image_name_iris variable
docker image rm $image_name_iris
# clear the cache
docker system prune -f