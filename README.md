# Categories 

## How it was generated

### Generate the standard Django project structure in the current directory (first time it will take some time so docker can pull dependencies)

```shell
docker-compose run --rm --entrypoint="" web django-admin startproject core .
```

### Now creating the specific app for our logic called categories:

```shell
docker-compose run --rm --entrypoint="" web python manage.py startapp categories
```

## Build and run

First relay the `http://django` to `127.0.0.1` in your `hosts` file
So you can later observe the app

```shell
docker-compose down
docker system prune --all --volumes
docker-compose up --build -d
docker-compose exec web python manage.py createsuperuser # then create the user
docker-compose exec web pytest # check test
docker-compose exec web python manage.py analyze_rabbits # analyze
```
