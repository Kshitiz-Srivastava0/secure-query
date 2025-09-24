# Secure Query

A Python library for encrypting query payloads in the frontend and decrypting them in FastAPI backends using RSA-OAEP encryption. Protects sensitive query parameters during transmission.

## Features

- = **RSA-OAEP Encryption** with SHA-256 for secure payload transmission
- =� **FastAPI Integration** with ready-to-use router endpoints
- =� **Security Hardened** with rate limiting and input validation
- = **Automatic Key Management** - generates keypairs if missing
- < **Frontend Ready** - works with any JavaScript frontend
-  **100% Test Coverage** with comprehensive security tests

## Installation

```bash
pip install secure-query

# For FastAPI integration
pip install secure-query[fastapi]
```

## Quick Start

### Backend (FastAPI)

```python
from fastapi import FastAPI
from secure_query import router

app = FastAPI()
app.include_router(router)

# Keys are automatically generated on first run
# Available endpoints:
# GET /secure-query/public-key - Get public key for frontend
# GET /secure-query/decrypt?data=<encrypted> - Decrypt payload
```

### Frontend (JavaScript)

```javascript
// 1. Get the public key from your API
const response = await fetch('/secure-query/public-key');
const { pem } = await response.json();

// 2. Encrypt your sensitive data
async function encryptPayload(data, publicKeyPem) {
    // Import the public key
    const publicKey = await crypto.subtle.importKey(
        'spki',
        pemToArrayBuffer(publicKeyPem),
        {
            name: 'RSA-OAEP',
            hash: 'SHA-256'
        },
        false,
        ['encrypt']
    );

    // Encrypt the JSON payload
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(JSON.stringify(data));
    const encryptedBuffer = await crypto.subtle.encrypt(
        { name: 'RSA-OAEP' },
        publicKey,
        dataBuffer
    );

    // Convert to base64url for URL transmission
    return arrayBufferToBase64Url(encryptedBuffer);
}

// 3. Send encrypted data to your API
const sensitiveData = { userId: 123, query: "SELECT * FROM users" };
const encrypted = await encryptPayload(sensitiveData, pem);
const result = await fetch(`/secure-query/decrypt?data=${encrypted}`);
const decrypted = await result.json();
console.log(decrypted.payload); // Your original data
```

### Helper Functions for Frontend

```javascript
// Convert PEM to ArrayBuffer
function pemToArrayBuffer(pem) {
    const b64Lines = pem.replace(/-----[^-]+-----/g, '').replace(/\s/g, '');
    const binaryString = atob(b64Lines);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}

// Convert ArrayBuffer to base64url
function arrayBufferToBase64Url(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

// Complete encryption function
async function secureQueryEncrypt(data) {
    const response = await fetch('/secure-query/public-key');
    const { pem } = await response.json();

    const publicKey = await crypto.subtle.importKey(
        'spki',
        pemToArrayBuffer(pem),
        { name: 'RSA-OAEP', hash: 'SHA-256' },
        false,
        ['encrypt']
    );

    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(JSON.stringify(data));
    const encryptedBuffer = await crypto.subtle.encrypt(
        { name: 'RSA-OAEP' },
        publicKey,
        dataBuffer
    );

    return arrayBufferToBase64Url(encryptedBuffer);
}
```

## React Hook Example

```javascript
import { useState, useCallback } from 'react';

export function useSecureQuery() {
    const [publicKey, setPublicKey] = useState(null);

    const getPublicKey = useCallback(async () => {
        if (!publicKey) {
            const response = await fetch('/secure-query/public-key');
            const { pem } = await response.json();
            setPublicKey(pem);
            return pem;
        }
        return publicKey;
    }, [publicKey]);

    const encrypt = useCallback(async (data) => {
        const pem = await getPublicKey();
        // Use the encryption logic from above
        return await secureQueryEncrypt(data);
    }, [getPublicKey]);

    const query = useCallback(async (data) => {
        const encrypted = await encrypt(data);
        const response = await fetch(`/secure-query/decrypt?data=${encrypted}`);
        const result = await response.json();
        return result.payload;
    }, [encrypt]);

    return { encrypt, query };
}

// Usage in component
function MyComponent() {
    const { query } = useSecureQuery();

    const handleSecureQuery = async () => {
        const result = await query({
            userId: 123,
            sensitiveQuery: "SELECT * FROM sensitive_table"
        });
        console.log(result);
    };

    return <button onClick={handleSecureQuery}>Secure Query</button>;
}
```

## Advanced Usage

### Custom Configuration

```python
from secure_query import Settings
from secure_query.crypto import ensure_keys, decrypt_b64url_payload

# Custom keys directory
settings = Settings("/path/to/custom/keys")
ensure_keys()  # Generate keys in custom location

# Environment variable configuration
# Set SECURE_QUERY_KEYS_DIR=/path/to/keys
```

### Manual Decryption

```python
from secure_query import decrypt_b64url_payload

# Decrypt without FastAPI
try:
    payload = decrypt_b64url_payload(encrypted_data)
    print(payload)  # Your original data
except Exception:
    print("Decryption failed")
```

### Custom FastAPI Integration

```python
from fastapi import FastAPI, Query, HTTPException, Request
from secure_query.crypto import ensure_keys, get_public_key_pem, decrypt_b64url_payload

app = FastAPI()
ensure_keys()

@app.get("/my-public-key")
def get_public_key():
    return {"key": get_public_key_pem()}

@app.post("/my-decrypt")
def decrypt_data(request: Request, data: str = Query(..., max_length=4096)):
    try:
        payload = decrypt_b64url_payload(data)
        return {"success": True, "data": payload}
    except Exception:
        raise HTTPException(status_code=400, detail="Decryption failed")
```

## Security Features

### Built-in Protection

- **Rate Limiting**: 10 requests/minute per IP on decrypt endpoint
- **Input Validation**: 4KB maximum payload size
- **Generic Error Messages**: No information disclosure
- **RSA-2048 Keys**: Industry standard encryption strength
- **Base64URL Encoding**: URL-safe transmission

### Security Considerations

- **Key Storage**: Private keys stored unencrypted (standard for application keys)
- **Rate Limiting**: In-memory storage - use Redis for production clusters
- **Payload Size**: RSA-2048 OAEP limits payloads to ~190 bytes
- **HTTPS Required**: Always use HTTPS in production
- **Key Rotation**: Implement key rotation for long-running applications

## API Reference

### Endpoints

#### GET /secure-query/public-key

Returns the RSA public key for client-side encryption.

**Response:**
```json
{
    "alg": "RSA-OAEP-256",
    "format": "spki-pem",
    "pem": "-----BEGIN PUBLIC KEY-----\n..."
}
```

#### GET /secure-query/decrypt?data={encrypted}

Decrypts base64url-encoded RSA-OAEP ciphertext.

**Parameters:**
- `data` (string): Base64url-encoded encrypted payload (max 4096 chars)

**Response:**
```json
{
    "ok": true,
    "payload": { /* your decrypted data */ }
}
```

**Error Responses:**
- `400`: Decryption failed (generic message for security)
- `422`: Invalid input (validation error)
- `429`: Rate limit exceeded

### Functions

#### `ensure_keys()`
Generates RSA keypair if missing. Safe to call multiple times.

#### `get_public_key_pem() -> str`
Returns public key in PEM format.

#### `decrypt_b64url_payload(data: str) -> dict`
Decrypts base64url payload and returns original data.

## Testing

```bash
# Install with test dependencies
pip install -e .[test]

# Run tests
pytest -v

# Run with coverage
pytest --cov=secure_query --cov-report=html
```

## Examples

### Complete Full-Stack Example

**Backend (`main.py`):**
```python
from fastapi import FastAPI
from secure_query import router

app = FastAPI(title="Secure Query Demo")
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Secure Query API Ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Frontend (`index.html`):**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Secure Query Demo</title>
</head>
<body>
    <h1>Secure Query Demo</h1>
    <button onclick="testSecureQuery()">Test Secure Query</button>
    <div id="result"></div>

    <script>
        // Add the helper functions here (from above)

        async function testSecureQuery() {
            const data = {
                user: "alice",
                query: "SELECT * FROM sensitive_data",
                timestamp: new Date().toISOString()
            };

            try {
                const encrypted = await secureQueryEncrypt(data);
                const response = await fetch(`/secure-query/decrypt?data=${encrypted}`);
                const result = await response.json();

                document.getElementById('result').innerHTML =
                    `<pre>${JSON.stringify(result.payload, null, 2)}</pre>`;
            } catch (error) {
                console.error('Encryption/Decryption failed:', error);
                document.getElementById('result').innerHTML = 'Error: ' + error.message;
            }
        }
    </script>
</body>
</html>
```

## Publishing to PyPI

To make this package globally accessible, you can publish it to PyPI:

### Prerequisites

1. **Create PyPI Account**: Register at [pypi.org](https://pypi.org/account/register/)
2. **Create TestPyPI Account**: Register at [test.pypi.org](https://test.pypi.org/account/register/) for testing
3. **Configure API Tokens**:
   ```bash
   # Create API tokens in your PyPI account settings
   # Configure them in ~/.pypirc or use environment variables
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-your-api-token-here
   ```

### Quick Publish

```bash
# Test upload to TestPyPI first
python publish.py --test

# Production upload to PyPI
python publish.py
```

### Manual Publishing Steps

```bash
# 1. Install build tools
pip install build twine

# 2. Run tests to ensure everything works
pytest -v

# 3. Build the package
python -m build

# 4. Check the package
python -m twine check dist/*

# 5. Upload to TestPyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# 6. Test install from TestPyPI
pip install -i https://test.pypi.org/simple/ secure-query

# 7. Upload to production PyPI
python -m twine upload dist/*
```

### After Publishing

Once published, anyone can install your package globally:

```bash
# Global installation
pip install secure-query

# With FastAPI support
pip install secure-query[fastapi]

# Development installation
pip install secure-query[test]
```

### Package Management

- **Update Version**: Edit `version` in `pyproject.toml`
- **Update Dependencies**: Modify `dependencies` in `pyproject.toml`
- **Add Features**: Update `CHANGELOG.md` with changes
- **Security Updates**: Follow semantic versioning for patches

### GitHub Integration

1. **Create Repository**: Push code to GitHub
2. **Update URLs**: Change GitHub URLs in `pyproject.toml`
3. **Set Up Actions**: Use provided workflow for automated publishing
4. **Release Management**: Create GitHub releases for versions

### Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine pytest
        pip install -e .[test]

    - name: Run tests
      run: pytest -v

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: python -m twine upload dist/*
```

### Distribution Statistics

After publishing, monitor your package:

- **PyPI Stats**: View download statistics on PyPI
- **GitHub Insights**: Track repository stars and forks
- **Issue Tracking**: Monitor bug reports and feature requests
- **Security Alerts**: Stay informed about dependency vulnerabilities

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure 100% test coverage
5. Submit a pull request

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/secure-query.git
cd secure-query

# Install in development mode
pip install -e .[test]

# Run tests
pytest -v

# Check coverage
pytest --cov=secure_query --cov-report=html
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### v0.1.0
- Initial release
- RSA-OAEP encryption/decryption
- FastAPI integration
- Rate limiting and security hardening
- Comprehensive test suite
- Frontend integration examples