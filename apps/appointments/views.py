from rest_framework.decorators import api_view
from rest_framework.response import Response

# Vets & Schedules
@api_view(['GET'])
def vet_slots(request, vet_id):
    """
    GET /api/v1/vets/{vet_id}/slots/
    Consultar los horarios (huecos) disponibles de un veterinario específico.
    """
    return Response({'message': f'slots for vet {vet_id} stub'})

@api_view(['GET'])
def schedule_calendar(request):
    """
    GET /api/v1/schedules/calendar/
    Consultar un calendario unificado con los horarios y citas de todos los veterinarios.
    """
    return Response({'message': 'calendar stub'})

# Appointments
@api_view(['POST'])
def appointment_list(request):
    """
    POST /api/v1/appointments/
    Crear una nueva cita para un paciente con un veterinario específico.
    """
    return Response({'message': 'create appointment stub'})

@api_view(['POST'])
def appointment_cancel(request, id):
    """
    POST /api/v1/appointments/{id}/cancel/
    Cancelar una cita programada.
    """
    return Response({'message': f'cancel appointment {id} stub'})

@api_view(['POST'])
def appointment_confirm(request, id):
    """
    POST /api/v1/appointments/{id}/confirm/
    Confirmar que el paciente asistirá a la cita programada (estado CONFIRMED).
    """
    return Response({'message': f'confirm appointment {id} stub'})

# Dashboard & Waiting List
@api_view(['GET'])
def appointments_today(request):
    """
    GET /api/v1/appointments/today/
    Obtener todas las citas del día actual (para dashboard de recepción).
    """
    return Response({'message': 'appointments today stub'})

@api_view(['GET'])
def appointments_today_by_vet(request, vet_id):
    """
    GET /api/v1/appointments/today/by-vet/{vet_id}/
    Filtrar las citas del día actual asignadas únicamente a un veterinario en específico.
    """
    return Response({'message': f'appointments today for vet {vet_id} stub'})

@api_view(['POST'])
def appointment_check_in(request, id):
    """
    POST /api/v1/appointments/{id}/check-in/
    Registrar que el paciente ha llegado a la clínica (estado CHECKED_IN).
    """
    return Response({'message': f'check-in appointment {id} stub'})

@api_view(['GET'])
def waiting_list(request):
    """
    GET /api/v1/waiting-list/
    Consultar la lista en tiempo real de los pacientes que están en la sala de espera.
    """
    return Response({'message': 'waiting list today stub'})

@api_view(['POST'])
def waiting_list_call_next(request, id):
    """
    POST /api/v1/waiting-list/{id}/call-next/
    El veterinario llama al siguiente paciente de la lista para ingresar al consultorio.
    """
    return Response({'message': f'call next patient for waiting list {id} stub'})

# Consultations
@api_view(['POST'])
def appointment_consultations(request, id):
    """
    POST /api/v1/appointments/{id}/consultations/
    Guardar las notas clínicas, el diagnóstico y las recetas médicas al finalizar una consulta.
    """
    return Response({'message': f'register consultation for appointment {id} stub'})

@api_view(['POST'])
def consultation_supplies_used(request, id):
    """
    POST /api/v1/consultations/{id}/supplies-used/
    Registrar qué insumos del inventario se consumieron durante esa consulta.
    """
    return Response({'message': f'register supplies for consultation {id} stub'})
