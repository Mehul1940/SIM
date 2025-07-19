from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import SimCard, SimType, SimStatus, PlanType
from carriers.models import Carrier
from departments.models import Department
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.timezone import now
from datetime import date
from django.db.models import Count, Sum


@login_required
def simcard_list(request):
    sim_type_filter = request.GET.get('sim_type')
    
    if sim_type_filter in SimType.values:
        simcards = SimCard.objects.filter(sim_type=sim_type_filter).select_related('department', 'carrier')
    else:
        simcards = SimCard.objects.all().select_related('department', 'carrier')

    return render(request, 'simcards/simcard_list.html', {
        'simcards': simcards,
        'sim_type_filter': sim_type_filter,
        'sim_types': SimType.choices,
    })


@login_required
def simcard_detail(request, pk):
    simcard = get_object_or_404(SimCard.objects.select_related('department', 'carrier'), pk=pk)
    return render(request, 'simcards/simcard_detail.html', {'simcard': simcard})


@login_required
def simcard_create(request):
    if request.method == 'POST':
        carrier_id = request.POST.get('carrier')
        carrier = Carrier.objects.get(id=carrier_id) if carrier_id else None

        department_id = request.POST.get('department')
        department = Department.objects.get(id=department_id) if department_id else None

        SimCard.objects.create(
            mobile_number=request.POST.get('mobile_number'),
            iccid_number=request.POST.get('iccid_number'),
            imsi_number=request.POST.get('imsi_number'),
            basket_name=request.POST.get('basket_name'),
            sim_status=request.POST.get('sim_status'),
            plan_name=request.POST.get('plan_name'),
            plan_type=request.POST.get('plan_type'),
            sim_type=request.POST.get('sim_type'),
            imei_number=request.POST.get('imei_number'),
            current_ip=request.POST.get('current_ip'),
            last_connected=request.POST.get('last_connected') or None,
            action=request.POST.get('action'),
            new_sim_number=request.POST.get('new_sim_number'),
            reason=request.POST.get('reason'),
            remark1=request.POST.get('remark1'),
            remark2=request.POST.get('remark2'),
            remark3=request.POST.get('remark3'),
            carrier=carrier,
            vehicle_reg_no=request.POST.get('vehicle_reg_no'),
            transporter_name=request.POST.get('transporter_name'),
            device_company=request.POST.get('device_company'),
            starting_odo_meter=request.POST.get('starting_odo_meter') or None,
            department=department,
        )
        messages.success(request, "SIM card created successfully.")
        return redirect('departments_list')

    return render(request, 'simcards/simcard_form.html', {
        'sim_status_choices': SimStatus.choices,
        'sim_type_choices': SimType.choices,
        'plan_type_choices': PlanType.choices,
        'carriers': Carrier.objects.all(),
        'departments': Department.objects.all(),
    })


@login_required
def simcard_update(request, pk):
    simcard = get_object_or_404(SimCard, pk=pk)

    if request.method == 'POST':
        carrier_id = request.POST.get('carrier')
        carrier = Carrier.objects.get(id=carrier_id) if carrier_id else None

        department_id = request.POST.get('department')
        department = Department.objects.get(id=department_id) if department_id else None

        simcard.mobile_number = request.POST.get('mobile_number')
        simcard.iccid_number = request.POST.get('iccid_number')
        simcard.imsi_number = request.POST.get('imsi_number')
        simcard.basket_name = request.POST.get('basket_name')
        simcard.sim_status = request.POST.get('sim_status')
        simcard.plan_name = request.POST.get('plan_name')
        simcard.plan_type = request.POST.get('plan_type')
        simcard.sim_type = request.POST.get('sim_type')
        simcard.imei_number = request.POST.get('imei_number')
        simcard.current_ip = request.POST.get('current_ip')
        simcard.last_connected = request.POST.get('last_connected') or None
        simcard.action = request.POST.get('action')
        simcard.new_sim_number = request.POST.get('new_sim_number')
        simcard.reason = request.POST.get('reason')
        simcard.remark1 = request.POST.get('remark1')
        simcard.remark2 = request.POST.get('remark2')
        simcard.remark3 = request.POST.get('remark3')
        simcard.carrier = carrier
        simcard.vehicle_reg_no = request.POST.get('vehicle_reg_no')
        simcard.transporter_name = request.POST.get('transporter_name')
        simcard.device_company = request.POST.get('device_company')
        simcard.starting_odo_meter = request.POST.get('starting_odo_meter') or None
        simcard.department = department
        simcard.save()

        messages.success(request, "SIM card updated successfully.")
        return redirect('departments_list')

    return render(request, 'simcards/simcard_form.html', {
        'simcard': simcard,
        'sim_status_choices': SimStatus.choices,
        'sim_type_choices': SimType.choices,
        'plan_type_choices': PlanType.choices,
        'carriers': Carrier.objects.all(),
        'departments': Department.objects.all(),
    })


@login_required
def simcard_delete(request, pk):
    simcard = get_object_or_404(SimCard, pk=pk)
    
    if request.method == 'POST':
        simcard.delete()
        messages.success(request, "SIM card deleted.")
        return redirect('departments_list')
    
    return render(request, 'simcards/simcard_confirm_delete.html', {'simcard': simcard})

@login_required
def vehicle(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    sim_type = request.GET.get('sim_type', '').strip()  # <-- Add this line

    sim_cards = SimCard.objects.all()

    if query:
        sim_cards = sim_cards.filter(
            Q(vehicle_reg_no__icontains=query) |
            Q(mobile_number__icontains=query)
        )

    if status:
        sim_cards = sim_cards.filter(sim_status=status)

    if sim_type:
        sim_cards = sim_cards.filter(sim_type=sim_type)  # <-- Filter by sim_type

    sim_cards = sim_cards.order_by('vehicle_reg_no')

    # Badge class mapping
    badge_map = {
        'Active': 'success',
        'Inactive': 'secondary',
        'Suspended': 'warning',
        'Retired': 'danger',
    }

    for sim in sim_cards:
        sim.status_badge = badge_map.get(sim.sim_status, 'info')

    # ✅ Pagination
    paginator = Paginator(sim_cards, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ✅ Filtered statistics
    filtered_total = sim_cards.count()
    filtered_active = sim_cards.filter(sim_status='Active').count()
    filtered_inactive = sim_cards.filter(sim_status='Inactive').count()
    filtered_connected_today = sim_cards.filter(last_connected__date=date.today()).count()
    filtered_device_companies = sim_cards.exclude(device_company__isnull=True).values('device_company').distinct().count()
    filtered_odo = sim_cards.aggregate(Sum('starting_odo_meter'))['starting_odo_meter__sum'] or 0

    context = {
        'page_obj': page_obj,
        'sim_status_choices': SimStatus.choices,
        'sim_type_choices': SimType.choices,  # <-- Pass choices to the template
        'request': request,
        'total_vehicles': filtered_total,
        'total_active': filtered_active,
        'total_inactive': filtered_inactive,
        'connected_today': filtered_connected_today,
        'unique_device_companies': filtered_device_companies,
        'total_odo': filtered_odo,
    }
    return render(request, 'simcards/vehicle.html', context)


