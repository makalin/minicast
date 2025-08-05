# Minicast Makefile
# Common development and deployment tasks

.PHONY: help install test lint clean build docker-build docker-run docker-stop

# Default target
help:
	@echo "Minicast - Ultra-Low-Bandwidth Reaction GIF Channel"
	@echo ""
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker containers"
	@echo "  transcode    - Transcode a GIF (usage: make transcode INPUT=file.gif)"
	@echo "  server       - Start server (usage: make server INPUT=file.mp4)"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Run tests
test:
	pytest tests/ -v --cov=minicast --cov-report=html

# Run linting
lint:
	flake8 minicast/ tests/ --max-line-length=100
	black --check minicast/ tests/
	mypy minicast/

# Format code
format:
	black minicast/ tests/
	isort minicast/ tests/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	python setup.py sdist bdist_wheel

# Docker commands
docker-build:
	docker build -t minicast:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

# Development commands
transcode:
	@if [ -z "$(INPUT)" ]; then \
		echo "Usage: make transcode INPUT=file.gif"; \
		exit 1; \
	fi
	python transcode.py $(INPUT) output.mp4 --stream-ready

server:
	@if [ -z "$(INPUT)" ]; then \
		echo "Usage: make server INPUT=file.mp4"; \
		exit 1; \
	fi
	python server.py --input $(INPUT) --port 554

# Create sample GIF for testing
sample-gif:
	@echo "Creating sample GIF for testing..."
	@mkdir -p gifs
	@echo "Please add a GIF file to the gifs/ directory for testing"

# Setup development environment
dev-setup: install sample-gif
	@echo "Development environment setup complete!"
	@echo "Add GIF files to gifs/ directory and run: make transcode INPUT=gifs/your_file.gif"

# Quick start
quick-start: dev-setup
	@echo "Quick start guide:"
	@echo "1. Add a GIF to gifs/ directory"
	@echo "2. Run: make transcode INPUT=gifs/your_file.gif"
	@echo "3. Run: make server INPUT=streams/your_file_stream.mp4"
	@echo "4. Open VLC and connect to: rtsp://localhost:554/minicast" 