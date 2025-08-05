# Contributing to Minicast

Thank you for your interest in contributing to Minicast! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- FFmpeg installed and available in PATH
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/minicast/minicast.git
   cd minicast
   ```

2. **Install dependencies**
   ```bash
   make install
   # or
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests**
   ```bash
   make test
   # or
   pytest tests/ -v
   ```

## Development Workflow

### Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run the formatters:
```bash
make format
# or
black minicast/ tests/
isort minicast/ tests/
```

Check code quality:
```bash
make lint
# or
flake8 minicast/ tests/
mypy minicast/
```

### Testing

Write tests for new features and ensure all tests pass:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=minicast --cov-report=html

# Run specific test file
pytest tests/test_transcoder.py -v
```

### Adding New Features

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   ```bash
   make test
   make lint
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Project Structure

```
minicast/
├── minicast/           # Main package
│   ├── __init__.py
│   ├── transcoder.py   # GIF transcoding functionality
│   └── server.py       # RTSP server implementation
├── tests/              # Test files
├── examples/           # Usage examples
├── docs/               # Documentation
├── gifs/               # Sample GIFs for testing
├── streams/            # Transcoding output
├── logs/               # Log files
├── transcode.py        # CLI transcoder script
├── server.py           # CLI server script
├── requirements.txt    # Python dependencies
├── setup.py           # Package setup
├── pyproject.toml     # Modern Python packaging
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose setup
├── Makefile           # Development tasks
└── .gitignore         # Git ignore rules
```

## Code Guidelines

### Python Code

- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Add docstrings for all public functions and classes
- Keep functions small and focused

### Documentation

- Update README.md for user-facing changes
- Update API.md for API changes
- Add inline comments for complex logic
- Include usage examples

### Testing

- Write unit tests for all new functionality
- Aim for high test coverage
- Use descriptive test names
- Mock external dependencies (FFmpeg, network calls)

## Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat: add support for custom RTSP paths
fix: resolve FFmpeg process cleanup issue
docs: update API documentation
test: add unit tests for transcoder
```

## Pull Request Guidelines

1. **Title**: Use a clear, descriptive title
2. **Description**: Explain what the PR does and why
3. **Tests**: Ensure all tests pass
4. **Documentation**: Update docs if needed
5. **Screenshots**: Include screenshots for UI changes

## Reporting Issues

When reporting issues, please include:

1. **Environment details**:
   - Operating system and version
   - Python version
   - FFmpeg version
   - Minicast version

2. **Steps to reproduce**:
   - Clear, step-by-step instructions
   - Sample input files if applicable

3. **Expected vs actual behavior**:
   - What you expected to happen
   - What actually happened

4. **Error messages**:
   - Full error traceback
   - Log files if available

## Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and general discussion
- **Documentation**: Check the docs/ directory and README.md

## License

By contributing to Minicast, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

Please be respectful and inclusive in all interactions. We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

Thank you for contributing to Minicast! 🎞️📡 