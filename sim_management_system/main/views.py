import json
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.shortcuts import render, redirect
from django.db.models import Count, Max, Sum
from django.db.models.functions import TruncMonth, Coalesce

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction

from simcards.models import SimCard, SimStatus, SimType 
from customers.models import Customer
from stock.models import DeviceDispatch, DeviceReturn, InventoryItem
from departments.models import Department
from carriers.models import Carrier


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'main/login.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'main/change_password.html', {
        'form': form,
        'title': 'Change Password'
    })

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = date.fromisoformat(start_date_str)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_date = date.fromisoformat(end_date_str)
        except ValueError:
            pass 

    selected_department_id = request.GET.get('department')
    selected_sim_type = request.GET.get('sim_type')

    sim_cards_queryset = SimCard.objects.all()
    dispatches_queryset = DeviceDispatch.objects.all()
    returns_queryset = DeviceReturn.objects.all()
    customers_queryset = Customer.objects.all()

    if selected_department_id:
        try:
            department_id = int(selected_department_id)
            if hasattr(SimCard, 'department_id'):
                sim_cards_queryset = sim_cards_queryset.filter(department_id=department_id)
            elif hasattr(SimCard, 'location_id'): 
                sim_cards_queryset = sim_cards_queryset.filter(location_id=department_id)

            dispatch_return_department_field = None
            if hasattr(DeviceDispatch, 'department_id'):
                dispatch_return_department_field = 'department_id'
            elif hasattr(DeviceDispatch, 'location_id'):
                dispatch_return_department_field = 'location_id'

            if dispatch_return_department_field:
                dispatches_queryset = dispatches_queryset.filter(**{dispatch_return_department_field: department_id})
                returns_queryset = returns_queryset.filter(**{dispatch_return_department_field: department_id})

        except ValueError:
            pass

 
    if selected_sim_type and selected_sim_type != 'all':
        sim_cards_queryset = sim_cards_queryset.filter(sim_type=selected_sim_type)
    
    filtered_dispatches_by_date = dispatches_queryset
    filtered_returns_by_date = returns_queryset

    if start_date and end_date:
        filtered_dispatches_by_date = filtered_dispatches_by_date.filter(date__range=[start_date, end_date])
        filtered_returns_by_date = filtered_returns_by_date.filter(date__range=[start_date, end_date])
    elif start_date: 
        filtered_dispatches_by_date = filtered_dispatches_by_date.filter(date__gte=start_date)
        filtered_returns_by_date = filtered_returns_by_date.filter(date__gte=start_date)
    elif end_date:
        filtered_dispatches_by_date = filtered_dispatches_by_date.filter(date__lte=end_date)
        filtered_returns_by_date = filtered_returns_by_date.filter(date__lte=end_date)


    sim_card_count = sim_cards_queryset.count()
    dispatched_devices_count = filtered_dispatches_by_date.count()
    returned_devices_count = filtered_returns_by_date.count()

    total_dispatched_quantity_sum = filtered_dispatches_by_date.aggregate(
        total_quantity=Coalesce(Sum('quantity'), 0)
    )['total_quantity'] if hasattr(DeviceDispatch, 'quantity') else filtered_dispatches_by_date.count()

    total_returned_quantity_sum = filtered_returns_by_date.aggregate(
        total_quantity=Coalesce(Sum('quantity'), 0)
    )['total_quantity'] if hasattr(DeviceReturn, 'quantity') else filtered_returns_by_date.count()

    inventory_items_count = total_dispatched_quantity_sum + total_returned_quantity_sum
    diable_sim_count = sim_cards_queryset.filter(sim_status=SimStatus.DISABLE).count()

    try:
        active_sim_count = sim_cards_queryset.filter(sim_status=SimStatus.ACTIVE).count()
        deactive_sim_count = sim_cards_queryset.filter(sim_status=SimStatus.DEACTIVE).count()
    except AttributeError:
        active_sim_count = sim_cards_queryset.filter(sim_status='ACTIVE').count()
        deactive_sim_count = sim_cards_queryset.filter(sim_status='DEACTIVE').count()

    customer_count = customers_queryset.count()

    inventory_items_count = inventory_items_count
    diable_sim=diable_sim_count

    sim_status_labels = []
    sim_status_data = []
    try:
        sim_status_counts = (sim_cards_queryset
                             .values('sim_status')
                             .annotate(count=Count('sim_status'))
                             .order_by('sim_status'))

        status_display_map = dict(SimStatus.choices) if hasattr(SimStatus, 'choices') else {}
        for status_entry in sim_status_counts:
            if status_entry['count'] > 0:
                label = status_display_map.get(status_entry['sim_status'], status_entry['sim_status'])
                sim_status_labels.append(label)
                sim_status_data.append(status_entry['count'])
    except Exception as e:
        print(f"Error generating SIM status chart data: {e}")

    sim_type_labels = []
    sim_type_data = []
  
    try:
        sim_type_counts = (sim_cards_queryset
                           .values('sim_type')
                           .annotate(count=Count('sim_type'))
                           .order_by('sim_type'))

        type_display_map = dict(SimType.choices) if hasattr(SimType, 'choices') else {}
        for type_entry in sim_type_counts:
            if type_entry['count'] > 0:
                label = type_display_map.get(type_entry['sim_type'], type_entry['sim_type'])
                sim_type_labels.append(label)
                sim_type_data.append(type_entry['count'])
    except Exception as e:
        print(f"Error generating SIM type chart data: {e}")
  

    device_activity_labels = []
    dispatch_counts = []
    return_counts = []
  
    if start_date and end_date:
        try:
            monthly_dispatches_data = (filtered_dispatches_by_date
                                       .filter(date__isnull=False)
                                       .annotate(month=TruncMonth('date'))
                                       .values('month')
                                       .annotate(count=Count('id'))
                                       .order_by('month'))

            monthly_returns_data = (filtered_returns_by_date
                                    .filter(date__isnull=False)
                                    .annotate(month=TruncMonth('date'))
                                    .values('month')
                                    .annotate(count=Count('id'))
                                    .order_by('month'))

            current_month = start_date.replace(day=1)
            end_month = end_date.replace(day=1) if end_date.day == 1 else (end_date + relativedelta(months=1)).replace(day=1)

            while current_month <= end_month:
                month_label = current_month.strftime('%b %Y')
                device_activity_labels.append(month_label)

                dispatch_count = next(
                    (item['count'] for item in monthly_dispatches_data
                     if item['month'] and item['month'].year == current_month.year
                     and item['month'].month == current_month.month), 0
                )
                return_count = next(
                    (item['count'] for item in monthly_returns_data
                     if item['month'] and item['month'].year == current_month.year
                     and item['month'].month == current_month.month), 0
                )

                dispatch_counts.append(dispatch_count)
                return_counts.append(return_count)

                current_month += relativedelta(months=1)

        except Exception as e:
            print(f"Error generating device activity chart data: {e}")
            device_activity_labels = []
            dispatch_counts = []
            return_counts = []

    device_activity_chart_data = {
        'labels': device_activity_labels,
        'dispatch_data': dispatch_counts,
        'return_data': return_counts,
    }

    sims_by_department_labels = []
    sims_by_department_data = []
    try:
        sims_by_department_counts = (sim_cards_queryset
                                     .filter(department__isnull=False)
                                     .values('department__name')
                                     .annotate(count=Count('id'))
                                     .order_by('-count')[:10])

        sims_by_department_labels = [item['department__name'] for item in sims_by_department_counts]
        sims_by_department_data = [item['count'] for item in sims_by_department_counts]
    except Exception as e:
        print(f"Error generating SIMs by department chart data: {e}")

    sims_by_carrier_labels = []
    sims_by_carrier_data = []
    try:
        sims_by_carrier_counts = (sim_cards_queryset
                                  .filter(carrier__isnull=False)
                                  .values('carrier__name')
                                  .annotate(count=Count('id'))
                                  .order_by('-count')[:10])

        sims_by_carrier_labels = [item['carrier__name'] for item in sims_by_carrier_counts]
        sims_by_carrier_data = [item['count'] for item in sims_by_carrier_counts]
    except Exception as e:
        print(f"Error generating SIMs by carrier chart data: {e}")

   
    all_sim_types = [choice[0] for choice in SimType.choices] if hasattr(SimType, 'choices') else list(SimCard.objects.values_list('sim_type', flat=True).distinct().order_by('sim_type'))
  


    context = {
        'sim_card_count': sim_card_count,
        'dispatched_devices_count': dispatched_devices_count,
        'returned_devices_count': returned_devices_count,
        'inventory_items_count': inventory_items_count,
        'active_sim_count': active_sim_count,
        'deactive_sim_count': deactive_sim_count,
        'customer_count': customer_count,
        'diable_sim': diable_sim,

        'departments': Department.objects.all(),
        'carriers': Carrier.objects.all(), # Keep carriers in context if other parts of dashboard use it
        'all_sim_types': all_sim_types, # Pass all available SIM types to the template
        # Pass raw string for value attribute if dates are not selected
        'start_date': start_date.isoformat() if start_date else '',
        'end_date': end_date.isoformat() if end_date else '',
        'selected_department': selected_department_id,
        'selected_sim_type': selected_sim_type, # Pass the selected SIM type to the template
        # 'selected_carrier': selected_carrier_id, # Removed as per requirement

        'sim_status_data': json.dumps({
            'labels': sim_status_labels,
            'data': sim_status_data,
        }),
        'sim_type_data': json.dumps({
            'labels': sim_type_labels,
            'data': sim_type_data,
        }),
        'device_activity_data': json.dumps(device_activity_chart_data),
        'sims_by_department_data': json.dumps({
            'labels': sims_by_department_labels,
            'data': sims_by_department_data,
        }),
        'sims_by_carrier_data': json.dumps({
            'labels': sims_by_carrier_labels,
            'data': sims_by_carrier_data,
        }),
    }

    return render(request, 'main/dashboard.html', context)

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        errors = []
        required_fields = [
            ('username', 'Username'),
            ('password1', 'Password'),
            ('password2', 'Password confirmation'),
            ('email', 'Email'),
            ('phone', 'Phone number'),
            ('address', 'Address')
        ]

        for field, name in required_fields:
            if not request.POST.get(field):
                errors.append(f"{name} is required")

        if User.objects.filter(username=username).exists():
            errors.append('Username already exists')

        if password1 != password2:
            errors.append('Passwords do not match')

        if len(phone) < 10:
            errors.append('Phone number must be at least 10 digits')

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('register')

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    password=password1,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                Customer.objects.create(
                    user=user,
                    phone=phone,
                    address=address
                )
                messages.success(request, 'Registration successful! Please login')
                return redirect('login')

        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('register')

    return render(request, 'main/register.html')


@login_required
def user_dashboard(request):
    context = {
        'user': request.user,
    }
    return render(request, 'main/user_dashboard.html', context)