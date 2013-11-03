from django.core.management.base import BaseCommand, CommandError
from services.models import ServiceModel

class Command(BaseCommand):
	help = 'Pings all services and updates their history'
	args = '<should_force_ping>'

	def handle(self, *args, **options):
		"""
		Executes the ``python manage.py pingservices`` command.
		To force a ping of all services use ``python manage.py pingservices forceping`` 
		"""
		force_ping = False
		if args:
			force_ping = True

		will_be_pinging_all = 'Will' if force_ping else 'Will not'
		self.stdout.write(will_be_pinging_all + ' be force ping of all services.')
		self.stdout.write('Current Status:')

		for service in ServiceModel.objects.all():
			service.ping(force_ping)
			is_up = 'up.' if service.is_up else 'down.'
			self.stdout.write('    ' + service.name + ' in group ' + service.service_group.name + ' is ' + is_up)

		self.stdout.write('Finished checking the health of services.')