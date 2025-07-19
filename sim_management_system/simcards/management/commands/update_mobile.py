import pandas as pd
from django.core.management.base import BaseCommand
from simcards.models import SimCard, SimStatus

class Command(BaseCommand):
    help = 'Update SIM card data based on mobile_number from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to Excel file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            df = pd.read_excel(file_path, dtype=str)
            df.columns = df.columns.str.strip().str.lower()

            required_columns = [
                'mobile_number', 'iccid_number', 'imsi_number', 'basket_name',
                'sim_status', 'plan_name', 'plan_type'
            ]
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                self.stderr.write(f"❌ Missing columns in Excel: {', '.join(missing_cols)}")
                return

            updated = 0
            not_found = 0
            invalid_status = 0

            for index, row in df.iterrows():
                mobile_number = str(row['mobile_number']).strip()
                if not mobile_number:
                    self.stderr.write(f"[Row {index + 2}] Missing mobile_number. Skipping.")
                    continue

                try:
                    sim = SimCard.objects.get(mobile_number__iexact=mobile_number)

                    # Validate and set sim_status
                    status_raw = str(row['sim_status']).strip()
                    sim_status_valid = next((s for s in SimStatus.values if s.lower() == status_raw.lower()), None)
                    if not sim_status_valid:
                        self.stderr.write(f"[Row {index + 2}] Invalid sim_status: '{status_raw}'. Skipping.")
                        invalid_status += 1
                        continue

                    # Update fields
                    sim.iccid_number = str(row['iccid_number']).strip()
                    sim.imsi_number = str(row['imsi_number']).strip()
                    sim.basket_name = str(row['basket_name']).strip()
                    sim.sim_status = sim_status_valid
                    sim.plan_name = str(row['plan_name']).strip()
                    sim.plan_type = str(row['plan_type']).strip()
                    sim.save()

                    updated += 1
                    self.stdout.write(f"[Row {index + 2}] ✅ Updated SIM for mobile: {mobile_number}")

                except SimCard.DoesNotExist:
                    self.stderr.write(f"[Row {index + 2}] ❌ SIM not found for mobile_number: {mobile_number}")
                    not_found += 1

            self.stdout.write(self.style.SUCCESS(
                f"✅ Done: {updated} updated, {not_found} not found, {invalid_status} rows skipped due to invalid status."
            ))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error: {str(e)}"))
