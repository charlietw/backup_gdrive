# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /home/charlie/docker/homeassistant-backup

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN mkdir test_folder

RUN touch test_folder/file1

COPY . .

ENV FILE_PATH=test_folder
ENV GDRIVE_FOLDER=test_gdrive_folder
ENV BACKUPS_TO_KEEP=1

WORKDIR /home/charlie/docker/homeassistant-backup/app

CMD [ "python3" , "main.py"]