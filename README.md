#SISTEMA DE TICKETS - DJANGO REST FRAMEWORK

## Contenido
Este proyecto tiene dos brazos develop y master, **develop** tiene todo el codigo para pruebas y **master** tiene el codigo para producción

## Requerimientos
Version Python 3.7.7

## Instalación
* Instalar Python 3.7.7
* Instalar Pip para Python: https://tecnonucleous.com/2018/01/28/como-instalar-pip-para-python-en-windows-mac-y-linux/
* Instalar las dependencias(En la raiz del proyecto) con el comando:
```bash
pip install -r requirements.txt
```
* Editar el archivo settings.py para cambiar la conección a la base de datos

```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dbtickets',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
* Crear Migraciones con el comando:
```bash
python manage.py makemigrations
```
* Pasar la migraciones a la base de datos con el comando:
```bash
python manage.py migrate
```
* Crear un superuuario para la base de datos y llenar los datos con el comando:
```bash
python manage.py createsuperuser
```
* Para correr el proyecto con el comando:
```bash
python manage.py runserver 0.0.0.0:8000
```

### Notes
* La version usada para Django es 2.2.9
* Las dependencias usadas se encuentran en requirements.txt
