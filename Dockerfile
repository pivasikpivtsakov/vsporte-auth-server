FROM python:3.11.6-slim

# create workdir
RUN mkdir /vsporte-auth-server

# set workdir
WORKDIR /vsporte-auth-server

# install dependencies separately
COPY /pyproject.toml /vsporte-auth-server
# install poetry via pip
RUN pip --no-cache-dir install poetry
# install other dependencies via poetry
RUN poetry config virtualenvs.create false
RUN poetry install

# copy all files
COPY . .

# give access to shell run file
RUN chmod a+x runapp.sh
