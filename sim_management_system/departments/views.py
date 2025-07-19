from django.shortcuts import render, get_object_or_404
from simcards.models import SimCard
from .models import Department
from .utils import filter_simcards
import openpyxl
from django.http import HttpResponse


def departments_list(request):
    department_name = request.GET.get('department', '').strip().lower() or 'all'
    all_departments = Department.objects.all()

    # Safely filter by department name
    if department_name != 'all':
        departments = all_departments.filter(name__iexact=department_name)
    else:
        departments = all_departments

    filtered_departments = []
    for department in departments.prefetch_related('simcards'):
        simcards_qs = department.simcards.all()
        filtered_simcards, _ = filter_simcards(request, simcards_qs)
        if filtered_simcards.exists():
            department.filtered_simcards = filtered_simcards
            filtered_departments.append(department)

    # Dropdown filter values
    all_sim_types = SimCard.objects.values_list('sim_type', flat=True).distinct().exclude(sim_type__exact='').order_by('sim_type')
    all_sim_statuses = SimCard.objects.values_list('sim_status', flat=True).distinct().exclude(sim_status__exact='').order_by('sim_status')

    context = {
        'departments': filtered_departments,
        'all_departments': all_departments,  # For dropdown
        'selected_department': department_name,
        'all_sim_types': all_sim_types,
        'all_sim_statuses': all_sim_statuses,
        'search_query': request.GET.get('q', '').strip(),
        'filter_status': request.GET.get('status', 'all').strip(),
        'filter_type': request.GET.get('sim_type', 'all').strip(),
        'start_date': request.GET.get('start_date', '').strip(),
        'end_date': request.GET.get('end_date', '').strip(),
    }
    return render(request, 'departments/departments_list.html', context)


def department_view(request, department_name, template_name):
    department = get_object_or_404(Department, name__iexact=department_name)
    simcards_qs = SimCard.objects.filter(department=department)
    filtered_simcards, filter_context = filter_simcards(request, simcards_qs)

    context = {
        'department': department,
        'simcards': filtered_simcards,
        **filter_context
    }
    return render(request, f'departments/{template_name}', context)


# Department-specific views
def siliguri(request):
    return department_view(request, "Siliguri", "siliguri.html")

def margdarshak(request):
    return department_view(request, "Margdarshak", "margdarshak.html")

def vmc(request):
    return department_view(request, "vmc", "vmc.html")

def local_client(request):
    return department_view(request, "local_client", "local_client.html")

def wb(request):
    return department_view(request, "Wb", "wb.html")

def pso(request):
    return department_view(request, "Pso", "pso.html")


def export_simcards_excel(request):
    department_name = request.GET.get('department', '').strip().lower() or 'all'

    if department_name != 'all':
        try:
            department = get_object_or_404(Department, name__iexact=department_name)
            simcards_qs = SimCard.objects.filter(department=department)
            sheet_title = department.name
            filename = f"{department.name.lower().replace(' ', '_')}_simcards.xlsx"
        except Department.DoesNotExist:
            simcards_qs = SimCard.objects.none()
            sheet_title = "Invalid Department"
            filename = "invalid_department.xlsx"
    else:
        simcards_qs = SimCard.objects.all()
        sheet_title = "All Departments"
        filename = "all_simcards.xlsx"

    # ✅ Apply the same filters as UI
    filtered_simcards, _ = filter_simcards(request, simcards_qs)

    # Create Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_title

    headers = ['Vehicle No', 'Mobile No', 'IMEI', 'Transporter', 'Department', 'SIM Type', 'SIM Status']
    ws.append(headers)

    for sim in filtered_simcards:
        ws.append([
            sim.vehicle_reg_no or 'N/A',
            sim.mobile_number or 'N/A',
            sim.imei_number or 'N/A',
            sim.transporter_name or 'N/A',
            sim.department.name if sim.department else 'N/A',
            sim.get_sim_type_display() or 'N/A',
            sim.get_sim_status_display() or 'N/A',
        ])

    # Return Excel file as response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response
