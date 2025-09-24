# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-09-24

### Added
- Initial release of secure-query
- RSA-OAEP encryption/decryption functionality
- FastAPI router integration with `/public-key` and `/decrypt` endpoints
- Automatic RSA keypair generation and management
- Rate limiting (10 requests/minute per IP) for decrypt endpoint
- Input validation with 4KB payload size limit
- Generic error messages to prevent information disclosure
- Comprehensive test suite with 100% code coverage
- Security edge case testing
- Base64URL encoding for URL-safe transmission
- Frontend JavaScript integration examples
- React hook for easy component integration
- Complete documentation with usage examples

### Security Features
- RSA-2048 key generation with OAEP-SHA256 padding
- Per-IP rate limiting with configurable windows
- Input sanitization and validation
- No sensitive information in error messages
- Secure key storage and management
- Protection against oversized payload attacks

### Dependencies
- `cryptography>=42,<45` - Core encryption functionality
- `fastapi>=0.110,<1.0` - Optional FastAPI integration
- `pytest>=7.0` - Testing framework (dev dependency)
- `pytest-cov>=4.0` - Coverage reporting (dev dependency)
- `httpx>=0.24.0` - HTTP client for testing (dev dependency)

### Documentation
- Complete README with usage instructions
- Frontend integration examples (JavaScript, React)
- API reference documentation
- Security considerations and best practices
- Full-stack example application