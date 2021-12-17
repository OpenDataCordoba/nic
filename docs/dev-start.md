# Local environment

Create a Python 3 local environment and run

´´´
pip install -r requirements.txt
pip install -r dev-requirements.txt
cd djnic
./manage.py migrate
./manage runserver
´´´

Create test data

´´´
./manage create_tesrt_data
´´´

Done, app running at http://localhost:8000/

## Testing

Run tests

´´´
./manage runserver
´´´
