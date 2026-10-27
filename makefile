# Run the development environment
dev:
	APP_ENV=dev docker compose up --build

# Run the test environment
test:
	APP_ENV=test docker compose up --build

# Run the production environment
prod:
	APP_ENV=prod docker compose up --build

# Stop all running containers
stop:
	docker compose down
