import pandas as pd
from django.core.management.base import BaseCommand
from simcards.models import SimCard, SimStatus


class Command(BaseCommand):
    help = 'Update SIM status using a file and a given status (e.g., DEACTIVE, ACTIVE)'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to Excel file')
        parser.add_argument('target_status', type=str, help='Target status (must match SimStatus)')

    def handle(self, *args, **options):
        file_path = options['file_path']
        target_status_raw = options['target_status'].strip()

        # Validate target status
        valid_status = next((s for s in SimStatus.values if s.lower() == target_status_raw.lower()), None)
        if not valid_status:
            self.stderr.write(f"❌ Error: '{target_status_raw}' is not a valid SimStatus. Valid options are: {SimStatus.values}")
            return

        try:
            df = pd.read_excel(file_path, dtype=str)
            df.columns = df.columns.str.strip().str.lower()

            if 'vehicle no' not in df.columns:
                self.stderr.write("❌ Excel must contain a 'Vehicle No' column.")
                return

            updated = 0
            skipped = 0
            not_found = 0

            for index, row in df.iterrows():
                vehicle_no = str(row.get('vehicle no')).strip().upper()

                if not vehicle_no:
                    self.stderr.write(f"[Row {index + 2}] Missing Vehicle No. Skipping.")
                    continue

                try:
                    sim = SimCard.objects.get(vehicle_reg_no__iexact=vehicle_no)
                    if sim.sim_status != valid_status:
                        sim.sim_status = valid_status
                        sim.save()
                        updated += 1
                        self.stdout.write(f"[Row {index + 2}] Updated {vehicle_no} to {valid_status}")
                    else:
                        skipped += 1
                except SimCard.DoesNotExist:
                    not_found += 1
                    self.stderr.write(f"[Row {index + 2}] Vehicle not found: {vehicle_no}")

            self.stdout.write(self.style.SUCCESS(
                f"✅ Done: {updated} updated, {skipped} skipped (already correct), {not_found} not found."
            ))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error: {str(e)}"))
