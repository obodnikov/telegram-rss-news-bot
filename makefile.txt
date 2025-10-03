.PHONY: help install setup run test debug clean

help:
	@echo "Telegram RSS Bot - Available Commands"
	@echo ""
	@echo "  make install    - Install dependencies"
	@echo "  make setup      - Run interactive setup"
	@echo "  make run        - Run the bot"
	@echo "  make test       - Test run (once)"
	@echo "  make debug      - Run with debug logging"
	@echo "  make clean      - Clean cache files"
	@echo ""
	@echo "Systemd commands:"
	@echo "  make systemd-install  - Install systemd service"
	@echo "  make systemd-start    - Start service"
	@echo "  make systemd-stop     - Stop service"
	@echo "  make systemd-status   - Check service status"
	@echo "  make systemd-logs     - View service logs"
	@echo ""
	@echo "Docker commands:"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-run       - Run in Docker"
	@echo "  make docker-stop      - Stop Docker container"
	@echo "  make docker-logs      - View Docker logs"

install:
	pip3 install -r requirements.txt

setup:
	chmod +x setup.sh
	./setup.sh

run:
	@if [ ! -f .env ]; then echo "Error: .env file not found. Run 'make setup' first."; exit 1; fi
	bash -c "source .env && python3 rss_bot.py"

test:
	@if [ ! -f .env ]; then echo "Error: .env file not found. Run 'make setup' first."; exit 1; fi
	bash -c "source .env && python3 rss_bot.py --once"

debug:
	@if [ ! -f .env ]; then echo "Error: .env file not found. Run 'make setup' first."; exit 1; fi
	bash -c "source .env && python3 rss_bot.py --once --log-level DEBUG"

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type f -name '*.log' -delete
	rm -rf .pytest_cache

# Systemd commands
systemd-install:
	@echo "Installing systemd service..."
	@if [ ! -f rss-bot.service ]; then echo "Error: rss-bot.service not found"; exit 1; fi
	@echo "Please edit rss-bot.service with your paths first!"
	@echo "Then run: sudo cp rss-bot.service /etc/systemd/system/"
	@echo "          sudo systemctl daemon-reload"
	@echo "          sudo systemctl enable rss-bot"

systemd-start:
	sudo systemctl start rss-bot

systemd-stop:
	sudo systemctl stop rss-bot

systemd-restart:
	sudo systemctl restart rss-bot

systemd-status:
	sudo systemctl status rss-bot

systemd-logs:
	sudo journalctl -u rss-bot -f

systemd-enable:
	sudo systemctl enable rss-bot

systemd-disable:
	sudo systemctl disable rss-bot

# Docker commands
docker-build:
	docker build -t rss-bot .

docker-run:
	@if [ ! -f .env ]; then echo "Error: .env file not found. Run 'make setup' first."; exit 1; fi
	docker run -d --name rss-bot --restart=always --env-file .env rss-bot

docker-stop:
	docker stop rss-bot
	docker rm rss-bot

docker-logs:
	docker logs -f rss-bot

docker-shell:
	docker exec -it rss-bot /bin/bash

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

docker-compose-logs:
	docker-compose logs -f
