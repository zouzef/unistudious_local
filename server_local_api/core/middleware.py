from functools import wraps
from flask import request, jsonify
import jwt
from config import Config


def token_required(f):
    """Decorator to protect routes with JWT authentication"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]

            # Decode token
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            request.user = data['user']

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated