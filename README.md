# levenshtein-distance-service 

## Table of content
1. [Introduction](#introduction)
2. [Development](#development)
    1. [Getting started](#getting-started)
    2. [How to enable BuildKit?](#how-to-enable-buildkit)   
       1. [Enable the BuildKit in Docker Desktop](#enable-the-buildkit-in-docker-desktop)
       2. [Enable the BuildKit in a fresh terminal](#enable-the-buildkit-in-a-fresh-terminal)
       3. [On Linux machines, you may also need](#on-linux-machines-you-may-also-need)
    3. [Building your Docker images](#building-your-docker-images)
    4. [How to update project dependencies?](#how-to-update-project-dependencies)
    5. [How to run services locally?](#how-to-run-services-locally)
3. [Testing and code formatting](#testing-and-code-formatting)
    1. [How to run tests locally?](#how-to-run-tests-locally)
    2. [How to format the code before pushing new changes to remote?](#how-to-format-the-code-before-pushing-new-changes-to-remote)
4. [Continuous integration/CI](#continuous-integration)
    1. [Code coverage](#code-coverage)


## Introduction

A web service for calculating the Levenshtein distance between two sequences.

In order to compare and study proteins, scientists have devised many computational techniques and
algorithms. One such algorithm is the “Levenshtein distance”, which computes the distance between
two string-like sequences. It is used as a simple measure of similarity between two proteins.

The aim of this project is to develop a web application where a user can compute the Levenshtein distance between
two proteins.

## Development

### Getting started

...

### How to enable BuildKit?

This could be achieved in different ways.

#### Enable the BuildKit in Docker Desktop

![image info](docs/screenshot_docker_desktop_enable_buildkit.png)

#### Enable the BuildKit in a fresh terminal

```
export DOCKER_BUILDKIT=1
```

##### On Linux machines, you may also need:
```
export COMPOSE_DOCKER_CLI_BUILD=1
```

### Building your Docker images

```shell
docker build --ssh default . -f Dockerfile -t mscheremetjew/levenshtein-distance-service

docker-compose build
```

And then the service can be started as following:

```shell
docker-compose up
```

### How to update project dependencies?

For this project we are using pip-tools to manage all project dependencies. Apply changes to
requirements.in and run pip-compile, which generates an updated version of requirements.txt.

For rsa keys run...
```console
make pip-compile-rsa
```

For ed-25519 keys run...
```console
make pip-compile-ed-25519
```

### How to run services locally?

#### How to start all services defined in docker-compose file - for development only?

```shell
docker-compose up
```

OR use the following Makefile command:
```shell
make up
```

#### How to start services marked with specific profiles - for development only?

Certain services are marked with specific profiles. To start these services
you have to use the --profile option in your docker-compose command.

```shell
docker-compose [--profile prometheus]  up
```

## Testing and code formatting

### How to run tests locally?

```console
make pytest

OR you can run specific test like this...
docker-compose run --rm --entrypoint=sh <service-name> -c "pytest app/tests/unit/test_*.py"
```

### How to format the code before pushing new changes to remote?

```console
make format

make lint
```

## Continuous integration

...

### Code coverage

For this project code coverage is set up.