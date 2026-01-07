# Licensed under MIT.

## Third-Party Notices

This project uses the following open-source software:

### Django REST Framework

### Other Dependencies (Django REST Framework for exaple) are subject to their respective licenses.

## Build and run

First relay the `http://django` to `127.0.0.1` in your `hosts` file

[Changing hosts file in windows](https://learn.microsoft.com/en-us/windows/powertoys/hosts-file-editor)

[Changing hosts file in linux/mac](https://gist.github.com/andreipa/47ce0679d1905883c18b9ac3a1a9a8f6)

So you can later observe the app

```shell
docker-compose down
# clean the docker env so we can rebuild again 
docker system prune --all --volumes

# build and detach , if it fails you may need to run i twice - cold start sometimes messes up the pgsql
docker-compose up --build -d --force-recreate --remove-orphans

# only first time create super user:
docker-compose exec web python manage.py createsuperuser # then create the user

# test, prepare and run migrations
docker-compose exec web pytest
docker-compose run --rm --entrypoint="" web python manage.py makemigrations
docker-compose run --rm --entrypoint="" web python manage.py migrate

# If needed you can clear the database 
docker-compose exec web python manage.py clear_categories

# test the 200k 
docker-compose exec web python manage.py stress_test_rabbits

# when needed execute the analyze script
docker-compose exec web python manage.py analyze_rabbits


# clear the database
docker-compose exec web python manage.py clear_categories
```

Then go to [http://django/api/docs/](http://django/api/docs/)

## Tips

Try the Tree: Use [GET] /api/categories/tree/.
Move a Node: [PATCH] /api/categories/{id}/move/ with {"parent_id": new_id}

## Urls

1. [http://django/api/](http://django/api/)
2. [http://django/admin/](http://django/admin/)
3. [http://django/api/docs/](http://django/api/docs/)

## How it was generated

### Generate the standard Django project structure in the current directory (first time it will take some time so docker can pull dependencies)

```shell
docker-compose run --rm --entrypoint="" web django-admin startproject core .
```

### Now creating the specific app for our logic called categories

```shell
docker-compose run --rm --entrypoint="" web python manage.py startapp categories
```
