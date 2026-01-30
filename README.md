# Patient Encounter API

HIPAA-compliant REST API for managing patient encounter records.

**Requires**: Python 3.11+

## Setup

```bash
make init
```

This will:
- Copy `config.example.yml` to `config.yml`
- Copy `.env.example` to `.env`
- Create a virtual environment
- Install dependencies

## Run

```bash
make run
```

Server starts at http://localhost:8000

## API Docs

With server running, visit http://localhost:8000/docs for interactive API documentation.

## Test

```bash
make test
```

## Configuration

**config.yml** - Encounter types (extensible without code changes)

**\.env** - API keys in format `key:user_id:name,key2:user_id2:name2`

## Production Considerations

This is a demo implementation. For production:

- **Database**: Replace in-memory storage with PostgreSQL or similar
- **Authentication**: Use OAuth2/JWT instead of API keys and use a managed auth provider like AWS Cognito or Firebase. JWT short lived access tokens are more secure
- **Access Controls**: Implement role-based access (e.g., providers see only their patients, only admins can view audit logs)
- **HTTPS**: Terminate TLS at load balancer or reverse proxy
- **Rate Limiting**: Add rate limiting middleware to prevent abuse
- **Logging**: Configure structured logging with log aggregation (CloudWatch, Datadog)
- **PHI Sanitization**: If we add more than request logging or Postgres make sure that our
redaction strategy supports those cases
- **Encryption**: Encrypt PHI at rest and in transit
- **API Versioning**: Version the API (e.g., `/v1/encounters`) for backwards compatibility
- **Exception Handling**: Add global exception handler to catch unexpected errors and return generic messages (avoid PHI in stack traces)
- **Staging Environment**: Verify all changes in staging with production-like data before deploying
