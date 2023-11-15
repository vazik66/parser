# Parser
 
## Start with docker compose

```sh
docker compose up -d
```

## Create django superuser

```sh
docker exec -it habr_parser-web-1  python src/web/manage.py createsuperuser
```
## Go to admin and add hubs

Go to localhost:8000/admin and add hubs to parse
