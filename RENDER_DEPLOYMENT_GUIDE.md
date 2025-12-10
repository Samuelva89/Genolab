# Genolab Deployment to Render

This guide explains how to deploy the Genolab application to Render, a cloud platform that hosts your applications. Follow these steps to get your Genolab instance running in production.

## Prerequisites

- A Render account (sign up at https://render.com)
- A GitHub repository containing your Genolab code (including the `render.yaml` file created for this deployment)
- External S3-compatible storage (AWS S3, DigitalOcean Spaces, or Cloudflare R2)
- A secure secret key for JWT authentication

## Deployment Steps

### 1. Prepare Your Repository

1. Ensure your repository contains these files:
   - `render.yaml` (in the root directory)
   - `services/Dockerfile.prod`
   - `services/.env.render` (as reference for required environment variables)

2. Make sure your code is committed and pushed to GitHub

### 2. Set Up External Storage

Your Genolab application requires external object storage for file uploads. Follow the instructions in `RENDER_MINIO_SETUP.md` to set up one of the following:
- AWS S3
- DigitalOcean Spaces
- Cloudflare R2
- Or any other S3-compatible storage service

### 3. Create a New Web Service on Render

1. Log into your Render dashboard
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Select your Genolab repository
5. Render will automatically detect the `render.yaml` configuration
6. Click "Create Web Service"

### 4. Configure Environment Variables

After creating the service, you'll need to set up environment variables:

1. Go to your service dashboard
2. Navigate to "Environment" or "Environment Variables"
3. Add these required variables:

```
MINIO_ENDPOINT=https://your-storage-provider-endpoint
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
MINIO_BUCKET_NAME=your_bucket_name
SECRET_KEY=generate_a_secure_random_key_with_python_c_import_secrets_c_print_secrets_token_urlsafe_32
POSTGRES_PASSWORD=your_secure_db_password
```

### 5. Manual Service Creation (Alternative)

If you prefer to create services manually instead of using `render.yaml`:

#### Web Service:
- **Environment**: Python
- **Build Command**: 
  ```bash
  cd services && pip install -r requirements.txt && pip install gunicorn
  ```
- **Start Command**: 
  ```bash
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT app.main:app
  ```
- **Health Check**: `/api/health`

#### PostgreSQL Database:
- **Environment**: PostgreSQL
- **Database Name**: `genolab_db`
- **Database User**: `genolab_user`
- Set `POSTGRES_PASSWORD` in environment variables

#### Redis Instance:
- **Environment**: Redis
- Use the connection string provided by Render

### 6. Environment Variables Reference

Your application will automatically receive these from Render:
- `DATABASE_URL` (PostgreSQL connection string)
- `REDISHOST`, `REDISPORT` (Redis connection details)

You need to provide these manually:
- `MINIO_ENDPOINT` - Your external storage endpoint
- `MINIO_ACCESS_KEY` - Your storage access key
- `MINIO_SECRET_KEY` - Your storage secret key
- `MINIO_BUCKET_NAME` - Your storage bucket name
- `SECRET_KEY` - A secure random key for JWT (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `DEBUG=False` (for production)
- `TESTING=False` (for production)

### 7. Deploy and Monitor

1. After configuring environment variables, trigger a manual deploy or wait for automatic deployment
2. Monitor the logs in your Render dashboard during deployment
3. Check that all services (web, database, redis) are running properly
4. Visit your service URL to verify the application is running

### 8. Post-Deployment Tasks

1. Run database migrations (if not handled automatically):
   ```bash
   # This may need to be done through an SSH session or one-time job
   python services/create_db.py
   ```

2. Verify file upload functionality with your external storage provider

## Celery Worker Configuration (Optional)

If you want to run background tasks with Celery:

1. Create an additional process in your Render service or create a separate background worker service
2. Use the start command: `celery -A app.celery_worker.celery_app worker --loglevel=info`
3. Ensure it has the same environment variables as the web service

## Troubleshooting

### Common Issues:

1. **Database Connection Errors**: Verify that `DATABASE_URL` is properly set
2. **Storage Connection Errors**: Check that your external storage credentials are correct
3. **Redis Connection Errors**: Confirm `REDIS_URL` is properly configured
4. **Application Not Starting**: Check logs in Render dashboard for specific error messages

### Useful Commands:

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Test database connection
python services/check_database.py
```

## Scaling Configuration

As your Genolab instance grows, you can easily scale:

- **Web Service**: Increase instance size or add replicas in the Render dashboard
- **Database**: Upgrade to larger plans as needed
- **Redis**: Scale memory as needed based on task queue requirements

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Genolab README](README.md) (if available in your repository)