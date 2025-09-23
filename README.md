sudo -u postgres psql
sudo -u postgres psql javaproject



sudo -u postgres psql

CREATE USER ifiokambrose WITH PASSWORD '12345678';
CREATE DATABASE bbifk;
GRANT ALL PRIVILEGES ON DATABASE bbifk TO ifiokambrose;
GRANT ALL ON SCHEMA public TO ifiokambrose;


-- Make sure the user has access to the database itself
GRANT ALL PRIVILEGES ON DATABASE mydatabase TO ifiokambrose;

-- (Optional but recommended) Set default schema search path
ALTER ROLE ifiokambrose SET search_path TO public;

sudo -u postgres psql
sudo -u postgres psql bbifk