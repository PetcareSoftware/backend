from rest_framework.decorators import api_view
from rest_framework.response import Response

# Vets & Schedules
@api_view(['GET'])
def vet_slots(request, vet_id):
    """
    GET /api/v1/vets/{vet_id}/slots/
    Consultar los horarios (huecos) disponibles de un veterinario específico.
    """
    return Response({})

@api_view(['GET'])
def schedule_calendar(request):
    """
    GET /api/v1/schedules/calendar/
    Consultar un calendario unificado con los horarios y citas de todos los veterinarios.
    """
    return Response({})

# Appointments
@api_view(['GET', 'POST'])
def appointment_list(request):
    """
    GET /api/v1/appointments/?date=today&vet_id=3
    Listar y filtrar citas médicas por fecha o veterinario.

    POST /api/v1/appointments/
    Crear una nueva cita para un paciente con un veterinario específico.
    """
    return Response({})

@api_view(['POST'])
def appointment_cancel(request, appointment_id):
    """
    POST /api/v1/appointments/{appointment_id}/cancel/
    Cancelar una cita programada.
    """
    return Response({})

@api_view(['POST'])
def appointment_confirm(request, appointment_id):
    """
    POST /api/v1/appointments/{appointment_id}/confirm/
    Confirmar que el paciente asistirá a la cita programada (estado CONFIRMED).
    """
    return Response({})

# Dashboard & Waiting List
@api_view(['POST'])
def appointment_check_in(request, appointment_id):
    """
    POST /api/v1/appointments/{appointment_id}/check-in/
    Registrar que el paciente ha llegado a la clínica (estado CHECKED_IN).
    """
    return Response({})

@api_view(['GET'])
def waiting_list(request):
    """
    GET /api/v1/waiting-list/
    Consultar la lista en tiempo real de los pacientes que están en la sala de espera.
    """
    return Response({})

@api_view(['POST'])
def waiting_list_call_next(request, queue_id):
    """
    POST /api/v1/waiting-list/{queue_id}/call-next/
    El veterinario llama al siguiente paciente de la lista para ingresar al consultorio.
    """
    return Response({})

# Consultations
@api_view(['POST'])
def appointment_consultations(request, appointment_id):
    """
    POST /api/v1/appointments/{appointment_id}/consultations/
    Guardar las notas clínicas, el diagnóstico y las recetas médicas al finalizar una consulta.
    """
    return Response({})

@api_view(['POST'])
def consultation_supplies_used(request, consultation_id):
    """
    POST /api/v1/consultations/{consultation_id}/supplies-used/
    Registrar qué insumos del inventario se consumieron durante esa consulta.
    """
    return Response({})
