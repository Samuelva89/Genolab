# Genolab Render Deployment: External Storage Setup (MinIO Compatible)

This document provides instructions for setting up external object storage for your Genolab deployment on Render. Since Render doesn't natively provide object storage, you'll need to use an external service that's compatible with the S3 API (like AWS S3, DigitalOcean Spaces, or Cloudflare R2).

## Option 1: AWS S3 Setup

### 1. Create an S3 Bucket
1. Log in to your AWS Console
2. Navigate to the S3 service
3. Click "Create bucket"
4. Name your bucket (e.g., `genolab-your-app-name`)
5. Choose an appropriate region
6. Uncheck "Block all public access" if files need to be publicly accessible
7. Create the bucket

### 2. Set up IAM User for S3 Access
1. Go to AWS IAM service
2. Create a new user with programmatic access
3. Attach a policy with S3 permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::genolab-your-app-name",
                "arn:aws:s3:::genolab-your-app-name/*"
            ]
        }
    ]
}
```

### 3. Configure Render Environment Variables
Add the following environment variables to your Render service:

- `MINIO_ENDPOINT`: `https://s3.your-aws-region.amazonaws.com`
- `MINIO_ACCESS_KEY`: Your AWS IAM access key ID
- `MINIO_SECRET_KEY`: Your AWS IAM secret access key
- `MINIO_BUCKET_NAME`: `genolab-your-app-name`

## Option 2: DigitalOcean Spaces Setup

### 1. Create a Space
1. Log in to your DigitalOcean account
2. Navigate to Spaces
3. Click "Create a Space"
4. Choose a region
5. Name your Space (e.g., `genolab-your-app-name`)

### 2. Create Access Keys
1. Go to DigitalOcean API settings
2. Create a new access key
3. Note the Access Key ID and Secret Key

### 3. Configure Render Environment Variables
Add the following environment variables to your Render service:

- `MINIO_ENDPOINT`: `https://your-region.digitaloceanspaces.com`
- `MINIO_ACCESS_KEY`: Your DigitalOcean Spaces access key ID
- `MINIO_SECRET_KEY`: Your DigitalOcean Spaces secret key
- `MINIO_BUCKET_NAME`: `genolab-your-app-name`

## Option 3: Cloudflare R2 Setup

### 1. Create an R2 Bucket
1. Log in to your Cloudflare dashboard
2. Navigate to R2
3. Click "Create bucket"
4. Name your bucket (e.g., `genolab-your-app-name`)

### 2. Generate Access Keys
1. Go to R2 settings
2. Click "Manage R2 API tokens"
3. Create a new token with read/write permissions

### 3. Configure Render Environment Variables
Add the following environment variables to your Render service:

- `MINIO_ENDPOINT`: `https://your-account-id.r2.cloudflarestorage.com`
- `MINIO_ACCESS_KEY`: Your R2 access key ID
- `MINIO_SECRET_KEY`: Your R2 secret access key
- `MINIO_BUCKET_NAME`: `genolab-your-app-name`

## Setting Environment Variables in Render

1. Go to your Genolab service in the Render dashboard
2. Navigate to "Environment" or "Environment Variables" settings
3. Add the variables for your chosen storage provider
4. Add the required variables:
   - `MINIO_ENDPOINT`
   - `MINIO_ACCESS_KEY`
   - `MINIO_SECRET_KEY`
   - `MINIO_BUCKET_NAME`
   - `SECRET_KEY` (generate a secure random key)

## Testing Your Storage Setup

After deployment, you can verify that storage is working by:

1. Checking the application logs for any storage-related errors
2. Uploading a test file through your Genolab API
3. Verifying the file appears in your chosen storage service

## Important Notes

- Make sure to keep your access keys secure and never commit them to version control
- Set appropriate permissions to minimize security risks
- Consider enabling encryption at rest for your storage service
- Plan for backup and disaster recovery for your object storage