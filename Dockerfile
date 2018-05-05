FROM python:3.6

MAINTAINER Romain Soufflet <romain@soufflet.io>

RUN pip install tox twine wheel

ADD . /src
WORKDIR /src

RUN python setup.py develop
