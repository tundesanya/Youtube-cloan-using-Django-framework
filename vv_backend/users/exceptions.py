from rest_framework import status
from rest_framework.serializers import ValidationError

class UserUpdateValidationMessage(ValidationError):
    def __init__(self, detail=None, code=None, status_code=None):
        # Default status code set in ValidationError is 400
        self.status_code = status_code if status_code else status.HTTP_400_BAD_REQUEST
        self = super().__init__(detail, code)

