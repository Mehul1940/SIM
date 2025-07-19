from django.db.models import Q
from datetime import datetime
from simcards.models import SimCard

def filter_simcards(request, simcards_qs):
    search_query = request.GET.get('q', '').strip()
    filter_status = request.GET.get('status', 'all').strip()
    filter_type = request.GET.get('sim_type', 'all').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    if search_query:
        simcards_qs = simcards_qs.filter(
            Q(vehicle_reg_no__icontains=search_query) |
            Q(mobile_number__icontains=search_query) |
            Q(imei_number__icontains=search_query) |
            Q(device_company__icontains=search_query) |
            Q(transporter_name__icontains=search_query)
        )

    if filter_status != 'all':
        simcards_qs = simcards_qs.filter(sim_status=filter_status)

    if filter_type != 'all':
        simcards_qs = simcards_qs.filter(sim_type=filter_type)

    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            simcards_qs = simcards_qs.filter(last_connected__date__gte=start_date_obj)
        except ValueError:
            pass

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            simcards_qs = simcards_qs.filter(last_connected__date__lte=end_date_obj)
        except ValueError:
            pass

    all_sim_types = SimCard.objects.values_list('sim_type', flat=True).distinct().exclude(sim_type='').order_by('sim_type')
    all_sim_statuses = SimCard.objects.values_list('sim_status', flat=True).distinct().exclude(sim_status='').order_by('sim_status')

    return simcards_qs, {
        'search_query': search_query,
        'filter_status': filter_status,
        'filter_type': filter_type,
        'start_date': start_date,
        'end_date': end_date,
        'all_sim_types': all_sim_types,
        'all_sim_statuses': all_sim_statuses,
    }
