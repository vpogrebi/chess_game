# PostgreSQL Database Setup for Chess App

## Database Configuration

The chess application uses PostgreSQL for data storage.

### Database Details
- **Database Name**: chess_db
- **User**: chess_user
- **Password**: chess_password
- **Host**: localhost
- **Port**: 5432

### Setup Commands (if needed)

If you need to recreate the database setup:

```bash
# Start PostgreSQL service
brew services start postgresql@14

# Create database user
psql -c "CREATE USER chess_user WITH PASSWORD 'chess_password';"

# Create database
psql -c "CREATE DATABASE chess_db OWNER chess_user;"

# Grant privileges
psql -c "GRANT ALL PRIVILEGES ON DATABASE chess_db TO chess_user;"
```

### Django Settings

The database configuration in `chess_project/settings.py`:

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

### Migration Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Dependencies

Required packages are listed in `requirements.txt`:
- Django==5.2.11
- psycopg2-binary==2.9.11

Install with:
```bash
pip install -r requirements.txt
```
