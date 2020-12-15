FROM jordanirabor/python3.7-pip-pipenv

COPY . /fitness_jogger

WORKDIR /fitness_jogger
RUN apt-get update && apt-get -y install gdal-bin
RUN pipenv install
RUN chmod +x entrypoint.sh
