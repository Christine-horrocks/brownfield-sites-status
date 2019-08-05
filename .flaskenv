FLASK_ENV=development
FLASK_CONFIG=config.DevelopmentConfig
FLASK_APP=application.wsgi:app
SECRET_KEY=replaceinprod
DATABASE_URL=postgresql://localhost/brownfield_status
S3_REGION=eu-west-1
S3_BUCKET=brownfield-push