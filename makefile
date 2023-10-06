web:
	docker compose build web; docker compose up -d web
web_logs:
	docker compose build web; docker compose up -d web; docker compose logs web -f
