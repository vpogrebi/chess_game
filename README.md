# Chess Game Project

A comprehensive web-based chess game built with Django and PostgreSQL, featuring full chess rules implementation, move validation, and a modern web interface.

## 🏁 Overview

This chess game application provides a complete chess playing experience with:
- Full chess rules implementation including special moves (castling, en passant, pawn promotion)
- Real-time move validation and game state management
- PostgreSQL database for persistent game storage
- Modern web interface with interactive chessboard
- Player management and game history tracking
- Draw offers and resignation functionality

## 🛠️ Technology Stack

- **Backend**: Django 5.2.11
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Database Connector**: psycopg2-binary 2.9.11
- **Python**: 3.8+

## 📋 Prerequisites

Before setting up the project, ensure you have:

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd chess_game

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Start PostgreSQL service
brew services start postgresql@14  # macOS
# or
sudo systemctl start postgresql  # Linux

# Create database user and database
psql -c "CREATE USER chess_user WITH PASSWORD 'chess_password';"
psql -c "CREATE DATABASE chess_db OWNER chess_user;"
psql -c "GRANT ALL PRIVILEGES ON DATABASE chess_db TO chess_user;"
```

### 3. Django Setup

```bash
# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit `http://localhost:8000/` to access the chess game.

## 🏗️ Project Structure

```
chess_game/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── DATABASE_SETUP.md        # Database setup instructions
├── models.py                # Legacy models (deprecated)
├── chess/                   # Main chess application
│   ├── __init__.py
│   ├── admin.py            # Django admin configuration
│   ├── apps.py             # Django app configuration
│   ├── game_logic.py       # Core chess game logic (29KB)
│   ├── middleware.py       # Custom middleware
│   ├── migrations/         # Database migrations
│   ├── models.py           # Database models
│   ├── templates/          # HTML templates
│   │   └── chess/
│   │       ├── base.html       # Base template
│   │       ├── create_game.html # Game creation form
│   │       ├── game.html       # Main game interface (56KB)
│   │       ├── game_list.html  # Game listing
│   │       ├── home.html       # Home page
│   │       └── game_temp.html  # Temporary template
│   ├── tests.py            # Test cases
│   ├── urls.py             # URL routing
│   └── views.py            # View logic (16KB)
└── chess_project/          # Django project configuration
    ├── __init__.py
    ├── asgi.py            # ASGI configuration
    ├── settings.py        # Django settings
    ├── urls.py            # Project URL routing
    └── wsgi.py            # WSGI configuration
```

## 🗄️ Database Schema

### Core Models

#### Player
- `id`: Primary key
- `first_name`: Player's first name (max 50 chars)
- `last_name`: Player's last name (max 50 chars)
- `color`: Piece color ('white' or 'black', unique)
- `created_at`: Timestamp when player was created

#### Game
- `id`: Primary key
- `name`: Game name (max 200 chars)
- `white_player`: Foreign key to Player (white pieces)
- `black_player`: Foreign key to Player (black pieces)
- `current_turn`: Whose turn it is ('white' or 'black')
- `status`: Game status ('waiting', 'active', 'check', 'checkmate', 'stalemate', 'resigned', 'draw')
- `winner`: Foreign key to Player (optional)
- `started_at`: Game start timestamp
- `ended_at`: Game end timestamp
- `created_at`: Creation timestamp

#### ChessPiece
- `id`: Primary key
- `game`: Foreign key to Game
- `type`: Piece type ('pawn', 'rook', 'knight', 'bishop', 'queen', 'king')
- `color`: Piece color ('white' or 'black')
- `position_x`: X coordinate (0-7, representing a-h)
- `position_y`: Y coordinate (0-7, representing 1-8)
- `is_captured`: Whether piece is captured
- `captured_at`: When piece was captured
- `has_moved`: Whether piece has moved (for castling/en passant)
- `en_passant_vulnerable`: Whether vulnerable to en passant
- `has_castled`: Whether piece has castled

#### Move
- `id`: Primary key
- `game`: Foreign key to Game
- `piece`: Foreign key to ChessPiece
- `from_x`, `from_y`: Source position
- `to_x`, `to_y`: Destination position
- `captured_piece`: Foreign key to captured ChessPiece (optional)
- `move_number`: Move number in game
- `notation`: Algebraic notation of move
- `timestamp`: When move was made
- `is_castle`: Whether move is castling
- `is_en_passant`: Whether move is en passant
- `is_promotion`: Whether move is pawn promotion
- `promotion_piece`: Type of piece promoted to

#### DrawOffer
- `id`: Primary key
- `game`: Foreign key to Game
- `offering_player`: Foreign key to Player
- `offered_at`: When offer was made
- `is_active`: Whether offer is still active

#### CapturedPiece
- `id`: Primary key
- `game`: Foreign key to Game
- `piece`: Foreign key to ChessPiece
- `captured_by`: Foreign key to Player
- `captured_at`: When piece was captured

## 🎮 Game Features

### Implemented Chess Rules

1. **Basic Movement**
   - All pieces move according to standard chess rules
   - Real-time move validation
   - Illegal move prevention

2. **Special Moves**
   - **Castling**: King and rook special move under specific conditions
   - **En Passant**: Pawn capture of adjacent pawn that moved two squares
   - **Pawn Promotion**: Pawn promotion to Queen, Rook, Bishop, or Knight upon reaching the 8th rank

3. **Game States**
   - Check detection and notification
   - Checkmate detection
   - Stalemate detection
   - Draw by agreement
   - Resignation

4. **Move Validation**
   - Piece-specific movement rules
   - Path obstruction detection
   - Capture validation
   - King safety checks

### User Interface Features

- Interactive chessboard with drag-and-drop functionality
- Real-time move highlighting
- Captured pieces display
- Game history and move notation
- Player information display
- Game status indicators
- Responsive design for various screen sizes

## 🔧 Configuration

### Database Configuration

Database settings are configured in `chess_project/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'chess_db',
        'USER': 'chess_user',
        'PASSWORD': 'chess_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Environment Variables

For production deployment, consider using environment variables:

```python
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'chess_db'),
        'USER': os.environ.get('DB_USER', 'chess_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'chess_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

### Security Settings

For production deployment:

1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS`
3. Set a secure `SECRET_KEY`
4. Configure HTTPS
5. Set up proper CORS policies if needed

## 🎯 API Endpoints

The application provides the following URL endpoints:

- `/` - Home page
- `/create/` - Create new game
- `/games/` - List all games
- `/game/<id>/` - View specific game
- `/game/<id>/start/` - Start a game
- `/game/<id>/move/` - Make a move (POST)
- `/game/<id>/valid-moves/` - Get valid moves for a piece
- `/game/<id>/check-status/` - Check game status (check, checkmate, etc.)
- `/game/<id>/resign/` - Resign from game
- `/game/<id>/draw/` - Offer/accept draw
- `/game/<id>/check-draw-offer/` - Check for draw offers
- `/game/<id>/delete/` - Delete game

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test chess

# Run with verbose output
python manage.py test --verbosity=2
```

## 📦 Dependencies

### Core Dependencies
- `Django==5.2.11` - Web framework
- `psycopg2-binary==2.9.11` - PostgreSQL adapter
- `asgiref==3.11.1` - ASGI reference implementation
- `sqlparse==0.5.5` - SQL parsing library
- `typing_extensions==4.15.0` - Type hints extensions

### Development Dependencies (optional)
- `pytest-django` - Enhanced testing
- `django-debug-toolbar` - Debugging tools
- `coverage` - Code coverage analysis

## 🚀 Deployment

### Production Deployment Checklist

1. **Environment Setup**
   ```bash
   export DEBUG=False
   export SECRET_KEY='your-secret-key'
   export ALLOWED_HOSTS='yourdomain.com'
   ```

2. **Database**
   - Use production PostgreSQL instance
   - Configure connection pooling
   - Set up regular backups

3. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

4. **Web Server**
   - Configure Nginx or Apache
   - Set up SSL/TLS certificates
   - Configure Gunicorn or uWSGI

5. **Monitoring**
   - Set up application monitoring
   - Configure error logging
   - Set up performance monitoring

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: chess_db
      POSTGRES_USER: chess_user
      POSTGRES_PASSWORD: chess_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  postgres_data:
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure PostgreSQL is running
   - Check database credentials
   - Verify database exists

2. **Migration Issues**
   ```bash
   # Reset migrations (caution: deletes data)
   python manage.py migrate chess zero
   python manage.py migrate chess
   ```

3. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Permission Issues**
   - Check file permissions
   - Ensure database user has proper privileges

### Debug Mode

Enable debug middleware in `chess_project/settings.py`:

```python
MIDDLEWARE = [
    'chess.middleware.DebugMiddleware',
    # ... other middleware
]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:

- Create an issue in the repository
- Check the troubleshooting section
- Review the Django documentation

## 🔮 Future Enhancements

Planned features include:

- Online multiplayer functionality
- Chess AI opponent
- Tournament management
- Game analysis and replay
- Mobile app version
- Chess puzzles and training modes
- Integration with chess.com/lichess APIs

---

**Last Updated**: March 2026
**Version**: 1.0.0
**Framework**: Django 5.2.11
**Database**: PostgreSQL
