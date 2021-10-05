# Google Drive Backup

### About

This program takes files from your file system, packages them up, and stores them in Google Drive, removing stale files. I originally developed this to replicate the Snapshot feature of Home Assistant. Although there is an existing Home Assistant 'add-on', [Home Assistant Google Drive Backup](https://github.com/sabeechen/hassio-google-drive-backup), this only works for Hass.io installations of Home Assistant rather than container installations. 

I run it on my home server as a Docker container which I start from cron weekly to backup my config files. I set it up to run in Docker even though it is just a script as I have multiple containers running and this is the best way to keep it isolated. 

Once it is set up and configured correctly, it is simply a matter of configuring a cronjob (Unix) or scheduled task (Windows) to run however often you want to back up your directory to Google Drive. Old backups will be automatically deleted, and new backups will be ready to restore should you need to.




### Getting started

#### Configuration

You are required to configure three environmental variables to run this program. If you prefer to run it in Docker, you can set it when creating the Container.

1. FILE_PATH - the directory in which the files you want to backup are located. It will tar the files for ease of use. e.g.: /home/test_folder
2. GDRIVE_FOLDER - this must be specified, but it does not have to be an existing folder in your Google Drive. If it does not already exist, then it will be created. If there are multiple folders with the same name (including in the trash), you must delete one. e.g. gdrive_backup_test
3. BACKUPS_TO_KEEP - an integer which will specify how many backups to keep. e.g. 5



You are also required to allow programmatic access to your Google Drive. See instructions on how to do this [here](https://developers.google.com/workspace/guides/create-project). There are lots of tutorials available on the internet. Download the credentials file and save it somewhere you can access it. It is also possible to authenticate using a service account if you would prefer.


#### Installation - Docker



1. Clone the repository to your local machine by navigating to where you want to store the code, initialising a git repo, and pulling the code from this repo. 

2. Copy your credentials to the 'app/creds' directory and name it "credentials_token.json".

3. In the same directory, build the docker image: ```docker build --tag hassbackup:latest .```

4. Run the image you just created with the appropriate configuration

For example:

```docker run -e FILE_PATH=/gdrivebackup -e GDRIVE_FOLDER=Home_Assistant_Backups -e BACKUPS_TO_KEEP=5 -e TZ=Europe/London -v gdrivebackup_creds:/home/charlie/docker/homeassistant-backup/app/creds -v /home/charlie/docker/homeassistant-config:/gdrivebackup --name gdrivebackup hassbackup:latest```

Add ```-t -i``` after ```docker run``` the first time you run it inspect the shell and follow the Oauth flow.


Or in Docker Compose:

```
version: '3'
services:
  homeassistant_backup:
    container_name: gdrivebackup
    environment:
      - FILE_PATH=test_folder
      - GDRIVE_FOLDER=test_gdrive_folder
      - BACKUPS_TO_KEEP=2
    volumes:
      - <<your volume>>:<<path to credentials directory>>
    image: gdrivebackup
volumes:
  gdrivebackup_creds:
```

5. You are done! Whenever you want to call the script and backup, simply start the container with ```docker start gdrivebackup``` (or, even easier, call it from cron e.g. ```0 3 * * * docker start gdrivebackup``` to backup every day at 3am)
).

#### Installation - local



1. Clone the repository to your local machine by navigating to where you want to store the code, initialising a git repo, and pulling the code from this repo.

2. Copy your credentials to the 'app/creds' directory and name it "credentials_token.json".


3. Configure the program by setting the environmental variables mentioned above.

   *Optional: create a test directory for the program to back up*

4. Set up a virtual env if you so wish (recommended), then run ```pip install -r requirements.txt```
5.  ```cd app```, then run ``` python main.py ```

6. Follow the oauth flow from the command line to authorise the application to access you Drive.

7. You are done! Call ```main.py``` as many times as you like. You will be informed as to what is happening on the command line.




### Roadmap

- ~~Integrate with Google Drive~~
- ~~Remove stale backups~~
- ~~Allow to be customised from config~~
- ~~Package up with Docker~~
- Publish Docker image?
- Create internal API for health check from Home Assistant