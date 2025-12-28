# How it was generated

1. Generate the standard Django project structure in the current directory (first time it will take some time so docker can pull dependencies)

```shell
docker-compose run --rm web django-admin startproject core .
```

2. Now creating the specific app for our logic called categories:

```shell
docker-compose run --rm web python manage.py startapp categories
```
