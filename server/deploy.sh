source ~/env/bin/activate
cd ~/nic
git pull
pip install -U pip
pip install -r requirements.txt
cd djnic
./manage.py collectstatic --no-input
./manage.py migrate

sudo cp ~/nic/server/gunicorn/nic.conf.py /etc/gunicorn/nic.conf.py
sudo cp ~/nic/server/supervidor/nic.conf /etc/supervisor/conf.d/nic.conf

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart nic
