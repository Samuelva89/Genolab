# Genolab Deployment Guide for Institutional Accounts

This guide provides detailed instructions for deploying Genolab to Render using an institutional account.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setting Up Render Account](#setting-up-render-account)
3. [Database Selection](#database-selection)
4. [Deployment Steps](#deployment-steps)
5. [Environment Variables Configuration](#environment-variables-configuration)
6. [PostgreSQL + PostgREST Specific Setup](#postgresql--postgrest-specific-setup)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Security Considerations](#security-considerations)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting the deployment, ensure your institution has:

- A Render institutional account
- Administrative access to the GitHub repository
- Access to an object storage solution (MinIO, AWS S3, etc.)
- SSL certificate management capabilities (if custom domain is used)

## Setting Up Render Account

### 1. Account Creation
- Navigate to [https://render.com](https://render.com)
- Sign up using institutional email address
- Verify the email address
- Contact Render sales for institutional pricing plans

### 2. Team Setup
- Create a team for your department/institution
- Invite team members with appropriate roles (Admin, Member)
- Set up billing information specific to your institution

### 3. Security Settings
- Enable two-factor authentication for all team members
- Set up SSO if your institution supports it
- Configure IP restrictions if required by your security policy

## Database Selection

Choose between two deployment options based on your institutional requirements:

### Option A: MySQL Deployment
Best for institutions familiar with MySQL or requiring MySQL-specific features.

### Option B: PostgreSQL + PostgREST Deployment
Best for institutions preferring PostgreSQL or wanting automatic REST API generation.

## Deployment Steps

### Step 1: Prepare Your GitHub Repository

Run the setup script to prepare your repository:

```bash
chmod +x setup_github.sh
./setup_github.sh
```

Then push the code to your institutional GitHub repository.

### Step 2: MySQL Deployment

1. Log into your Render dashboard
2. Click "New +" and select "Web Service"
3. Connect to your GitHub repository
4. Select the branch to deploy (typically `main`)
5. For "Root Directory", enter `services`
6. In "Environment", select "Python"
7. Under "Build Command", enter:
   ```
   echo "python-3.11.10" > runtime.txt && \
   cd services && \
   pip install --upgrade pip && \
   pip install -r requirements.txt
   ```
8. Under "Start Command", enter:
   ```
   cd services && python create_db.py && PYTHONPATH=/opt/render/project/src/services:$PYTHONPATH gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:$PORT --timeout 120
   ```
9. Set the "Health Check Path" to `/api/health`
10. Add environment variables as described in the next section
11. Create a MySQL database service in Render
12. Link the web service to the database service

### Step 3: PostgreSQL + PostgREST Deployment

1. Follow steps 1-10 from the MySQL deployment
2. Create a PostgreSQL database service in Render
3. Create a separate web service for PostgREST using the Dockerfile:
   - For "Environment", select "Docker"
   - Use the Dockerfile.postgrest file
   - Configure environment variables for database connection
4. Link all services appropriately

## Environment Variables Configuration

### Required Variables for Both Deployments:

#### Database Configuration
- `SQLALCHEMY_DATABASE_URL`: Render will auto-populate from database service
- `PORT`: Render will auto-populate (leave blank, value comes from Render)

#### Redis Configuration
- `REDIS_URL`: Render will auto-populate from Redis service

#### MinIO/S3 Configuration
- `MINIO_ENDPOINT`: Your S3-compatible endpoint URL
- `MINIO_ACCESS_KEY`: Access key for your storage account
- `MINIO_SECRET_KEY`: Secret key for your storage account
- `MINIO_BUCKET_NAME`: Name of the bucket to use (default: genolab-bucket)

#### Security Configuration
- `SECRET_KEY`: Generate a strong secret key (32+ random characters)
  (Generate using: `openssl rand -hex 32`)
- `ALGORITHM`: Set to `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

#### Application Settings
- `DEBUG`: Set to `False` for production
- `TESTING`: Set to `False` for production
- `MAX_UPLOAD_SIZE_MB`: Max file upload size (default: 10)
- `ALLOWED_EXTENSIONS`: Allowed file extensions (default: fasta,fastq,gb,gff,fa,fq)

### PostgREST-Specific Variables:
- `POSTGREST_URL`: Public URL of your PostgREST service

## PostgreSQL + PostgREST Specific Setup

### 1. PostgREST Configuration
- Create a dedicated service for PostgREST
- Use the provided `Dockerfile.postgrest` and `postgrest.conf`
- Ensure the JWT secret matches your FastAPI application

### 2. Database Schema
- PostgREST will expose your database schema automatically
- Ensure proper permissions are set for database roles
- Configure row-level security if needed

### 3. Authentication Integration
- Configure JWT authentication to work across both services
- Sync the secret keys between FastAPI and PostgREST

## Monitoring and Maintenance

### Health Checks
- Monitor the `/api/health` endpoint regularly
- Set up alerting for service downtime
- Monitor resource utilization (CPU, memory, disk)

### Backups
1. Database backups: Configure automated backups in Render
2. File storage: Regular backup of MinIO/S3 buckets
3. Application configuration: Version control for all configuration files

### Scaling
- Monitor application performance metrics
- Adjust Render service plan as needed
- Consider adding CDN for static assets

### Updates
- Establish a process for applying security updates
- Plan for database migration procedures
- Test updates in staging environment first

## Security Considerations

### Network Security
- Use HTTPS for all connections
- Implement IP whitelisting if applicable
- Regularly review firewall rules

### Data Protection
- Encrypt database connections (SSL/TLS)
- Implement proper access controls
- Regular security audits of credentials

### API Security
- Rate limiting to prevent abuse
- Input validation and sanitization
- Secure authentication mechanisms

### Credential Management
- Never hardcode credentials in source code
- Use Render's encrypted environment variable storage
- Regularly rotate secrets
- Implement principle of least privilege

## Troubleshooting

### Common Issues

#### Database Connection Problems
- Verify database service is running
- Check database connection string
- Ensure database has proper tables created
- Confirm firewall rules allow connections

#### File Upload Failures
- Verify MinIO/S3 credentials
- Check bucket permissions
- Confirm endpoint accessibility
- Validate file size limits

#### Application Startup Failures
- Check application logs in Render dashboard
- Verify all required environment variables are set
- Confirm dependencies are installed correctly
- Review build logs for errors

#### Authentication Issues
- Verify JWT secret consistency across services
- Check token expiration settings
- Confirm authentication endpoints are accessible

### Diagnostic Commands
Access your running service to troubleshoot:

```bash
# View application logs
render logs <service-id>

# Connect to database to check tables
psql/mysql -h <database-host> -U <username> -d <database-name>

# Test API endpoints
curl https://<your-service-url>/api/health
```

### Support Process
1. Collect relevant logs and error messages
2. Document the steps to reproduce the issue
3. Escalate to Render support if infrastructure-related
4. Contact institutional IT support if network/security related

## Conclusion

Following this guide will enable you to successfully deploy Genolab to Render using your institutional account. Remember to regularly update and maintain the system to ensure optimal performance and security. Always follow your institution's security policies and compliance requirements.

For additional support, refer to the Render documentation or contact their support team directly.