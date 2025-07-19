import pandas as pd
from decimal import Decimal
from django.core.management.base import BaseCommand
from simcards.models import SimCard, SimType, SimStatus, PlanType
from carriers.models import Carrier
from departments.models import Department
from django.utils.dateparse import parse_datetime
import ipaddress


class Command(BaseCommand):
    help = 'Import SIM card data from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        try:
            df = pd.read_excel(file_path, dtype=str)
            df.columns = df.columns.str.strip().str.lower()

            print("Detected columns:", df.columns.tolist())

            for index, row in df.iterrows():
                # --- ICCID ---
                raw_iccid = row.get('iccid_number')
                if pd.isna(raw_iccid):
                    iccid_number = None
                    self.stderr.write(f"[Row {index + 2}] Missing iccid_number. Setting to NULL.")
                else:
                    try:
                        iccid_number = str(Decimal(str(raw_iccid)).quantize(Decimal('1'))).strip()
                    except Exception:
                        self.stderr.write(f"[Row {index + 2}] Invalid iccid_number format: {raw_iccid}. Setting to NULL.")
                        iccid_number = None

                # --- Mobile ---
                mobile_number = row.get('mobile_number')
                if pd.isna(mobile_number) or not str(mobile_number).strip():
                    self.stderr.write(f"[Row {index + 2}] Missing mobile_number. Skipping.")
                    continue
                mobile_number = str(mobile_number).strip()

                # --- Carrier ---
                carrier = None
                carrier_name = row.get('carrier')
                if pd.notna(carrier_name):
                    carrier = Carrier.objects.filter(name__iexact=carrier_name.strip()).first()

                # --- Last connected ---
                last_connected = row.get('last_connected')
                last_connected = parse_datetime(last_connected) if pd.notna(last_connected) else None

                # --- Odometer ---
                try:
                    starting_odo_meter = int(row.get('starting_odo_meter')) if pd.notna(row.get('starting_odo_meter')) else None
                except ValueError:
                    starting_odo_meter = None

                # --- IP ---
                current_ip = row.get('current_ip')
                if current_ip and pd.notna(current_ip):
                    try:
                        ipaddress.ip_address(current_ip.strip())
                        current_ip_clean = current_ip.strip()
                    except ValueError:
                        current_ip_clean = None
                else:
                    current_ip_clean = None

                # --- Enums ---
                sim_status_raw = row.get('sim_status', '').strip() if pd.notna(row.get('sim_status')) else ''
                sim_status = sim_status_raw if sim_status_raw in SimStatus.values else SimStatus.AVAILABLE

                sim_type_raw = row.get('sim_type', '').strip().capitalize() if pd.notna(row.get('sim_type')) else ''
                sim_type = sim_type_raw if sim_type_raw in SimType.values else SimType.OTHER

                plan_type_raw = row.get('plan_type', '').strip().upper() if pd.notna(row.get('plan_type')) else ''
                plan_type = plan_type_raw if plan_type_raw in PlanType.values else None

                # --- Department (get_or_create!) ---
                dept_name = row.get('department')
                department_instance = None
                if dept_name and pd.notna(dept_name) and str(dept_name).strip():
                    name_clean = str(dept_name).strip()
                    department_instance, created = Department.objects.get_or_create(
                        name__iexact=name_clean,
                        defaults={'name': name_clean}
                    )
                    if created:
                        self.stdout.write(f"[Row {index + 2}] Created new Department: {name_clean}")

                # --- Save or update SIMCard ---
                SimCard.objects.update_or_create(
                    mobile_number=mobile_number,
                    defaults={
                        'iccid_number': iccid_number,
                        'imsi_number': row.get('imsi_number'),
                        'basket_name': row.get('basket_name'),
                        'sim_status': sim_status,
                        'plan_name': row.get('plan_name'),
                        'plan_type': plan_type,
                        'sim_type': sim_type,
                        'imei_number': row.get('imei_number'),
                        'current_ip': current_ip_clean,
                        'last_connected': last_connected,
                        'action': row.get('action'),
                        'new_sim_number': row.get('new_sim_number'),
                        'reason': row.get('reason'),
                        'remark1': row.get('remark1'),
                        'remark2': row.get('remark2'),
                        'remark3': row.get('remark3'),
                        'carrier': carrier,
                        'vehicle_reg_no': row.get('vehicle_reg_no'),
                        'transporter_name': row.get('transporter_name'),
                        'device_company': row.get('device_company'),
                        'starting_odo_meter': starting_odo_meter,
                        'department': department_instance,    
                    }
                )

            self.stdout.write(self.style.SUCCESS('SIM cards imported successfully.'))

        except Exception as e:
            self.stderr.write(f'Error: {str(e)}')
