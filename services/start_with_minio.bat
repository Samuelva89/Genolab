@echo off
echo Starting Genolab API with MinIO connection...

REM Set environment variables for host-based MinIO connection
set MINIO_ENDPOINT=http://localhost:9000
set S3_ENDPOINT_URL=http://localhost:9000

REM Start the uvicorn server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause