from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def pet_medical_record_summary(request, pet_id):
    """
    GET /api/v1/pets/{pet_id}/medical-record/summary/
    Vista rápida y resumida del estado del paciente (alergias, enfermedades crónicas, última consulta).
    """
    return Response({'message': f'medical record summary for pet {pet_id} stub'})

@api_view(['GET'])
def pet_medical_record(request, pet_id):
    """
    GET /api/v1/pets/{pet_id}/medical-record/
    Expediente clínico completo con el historial de todas las visitas pasadas.
    """
    return Response({'message': f'full medical record for pet {pet_id} stub'})

@api_view(['GET'])
def pet_vaccination_schedule(request, pet_id):
    """
    GET /api/v1/pets/{pet_id}/vaccination-plan/schedule/
    Ver el cronograma de vacunas (aplicadas y próximas) de un paciente.
    """
    return Response({'message': f'vaccination schedule for pet {pet_id} stub'})

@api_view(['POST'])
def pet_vaccination_events(request, pet_id):
    """
    POST /api/v1/pets/{pet_id}/vaccination-events/
    Registrar que se le ha aplicado una vacuna a la mascota en ese momento.
    """
    return Response({'message': f'register vaccination event for pet {pet_id} stub'})
