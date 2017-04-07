### Installation

- It is highly recommended to use virtual environments for the installation of python packages, although it can still be done without them.

   * Install virtualenv
   ```
   sudo pip install virtualenv
   mkdir ~/.virtualenvs
   sudo pip install virtualenvwrapper
   ```

   * Edit ~/.bashrc. Add at the end of file
   ```
   export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python
   export WORKON_HOME=$HOME/.virtualenvs
   source /usr/local/bin/virtualenvwrapper.sh
   ```
   * to activate execute: 
   ```
   source ~/.bashrc
   ```

- Create virtualenv

```
mkvirtualenv --python=`which python3` itch
```

- Install requirements

```
while read line; do sudo apt-get install -y "$line"; done < setup/requirements.txt
```

- Install pip requirements

```
while read line; do pip install "$line"; done < setup/requirements-pip.txt
```
 
 NOTE: Make sure daphne 1.1.0 is installed. We had some issue with 1.1.2
 
- Add nginx config file ```/etc/nginx/sites-enabled/itch.conf``` for ITCH. Nginx will serve as a proxy server in front of Daphne

```
upstream iwebsocket {
    server 127.0.0.1:9000;
}

server {

    listen      9091 default_server;
    listen [::]:9091 default_server;
    server_name _;
    root /home/t7/dev/ITCH;
    index index.html index.htm index.nginx-debian.html;


    location / {
        proxy_set_header X-Real-IP  $remote_addr;
        proxy_set_header Host       $http_host;
        proxy_hide_header X-Frame-Options;
        proxy_pass          http://127.0.0.1:9000;
    }

    location /API-ws {
        proxy_pass http://iwebsocket;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header X-Real-IP  $remote_addr;
    }


    location /static {
        autoindex on;
        alias /home/t7/dev/ITCH/static/;
    }

}

```

- Restart nginx: ```sudo systemctl restart nginx.service```

- Create service ```itch-daphne.service``` for running Daphne in /etc/systemd/system/:

```
[Unit]
Description=ITCH Daphne Web Server
After=redis-server.service

[Service]
Type=simple
WorkingDirectory=/home/t7/dev/ITCH
ExecStart=/home/t7/.virtualenvs/itch/bin/daphne -b 127.0.0.1 -p 9000 itch.asgi:channel_layer --root-path=/home/t7/dev/ITCH 
Restart=always

[Install]
WantedBy=multi-user.target
```

- Enable newly added service:
```
sudo systemctl enable itch-daphne.service
```

- Start newly added service:
```
sudo systemctl start itch-daphne.service
```

- Create service ```itch-workers.service```  in /etc/systemd/system/ for spawning django workers:

```
[Unit]
Description=ITCH Django workers
After=redis-server.service

[Service]
Type=simple
WorkingDirectory=/home/t7/dev/ITCH
ExecStart=/home/t7/.virtualenvs/itch/bin/python manage.py runworker --threads 2
Restart=always

[Install]
WantedBy=multi-user.target
```

Threads n is the number of cores of the machine where it is running

- Enable newly added service:
```
sudo systemctl enable itch-workers.service
```

- Start newly added service:
```
sudo systemctl start itch-workers.service
```

- Run django migrations

```
/home/t7/.virtualenvs/itch/bin/pythonpython manage.py migrate
```

#### ITCH project creation

This section can be skipped as it describes how the project was setup in the first place. 
This is not required in a regular ITCH installation as the folder structure and files will already
have been created. This section is just for reference.

- Create Django project

```
cd /home/t7/dev/ITCH
django-admin startproject itch .
```

- Create ```config``` django app

```
cd /home/t7/dev/ITCH
python manage.py startapp ams
```

- Modify default ```settings.py``` to reflect changes in Databases, Cache, Logging, Installed_Apps
