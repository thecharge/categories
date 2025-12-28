# Categories 

## How it was generated

### Generate the standard Django project structure in the current directory (first time it will take some time so docker can pull dependencies)

```shell
docker-compose run --rm web django-admin startproject core .
```

### Now creating the specific app for our logic called categories:

```shell
docker-compose run --rm web python manage.py startapp categories
```

## Build and run

```shell
docker-compose up --build -d
docker-compose exec web python manage.py createsuperuser
docker-compose exec web pytest
docker-compose exec web python manage.py analyze_rabbits
```

## Clear local env

```shell
docker-compose down
docker system prune --all --volumes
```
