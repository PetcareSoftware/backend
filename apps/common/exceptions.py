from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


class BusinessRuleError(APIException):
    """Business-rule exception whose HTTP status can be set per instance.

    Subclassing DRF's APIException makes the status reliable even when the
    exception is handled by DRF's default exception machinery instead of the
    project-level custom handler. This prevents 409/403/400 business errors
    from being collapsed into the default 422.
    """

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'La operación no cumple una regla de negocio.'
    default_code = 'business_rule_error'

    def __init__(self, detail=None, status_code=None, code=None):
        if status_code is not None:
            self.status_code = int(status_code)
        super().__init__(detail=detail or self.default_detail, code=code or self.default_code)


class SlotNotAvailableError(BusinessRuleError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'El slot seleccionado ya no está disponible.'
    default_code = 'slot_not_available'


class PetNotOwnedByUserError(BusinessRuleError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'La mascota no pertenece al propietario autenticado.'
    default_code = 'pet_not_owned_by_user'


def petcare_exception_handler(exc, context):
    if isinstance(exc, BusinessRuleError):
        detail = exc.detail
        if isinstance(detail, dict):
            payload = detail
        elif isinstance(detail, list):
            payload = {'detail': detail}
        else:
            payload = {'detail': str(detail)}
        return Response(payload, status=exc.status_code)
    return exception_handler(exc, context)
