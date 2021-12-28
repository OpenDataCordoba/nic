# Install nic app

<pre>

sudo apt update -y
sudo apt upgrade -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo add-apt-repository ppa:certbot/certbot
sudo apt install git python3.8 python3.8-venv \
    supervisor nginx postgresql postgresql-contrib \
    postgresql-10-postgis-2.4 python-certbot-nginx \
    python-memcache

sudo mkdir /etc/gunicorn
# add conf.py file
sudo chown opendatacba:opendatacba /etc/gunicorn
sudo vim /etc/supervisor/conf.d/nic.conf
sudo vim /etc/nginx/sites-available/nic.conf
sudo ln -s /etc/nginx/sites-available/nic.conf /etc/nginx/sites-enabled/nic.conf
sudo vim /etc/nginx/sites-available/cache.conf
sudo ln -s /etc/nginx/sites-available/cache.conf /etc/nginx/sites-enabled/cache.conf

sudo supervisorctl reread
sudo supervisorctl update

sudo supervisorctl start nic

sudo service nginx restart
sudo nginx -t

sudo su - postgres
# create postgis extension, user and database
# migrate DB from previous server

python3.8 -m venv ~/env
source ~/env/bin/activate
pip install -U pip
git clone https://github.com/OpenDataCordoba/nic.git
cd nic
pip install -r dev-requirements.txt 
pip install -r requirements.txt 
   
# define /home/opendatacba/nic/djnic/djnic/local_settings.py
sudo supervisorctl restart nic

sudo certbot --nginx
crontab -e
# define cron tasks
   
</pre>