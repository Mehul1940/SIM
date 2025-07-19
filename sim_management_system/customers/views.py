from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Customer


@login_required
def customer_list(request):
    customers = Customer.objects.select_related('user').all()
    return render(request, 'customers/customer_list.html', {'customers': customers})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customers/customer_detail.html', {'customer': customer})


@login_required
def customer_create(request):
    users = User.objects.filter(customer_profile__isnull=True)

    if request.method == 'POST':
        user_id = request.POST.get('user')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email') or None
        address = request.POST.get('address') or None
        id_proof_type = request.POST.get('id_proof_type') or None
        id_proof_number = request.POST.get('id_proof_number') or None
        id_proof_file = request.FILES.get('id_proof_file')
        is_active = bool(request.POST.get('is_active'))

        user = User.objects.get(pk=user_id) if user_id else None

        Customer.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            email=email,
            address=address,
            id_proof_type=id_proof_type,
            id_proof_number=id_proof_number,
            id_proof_file=id_proof_file,
            is_active=is_active
        )

        messages.success(request, "Customer created successfully.")
        return redirect('customer_list')

    return render(request, 'customers/customer_form.html', {
        'users': users,
        'form_action': 'Create'
    })


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    users = User.objects.filter(customer_profile__isnull=True) | User.objects.filter(pk=customer.user_id)

    if request.method == 'POST':
        user_id = request.POST.get('user')
        customer.user = User.objects.get(pk=user_id) if user_id else None
        customer.full_name = request.POST.get('full_name')
        customer.phone = request.POST.get('phone')
        customer.email = request.POST.get('email') or None
        customer.address = request.POST.get('address') or None
        customer.id_proof_type = request.POST.get('id_proof_type') or None
        customer.id_proof_number = request.POST.get('id_proof_number') or None
        customer.is_active = bool(request.POST.get('is_active'))

        if request.FILES.get('id_proof_file'):
            customer.id_proof_file = request.FILES.get('id_proof_file')

        customer.save()

        messages.success(request, "Customer updated successfully.")
        return redirect('customer_detail', pk=customer.pk)

    return render(request, 'customers/customer_form.html', {
        'customer': customer,
        'users': users,
        'form_action': 'Update'
    })


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        customer.delete()
        messages.success(request, "Customer deleted.")
        return redirect('customer_list')

    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})
