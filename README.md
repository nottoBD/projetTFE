# Projet TFE - Gestion Frais extraordinaires


# Mise en place
1 cloner repo, ouvrir le dossier racine, CMD admin

## postgresql 
(settings.py contient les informations hardcodées)
```
cd "C:\Program Files\PostgreSQL\15\bin"

createuser --username=postgres --no-superuser --createdb --no-createrole usertest

createdb --owner=usertest dbtest --username=postgres

psql -U postgres
```

```
ALTER USER usertest WITH PASSWORD 'usertest';
GRANT ALL PRIVILEGES ON DATABASE dbtest TO usertest;
\q
```

## environnement virtuel
repo, ouvrir le dossier racine, CMD admin
```
python -m venv env

.\venv\Scripts\activate

pip install --upgrade pip

pip install -r requirements.txt
```

## variable env
dans le dossier racine doit etre écrit le fichier .env comme ceci
```
SECRET_KEY='gvfdu$XXXXXXXXXXXXXXXXXXXXXXX'
DEBUG=True
```
la clée est retirée du versioning de settings.py
le module django-environ appel .env dans settings.py

## Django
### Se placer dans la branche dev au préalable pour avoir accès au Hello World!
```
git checkout dev 
```
### Pour faire migrer les changements dans votre base de données :
```
python manage.py makemigrations
python manage.py migrate
```
### Load data test avec fixtures
```
python manage.py loaddata core/fixtures/fixtures.json
```
## Lancer "Hello World!"
Dossier racine, dans l'environnement virtuel
```
python manage.py runserver
```
