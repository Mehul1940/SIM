from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import DeviceReturn, DeviceDispatch, STATUS_CHOICES
from departments.models import Department
from django.utils import timezone
from itertools import chain
from django.db.models import Q
import pandas as pd
import datetime
import openpyxl
from django.http import HttpResponse
from django.utils.dateparse import parse_date 

def master_page(request):
    departments = Department.objects.all().order_by('name')
    department_id = request.GET.get('department')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_status = request.GET.get('status')
    search_query = request.GET.get('search_query', '').strip()

    dispatches = DeviceDispatch.objects.select_related('location').all()
    returns = DeviceReturn.objects.select_related('location').all()

    if department_id:
        dispatches = dispatches.filter(location_id=department_id)
        returns = returns.filter(location_id=department_id)

    if selected_status:
        dispatches = dispatches.filter(status=selected_status)
        returns = returns.filter(status=selected_status)
        
    if start_date:
        dispatches = dispatches.filter(date__gte=start_date)
        returns = returns.filter(date__gte=start_date)

    if end_date:
        dispatches = dispatches.filter(date__lte=end_date)
        returns = returns.filter(date__lte=end_date)

    if search_query:
        dispatches = dispatches.filter(
            Q(person__icontains=search_query) |
            Q(docket_number__icontains=search_query) |
            Q(parcel_sent_by__icontains=search_query) |
            Q(mobile_no__icontains=search_query) |
            Q(imei_no__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(location__name__icontains=search_query) |
            Q(city__icontains=search_query)
        ).distinct()

        returns = returns.filter(
            Q(person__icontains=search_query) |
            Q(docket_number__icontains=search_query) |
            Q(parcel_sent_by__icontains=search_query) |
            Q(mobile_no__icontains=search_query) |
            Q(imei_no__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(location__name__icontains=search_query) |
            Q(city__icontains=search_query)
        ).distinct()

    for d in dispatches:
        d.record_type = "Dispatch"
    for r in returns:
        r.record_type = "Return"

    all_records = sorted(
        chain(dispatches, returns),
        key=lambda x: x.date,
        reverse=True
    )

    context = {
        'departments': departments,
        'all_records': all_records,
        'selected_department': department_id,
        'start_date': start_date,
        'end_date': end_date,
        'search_query': search_query,
        'selected_status': selected_status,
        'status_choices': STATUS_CHOICES,
    }
    return render(request, 'stock/master.html', context)


def dispatch_item(request):
    search_query = request.GET.get('search_query', '').strip()
    selected_department = request.GET.get('department', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    dispatches = DeviceDispatch.objects.all().order_by('-date')

    if search_query:
        dispatches = dispatches.filter(
            Q(person__icontains=search_query) |
            Q(docket_number__icontains=search_query) |
            Q(parcel_sent_by__icontains=search_query) |
            Q(mobile_no__icontains=search_query) |
            Q(imei_no__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(location__name__icontains=search_query) |
            Q(city__icontains=search_query)
        ).distinct()

    if selected_department:
        dispatches = dispatches.filter(location_id=selected_department)

    if start_date:
        dispatches = dispatches.filter(date__gte=start_date)

    if end_date:
        dispatches = dispatches.filter(date__lte=end_date)

    departments = Department.objects.all().order_by('name')

    context = {
        'dispatches': dispatches,  # ✅ Correct variable name
        'departments': departments,
        'search_query': search_query,
        'selected_department': selected_department,
        'start_date': start_date,
        'end_date': end_date,
        'status_choices': STATUS_CHOICES,
    }
    return render(request, 'stock/dispatch.html', context)



def return_item(request):
    search_query = request.GET.get('search_query', '').strip()
    selected_department = request.GET.get('department', '')
    selected_city = request.GET.get('city', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    returns = DeviceReturn.objects.all().order_by('-date')

    if search_query:
        returns = returns.filter(
            Q(person__icontains=search_query) |
            Q(docket_number__icontains=search_query) |
            Q(parcel_sent_by__icontains=search_query) |
            Q(mobile_no__icontains=search_query) |
            Q(imei_no__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(location__name__icontains=search_query) |
            Q(city__icontains=search_query)
        ).distinct()

    if selected_department:
        returns = returns.filter(location_id=selected_department)

    if selected_city:
        returns = returns.filter(city__icontains=selected_city)

    if start_date:
        returns = returns.filter(date__gte=parse_date(start_date))

    if end_date:
        returns = returns.filter(date__lte=parse_date(end_date))

    departments = Department.objects.all().order_by('name')

    context = {
        'returns': returns,
        'departments': departments,
        'search_query': search_query,
        'selected_department': selected_department,
        'selected_city': selected_city,
        'start_date': start_date,
        'end_date': end_date,
        'status_choices': STATUS_CHOICES,
    }
    return render(request, 'stock/return.html', context)



def device_return(request):
    departments = Department.objects.all().order_by('name')
    status_choices = STATUS_CHOICES
    if request.method == 'POST':
        location_id = request.POST.get('location')
        city = request.POST.get('city')
        person = request.POST.get('person')
        date_str = request.POST.get('date')
        parcel_sent_by = request.POST.get('parcel_sent_by')
        docket_number = request.POST.get('docket_number')
        collected_person_name = request.POST.get('collected_person_name')
        status = request.POST.get('status')

        mobile_nos = request.POST.getlist('mobile_no[]')
        imei_nos = request.POST.getlist('imei_no[]')
        serial_numbers = request.POST.getlist('serial_number[]')

        if not all([location_id, city, person, date_str]) or not mobile_nos or not imei_nos or not serial_numbers:
            messages.error(request, "Please fill in all required fields")
            return render(request, 'stock/device_return.html', {
                'departments': departments,
                'today': date_str,
                'location_id': location_id,
                'city': city,
                'person': person,
                'mobile_nos': mobile_nos,
                'imei_nos': imei_nos,
                'serial_numbers': serial_numbers,
                'parcel_sent_by': parcel_sent_by,
                'docket_number': docket_number,
                'collected_person_name': collected_person_name,
                'status': status,
                'status_choices': status_choices,
            })

        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            for i in range(len(mobile_nos)):
                DeviceReturn.objects.create(
                    location_id=location_id,
                    city=city,
                    person=person,
                    date=date_obj,
                    mobile_no=mobile_nos[i],
                    imei_no=imei_nos[i],
                    serial_number=serial_numbers[i],
                    parcel_sent_by=parcel_sent_by,
                    docket_number=docket_number,
                    collected_person_name=collected_person_name,
                    status=status
                )
            messages.success(request, f"{len(mobile_nos)} device return record(s) added successfully.")
            return redirect('return')
        except Exception as e:
            messages.error(request, f"Error adding device return: {e}")
            return redirect('return')

    return render(request, 'stock/device_return.html', {
        'departments': departments,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'status_choices': status_choices,
    })


def device_dispatch(request):
    departments = Department.objects.all().order_by('name')
    status_choices = STATUS_CHOICES

    if request.method == 'POST':
        location_id = request.POST.get('location')
        city = request.POST.get('city')
        person = request.POST.get('person')
        date_str = request.POST.get('date')
        parcel_sent_by = request.POST.get('parcel_sent_by')
        docket_number = request.POST.get('docket_number')
        collected_person_name = request.POST.get('collected_person_name')
        status = request.POST.get('status')

        mobile_no_list = request.POST.getlist('mobile_no[]')
        imei_no_list = request.POST.getlist('imei_no[]')
        serial_number_list = request.POST.getlist('serial_number[]')

        # Validate required fields
        if not all([location_id, city, person, date_str, status]) or not mobile_no_list or not imei_no_list or not serial_number_list:
            errors = ["Please fill in all required fields."]
            return render(request, 'stock/device_dispatch.html', {
                'departments': departments,
                'today': date_str,
                'location_id': location_id,
                'city': city,
                'person': person,
                'parcel_sent_by': parcel_sent_by,
                'docket_number': docket_number,
                'collected_person_name': collected_person_name,
                'status': status,
                'mobile_no_list': mobile_no_list,
                'imei_no_list': imei_no_list,
                'serial_number_list': serial_number_list,
                'status_choices': status_choices,
                'errors': errors,
            })

        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            for i in range(len(mobile_no_list)):
                DeviceDispatch.objects.create(
                    location_id=location_id,
                    city=city,
                    person=person,
                    date=date_obj,
                    mobile_no=mobile_no_list[i],
                    imei_no=imei_no_list[i],
                    serial_number=serial_number_list[i],
                    parcel_sent_by=parcel_sent_by,
                    docket_number=docket_number,
                    collected_person_name=collected_person_name,
                    status=status
                )
            messages.success(request, f"{len(mobile_no_list)} device dispatch record(s) added successfully.")
            return redirect('dispatch')

        except Exception as e:
            messages.error(request, f"Error adding dispatch: {e}")
            return redirect('dispatch')

    return render(request, 'stock/device_dispatch.html', {
        'departments': departments,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'status_choices': status_choices,
    })



def dispatch_edit(request, pk):
    dispatch = get_object_or_404(DeviceDispatch, pk=pk)
    departments = Department.objects.all().order_by('name')
    status_choices = STATUS_CHOICES

    if request.method == 'POST':
        dispatch.location_id = request.POST.get('location')
        dispatch.city = request.POST.get('city')
        dispatch.person = request.POST.get('person')
        dispatch.date = request.POST.get('date')
        dispatch.mobile_no = request.POST.get('mobile_no')
        dispatch.imei_no = request.POST.get('imei_no')
        dispatch.serial_number = request.POST.get('serial_number')
        dispatch.parcel_sent_by = request.POST.get('parcel_sent_by')
        dispatch.docket_number = request.POST.get('docket_number')
        dispatch.collected_person_name = request.POST.get('collected_person_name')
        dispatch.status = request.POST.get('status')

        if not all([dispatch.location_id, dispatch.city, dispatch.person, dispatch.date, dispatch.mobile_no, dispatch.imei_no, dispatch.serial_number, dispatch.status]):
            messages.error(request, "Please fill in all required fields (including Status and City).")
            return redirect('dispatch')

        try:
            dispatch.save()
            messages.success(request, "Dispatch record updated successfully.")
            return redirect('dispatch')
        except Exception as e:
            messages.error(request, f"Error updating dispatch record: {e}")
            return redirect('dispatch_item')

    context = {
        'dispatch': dispatch,
        'departments': departments,
        'status_choices': status_choices,
    }
    return render(request, 'stock/dispatch_edit.html', context)


def dispatch_delete(request, pk):
    dispatch = get_object_or_404(DeviceDispatch, pk=pk)
    if request.method == 'POST':
        try:
            dispatch.delete()
            messages.success(request, "Dispatch record deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting dispatch record: {e}")
    return redirect('dispatch')


def return_edit(request, pk):
    ret = get_object_or_404(DeviceReturn, pk=pk)
    departments = Department.objects.all().order_by('name')
    status_choices = STATUS_CHOICES

    if request.method == 'POST':
        ret.location_id = request.POST.get('location')
        ret.city = request.POST.get('city')
        ret.person = request.POST.get('person')
        ret.date = request.POST.get('date')
        ret.mobile_no = request.POST.get('mobile_no')
        ret.imei_no = request.POST.get('imei_no')
        ret.serial_number = request.POST.get('serial_number')
        ret.parcel_sent_by = request.POST.get('parcel_sent_by')
        ret.docket_number = request.POST.get('docket_number')
        ret.collected_person_name = request.POST.get('collected_person_name')
        ret.status = request.POST.get('status')

        if not all([ret.location_id, ret.city, ret.person, ret.date, ret.mobile_no, ret.imei_no, ret.serial_number, ret.status]):
            messages.error(request, "Please fill in all required fields (including Status and City).")
            return redirect('return_item')

        try:
            ret.save()
            messages.success(request, "Return record updated successfully.")
            return redirect('return')
        except Exception as e:
            messages.error(request, f"Error updating return record: {e}")
            return redirect('return_item')

    context = {
        'ret': ret,
        'departments': departments,
        'status_choices': status_choices,
    }
    return render(request, 'stock/return_edit.html', context)


def return_delete(request, pk):
    ret = get_object_or_404(DeviceReturn, pk=pk)
    if request.method == 'POST':
        try:
            ret.delete()
            messages.success(request, "Return record deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting return record: {e}")
    return redirect('return')


def export_stock_excel(request):
    search_query = request.GET.get('search_query', '').strip()
    selected_department = request.GET.get('department', '')
    selected_status = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    dispatch_qs = DeviceDispatch.objects.all()
    return_qs = DeviceReturn.objects.all()

    if search_query:
        dispatch_qs = dispatch_qs.filter(
            Q(person__icontains=search_query) |
            Q(docket_number__icontains=search_query) |
            Q(parcel_sent_by__icontains=search_query) |
            Q(mobile_no__icontains=search_query) |
            Q(imei_no__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(location__name__icontains=search_query) |
            Q(city__icontains=search_query)
        )
        return_qs = return_qs.filter(
            Q(person__icontains=search_query) |
            Q(docket_number__icontains=search_query) |
            Q(parcel_sent_by__icontains=search_query) |
            Q(mobile_no__icontains=search_query) |
            Q(imei_no__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(location__name__icontains=search_query) |
            Q(city__icontains=search_query)
        )

    if selected_department:
        dispatch_qs = dispatch_qs.filter(location_id=selected_department)
        return_qs = return_qs.filter(location_id=selected_department)

    if selected_status:
        dispatch_qs = dispatch_qs.filter(status=selected_status)
        return_qs = return_qs.filter(status=selected_status)

    if start_date:
        dispatch_qs = dispatch_qs.filter(date__gte=parse_date(start_date))
        return_qs = return_qs.filter(date__gte=parse_date(start_date))

    if end_date:
        dispatch_qs = dispatch_qs.filter(date__lte=parse_date(end_date))
        return_qs = return_qs.filter(date__lte=parse_date(end_date))

    records = list(dispatch_qs) + list(return_qs)
    records.sort(key=lambda x: x.date or datetime.date.min, reverse=True)

    # Create Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Stock Records"

    headers = [
        "Type", "Department", "City", "Person", "Mobile", "IMEI", "Serial No",
        "Date", "Parcel Sent By", "Docket", "Collected Person", "Status"
    ]
    ws.append(headers)

    for rec in records:
        row = [
            "Dispatch" if isinstance(rec, DeviceDispatch) else "Return",
            rec.location.name if rec.location else '',
            rec.city or '',
            rec.person or '',
            rec.mobile_no or '',
            rec.imei_no or '',
            rec.serial_number or '',
            rec.date.strftime('%d-%m-%Y') if rec.date else '',
            rec.parcel_sent_by or '',
            rec.docket_number or '',
            rec.collected_person_name or '',
            rec.status or '',
        ]
        ws.append(row)

    # Prepare response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = "StockRecords.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'

    wb.save(response)
    return response

def import_stock_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            # Load DataFrame from Excel or CSV
            df = pd.read_excel(excel_file) if excel_file.name.endswith('.xlsx') else pd.read_csv(excel_file)

            # Map headers to model field names
            column_mapping = {
                'Type': 'record_type',
                'Department': 'location',
                'City': 'city',
                'Person': 'person',
                'Mobile': 'mobile_no',
                'IMEI': 'imei_no',
                'Serial No': 'serial_number',
                'Date': 'date',
                'Parcel Sent By': 'parcel_sent_by',
                'Docket': 'docket_number',
                'Collected Person': 'collected_person_name',
                'Status': 'status',
            }
            df.rename(columns=column_mapping, inplace=True)

            # Ensure required columns exist
            required_columns = set(column_mapping.values())
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                messages.error(request, f"Missing required columns: {', '.join(missing_columns)}")
                return redirect('master')

            # Counters for feedback
            created_count = 0
            skipped_count = 0

            for _, row in df.iterrows():
                try:
                    # Validate department
                    dept_name = str(row.get('location', '')).strip()
                    department = Department.objects.filter(name__iexact=dept_name).first()
                    if not department:
                        skipped_count += 1
                        continue

                    # Validate and clean fields
                    record_type = str(row.get('record_type', '')).strip().lower()
                    person = str(row.get('person', '')).strip()
                    mobile_no = str(row.get('mobile_no', '')).strip()
                    imei_no = str(row.get('imei_no', '')).strip()
                    serial_number = str(row.get('serial_number', '')).strip()
                    date_str = str(row.get('date', '')).strip()
                    date_val = parse_date(date_str)

                    status = str(row.get('status', '')).strip()
                    if not all([person, mobile_no, imei_no, serial_number, date_val, status]):
                        skipped_count += 1
                        continue

                    # Build record
                    common_data = {
                        "location": department,
                        "city": str(row.get("city", "")).strip(),
                        "person": person,
                        "mobile_no": mobile_no,
                        "imei_no": imei_no,
                        "serial_number": serial_number,
                        "date": date_val,
                        "parcel_sent_by": str(row.get("parcel_sent_by", "")).strip(),
                        "docket_number": str(row.get("docket_number", "")).strip(),
                        "collected_person_name": str(row.get("collected_person_name", "")).strip(),
                        "status": status,
                    }

                    if record_type == 'dispatch':
                        DeviceDispatch.objects.create(**common_data)
                    elif record_type == 'return':
                        DeviceReturn.objects.create(**common_data)
                    else:
                        skipped_count += 1
                        continue

                    created_count += 1

                except Exception:
                    skipped_count += 1
                    continue

            messages.success(request, f"✅ Imported {created_count} records. ❌ Skipped {skipped_count} invalid rows.")

        except Exception as e:
            messages.error(request, f"❌ Error during import: {str(e)}")

    return redirect('master')