sudo -u postgres psql
sudo -u postgres psql javaproject


CREATE USER username WITH PASSWORD '12345678';
CREATE DATABASE mydatabase;
GRANT ALL PRIVILEGES ON DATABASE mydatabase TO ifiokambrose;
GRANT ALL ON SCHEMA public TO ifiokambrose;

