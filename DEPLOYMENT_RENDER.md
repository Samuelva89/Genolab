# Genolab - Genomic Laboratory Management System

Genolab is a comprehensive genomic laboratory management system built with FastAPI, designed to manage organisms, strains, and perform bioinformatics analyses.

## Deployment Options

This repository supports multiple deployment configurations depending on your database preference:

### Option 1: MySQL Deployment
Deploy with MySQL as the primary database.

### Option 2: PostgreSQL + PostgREST Deployment  
Deploy with PostgreSQL database and PostgREST for automatic REST API generation.

## Technologies Used

- **Backend**: FastAPI (Python 3.11)
- **Database Options**: MySQL or PostgreSQL
- **API Layer**: FastAPI + optionally PostgREST
- **Task Queue**: Celery + Redis
- **Object Storage**: MinIO (S3-compatible)
- **Deployment**: Render

## Deployment to Render

### Prerequisites

1. A Render account (for institutional use)
2. Access to external object storage (MinIO/S3 bucket)
3. Properly configured repository access

### MySQL Deployment

1. Create a new Web Service on Render
2. Point to your repository
3. Update the Blueprint Configuration file to use `mysql_render.yaml`
4. Configure environment variables (see `.env.render.mysql`)

### PostgreSQL + PostgREST Deployment

1. Create a new Web Service on Render
2. Point to your repository
3. Update the Blueprint Configuration file to use `postgres_postgrest_render.yaml`
4. Configure environment variables (see `.env.render.postgres`)

## Environment Variables Setup

For both deployments, you'll need to configure the following:

- `SQLALCHEMY_DATABASE_URL`: Database connection string (auto-configured by Render from database service)
- `REDIS_URL`: Redis connection string (auto-configured by Render from Redis service)
- `MINIO_ENDPOINT`: MinIO/S3 endpoint URL
- `MINIO_ACCESS_KEY`: Access key for MinIO/S3
- `MINIO_SECRET_KEY`: Secret key for MinIO/S3
- `MINIO_BUCKET_NAME`: Bucket name for file storage
- `SECRET_KEY`: JWT secret key for authentication
- `POSTGREST_URL`: (Only for PostgreSQL+PostgREST option) PostgREST API URL

## Database Configuration

### MySQL
- Database Name: `genolab_db`
- Username: `genolab_user`
- Connection handled automatically by Render database service

### PostgreSQL with PostgREST
- Database Name: `genolab_db`
- Username: `genolab_user`
- PostgREST provides additional REST API layer
- JWT authentication configured to match FastAPI

## File Storage

The application uses MinIO (S3-compatible) for file storage. You can use:
- Self-hosted MinIO instance
- AWS S3
- Google Cloud Storage
- Any S3-compatible storage service

## API Documentation

Once deployed, API documentation is available at:
- `/docs` - Interactive API documentation (Swagger UI)
- `/redoc` - Alternative API documentation (ReDoc)

## Security Features

- JWT-based authentication
- Rate limiting (60 requests per minute per IP)
- Secure password hashing with bcrypt
- Input validation with Pydantic
- Environment-based configuration

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│   Clients   │───▶│  FastAPI App │───▶│  PostgreSQL  │
│ (Browser,   │    │              │    │    MySQL     │
│  Mobile)    │    │              │    │    Database  │
└─────────────┘    └──────────────┘    └──────────────┘
                          │
                    ┌─────────────┐
                    │   Redis     │
                    │ (Task Queue)│
                    └─────────────┘
                          │
                   ┌──────────────┐
                   │ MinIO/S3     │
                   │ (File Storage)│
                   └──────────────┘
```

## Development

To run locally for development:
```bash
# Clone the repository
git clone <your-repo-url>
cd Genolab

# Set up environment variables
cp services/.env.example services/.env
# Edit .env with your local configuration

# Install dependencies
cd services
pip install -r requirements.txt

# Start the application
uvicorn app.main:app --reload
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For institutional deployment support, contact your IT department for Render account setup and configuration assistance.