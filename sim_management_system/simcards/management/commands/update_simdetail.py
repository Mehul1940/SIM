import pandas as pd
from django.core.management.base import BaseCommand
from simcards.models import SimCard, Department
from django.utils import timezone


class Command(BaseCommand):
    help = 'Update SIM details like vehicle info, device info, odometer, and last connected time from Excel'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to Excel file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            df = pd.read_excel(file_path, dtype=str)
        except Exception as e:
            self.stderr.write(f"❌ Failed to read Excel file: {e}")
            return

        df.columns = df.columns.str.strip().str.lower()

        updated = 0
        not_found = 0
        dept_not_found = 0

        def safe_strip(val):
            return str(val).strip() if pd.notnull(val) else ''

        for index, row in df.iterrows():
            mobile_number = safe_strip(row.get('mobile_number'))
            if not mobile_number:
                self.stderr.write(f"[Row {index + 2}] ⚠️ Missing mobile_number. Skipping.")
                continue

            try:
                sim = SimCard.objects.get(mobile_number__iexact=mobile_number)

                sim.vehicle_reg_no = safe_strip(row.get('vehicle_reg_no'))
                sim.transporter_name = safe_strip(row.get('transporter_name'))
                sim.device_company = safe_strip(row.get('device_company'))
                sim.imei_number = safe_strip(row.get('imei_number'))

                # Parse odometer
                odo_val = row.get('starting_odo_meter')
                try:
                    sim.starting_odo_meter = int(str(odo_val).strip()) if pd.notnull(odo_val) and str(odo_val).strip().isdigit() else None
                except Exception:
                    sim.starting_odo_meter = None
                    self.stderr.write(f"[Row {index + 2}] ⚠️ Invalid odometer value.")

                # Handle last_connected with timezone
                last_connected_raw = row.get('last_connected')
                dt = pd.to_datetime(last_connected_raw, errors='coerce') if pd.notnull(last_connected_raw) else None
                if pd.notnull(dt):
                    try:
                        sim.last_connected = timezone.make_aware(dt, timezone.get_current_timezone())
                    except Exception as e:
                        sim.last_connected = None
                        self.stderr.write(f"[Row {index + 2}] ⚠️ Timezone conversion failed: {e}")
                else:
                    sim.last_connected = None

                # Department linking
                dept_name = safe_strip(row.get('department'))
                if dept_name:
                    try:
                        department = Department.objects.get(name__iexact=dept_name)
                        sim.department = department
                    except Department.DoesNotExist:
                        dept_not_found += 1
                        self.stderr.write(f"[Row {index + 2}] ⚠️ Department not found: {dept_name}")
                else:
                    self.stderr.write(f"[Row {index + 2}] ⚠️ Missing department name.")

                sim.save()
                updated += 1
                self.stdout.write(f"[Row {index + 2}] ✅ Updated SIM: {mobile_number}")

            except SimCard.DoesNotExist:
                not_found += 1
                self.stderr.write(f"[Row {index + 2}] ❌ SIM not found for mobile_number: {mobile_number}")

        # Final summary
        self.stdout.write(f"\n✅ Update Complete: {updated} SIM(s) updated.")
        self.stdout.write(f"❌ SIM(s) not found: {not_found}")
        self.stdout.write(f"⚠️ Department(s) not found: {dept_not_found}")
