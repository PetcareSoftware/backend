from unittest.mock import patch

from rest_framework import status

from apps.appointments.models import Appointment
from apps.appointments.tasks import request_attendance_confirmation, send_appointment_reminder
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService
from tests.base import PetCareAPITestCase, PetCareAPITransactionTestCase


class NotificationTests(PetCareAPITestCase):
    def test_confirm_scheduled_and_cancelled_422(self):
        res = self.create_appointment()
        appointment_id = res.data['id']
        self.auth(self.owner_user)
        confirmed = self.client.post(f'/api/v1/appointments/{appointment_id}/confirm/')
        self.assertEqual(confirmed.status_code, status.HTTP_200_OK)
        cancelled = Appointment.objects.get(id=appointment_id)
        cancelled.status = Appointment.Status.CANCELLED
        cancelled.save(update_fields=['status'])
        res = self.client.post(f'/api/v1/appointments/{appointment_id}/confirm/')
        self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_cancelled_before_reminder_no_notification(self):
        res = self.create_appointment()
        appointment = Appointment.objects.get(id=res.data['id'])
        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=['status'])
        send_appointment_reminder(str(appointment.id))
        request_attendance_confirmation(str(appointment.id))
        self.assertEqual(Notification.objects.filter(user=self.owner_user).count(), 0)

    def test_mark_other_notification_is_403_and_own_ok(self):
        notification = NotificationService.create(user=self.other_owner_user, title='X', message='Y')
        self.auth(self.owner_user)
        res = self.client.patch(f'/api/v1/notifications/{notification.id}/read/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        own = NotificationService.create(user=self.owner_user, title='X', message='Y')
        res = self.client.patch(f'/api/v1/notifications/{own.id}/read/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['is_read'])

    def test_notification_list_contract_filters_aliases_and_unread_count(self):
        read = NotificationService.create(user=self.owner_user, title='Read', message='Already read')
        NotificationService.mark_read(actor=self.owner_user, notification=read)
        unread = NotificationService.create(
            user=self.owner_user,
            title='Reminder',
            message='Remember appointment',
            notification_type=Notification.Type.REMINDER,
        )
        NotificationService.create(user=self.other_owner_user, title='Other', message='Hidden')

        self.auth(self.owner_user)
        listing = self.client.get('/api/v1/notifications/')
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(listing.data['unread_count'], 1)
        self.assertEqual(listing.data['count'], 2)
        self.assertEqual(listing.data['results'][0]['body'], unread.message)
        self.assertEqual(listing.data['results'][0]['type'], Notification.Type.REMINDER)

        only_unread = self.client.get('/api/v1/notifications/?is_read=false')
        self.assertEqual(only_unread.data['count'], 1)
        self.assertEqual(only_unread.data['results'][0]['id'], str(unread.id))

    def test_read_all_returns_marked_as_read(self):
        NotificationService.create(user=self.owner_user, title='One', message='Unread')
        NotificationService.create(user=self.owner_user, title='Two', message='Unread')
        self.auth(self.owner_user)

        res = self.client.patch('/api/v1/notifications/read-all/')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['marked_as_read'], 2)
        self.assertEqual(Notification.objects.filter(user=self.owner_user, is_read=False).count(), 0)


class NotificationOnCommitTests(PetCareAPITransactionTestCase):
    @patch('apps.appointments.tasks.send_appointment_reminder.apply_async')
    @patch('apps.appointments.tasks.request_attendance_confirmation.apply_async')
    def test_create_appointment_enqueues_two_celery_tasks(self, confirm_mock, reminder_mock):
        res = self.create_appointment()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(reminder_mock.called)
        self.assertTrue(confirm_mock.called)
