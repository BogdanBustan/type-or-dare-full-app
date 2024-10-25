# Dual Database FastAPI Example

This project demonstrates a FastAPI application that leverages Python's type system and validation capabilities while storing data in both MongoDB and SQLite databases. It showcases best practices for data validation, API development, and database interactions.

## Features

- FastAPI REST API with type validation
- Dual database storage (MongoDB and SQLite)
- CSV file processing with Pandera validation
- Individual record processing with Pydantic validation
- Docker and docker-compose setup
- Comprehensive data retrieval endpoints

## Type Validation Features

The project demonstrates several levels of type validation:

1. **Pydantic Models**: Used for API request/response validation
2. **SQLModel**: Combines SQLAlchemy with Pydantic for SQL database interactions
3. **Beanie**: MongoDB ODM with type support

## Project Structure

```
project/
├── app/
│   ├── main.py              # FastAPI application setup
│   ├── models/              # Data models and schemas
│   ├── database/            # Database connections
│   └── api/                 # API routes
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile              # Docker build instructions
└── requirements.txt        # Python dependencies
```

## Getting Started

1. Clone the repository
2. Start the services:
   ```bash
   docker-compose up --build
   ```

## API Endpoints

- `POST /api/upload/csv`: Upload and process a CSV file
- `POST /api/user`: Create a single user
- `GET /api/user/{user_id}`: Retrieve user by ID
- `GET /api/users`: Retrieve all users

## Data Validation

### CSV Validation
The application uses Pydantic to validate CSV data with the following rules:
- User ID: Required, string
- Name: Required, string (2-50 characters)
- Email: Required, valid email format
- Age: Required, integer (0-120)

### API Request Validation
Individual record creation is validated using Pydantic with similar rules to the CSV validation.

## Database Storage

### MongoDB
- Uses Beanie ODM for type-safe MongoDB interactions
- Stores user documents in a 'users' collection

### SQLite
- Uses SQLModel for type-safe SQL operations
- Stores user records in a 'user' table

## Development

To run the project in development mode:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Testing the API

1. Upload CSV:
   ```bash
   curl -X POST -F "file=@sample_data.csv" http://localhost:8000/api/upload/csv
   ```

2. Create individual user:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
        -d '{"user_id": "USR006", "name": "Test User", "email": "test@email.com", "age": 25}' \
        http://localhost:8000/api/user
   ```

3. Retrieve user:
   ```bash
   curl http://localhost:8000/api/user/USR001
   ```

4. Retrieve all users:
   ```bash
   curl http://localhost:8000/api/users
   ```

## Type Safety Benefits

This project demonstrates several benefits of Python's type system:

1. **Early Error Detection**: Type hints help catch errors during development
2. **Better IDE Support**: Enhanced autocomplete and refactoring capabilities
3. **Self-Documenting Code**: Types serve as documentation
4. **Runtime Validation**: Pydantic provides runtime type checking
5. **Database Schema Safety**: Both MongoDB and SQLite operations are type-safe
