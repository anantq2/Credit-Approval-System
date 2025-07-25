from django.core.management.base import BaseCommand
from customers.models import Customer

class Command(BaseCommand):
    help = 'Update approved_limit for existing customers based on monthly_income'

    def handle(self, *args, **options):
        customers = Customer.objects.all()
        updated_count = 0
        for customer in customers:
            # Assuming monthly_income was ingested from Excel; if it's 0, skip or set placeholder
            if customer.monthly_income > 0:  # Only update if income is set
                customer.approved_limit = round(36 * customer.monthly_income / 100000) * 100000
                customer.save()
                updated_count += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} customers'))
