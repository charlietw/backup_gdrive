# Google Drive Backup

### About

This program takes files from your file system, packages them up, and stores them in Google Drive, removing stale files. I originally developed this to replicate the Snapshot feature of Home Assistant. Although there is an existing Home Assistant 'add-on', [Home Assistant Google Drive Backup](https://github.com/sabeechen/hassio-google-drive-backup), this only works for Hass.io installations of Home Assistant rather than containers. This will run on Docker.

### Roadmap

- ~~Integrate with Google Drive~~
- Remove stale backups
- Allow to be customised from config
- Package up with Docker