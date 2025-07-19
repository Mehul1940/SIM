from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SimAssignment, AssignmentHistory
from simcards.models import SimCard
from customers.models import Customer
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()

@login_required
def assignment_list(request):
    assignments = SimAssignment.objects.select_related('sim_card', 'customer', 'assigned_by')
    return render(request, 'assignments/assignment_list.html', {'assignments': assignments})


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(SimAssignment, pk=pk)
    history = assignment.history.select_related('changed_by')
    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment,
        'history': history
    })


@login_required
def assignment_create(request):
    sims = SimCard.objects.filter(assignment__isnull=True)  
    customers = Customer.objects.all()

    if request.method == 'POST':
        sim_id = request.POST.get('sim_card')
        customer_id = request.POST.get('customer')
        sim = get_object_or_404(SimCard, id=sim_id)
        customer = get_object_or_404(Customer, id=customer_id)

        assignment = SimAssignment.objects.create(
            sim_card=sim,
            customer=customer,
            assigned_by=request.user,
            activation_date=request.POST.get('activation_date'),
            expiry_date=request.POST.get('expiry_date') or None,
            is_active=bool(request.POST.get('is_active')),
            reason=request.POST.get('reason') or '',
            notes=request.POST.get('notes') or '',
        )

        AssignmentHistory.objects.create(
            assignment=assignment,
            changed_by=request.user,
            change_type='CREATED',
            change_details={"reason": assignment.reason},
        )

        messages.success(request, 'SIM Assignment created successfully.')
        return redirect('assignment_list')

    return render(request, 'assignments/assignment_form.html', {
        'sims': sims,
        'customers': customers,
        'form_action': 'Create'
    })


@login_required
def assignment_update(request, pk):
    assignment = get_object_or_404(SimAssignment, pk=pk)
    customers = Customer.objects.all()

    if request.method == 'POST':
        old_data = {
            'customer': assignment.customer.id,
            'expiry_date': assignment.expiry_date,
            'is_active': assignment.is_active,
            'reason': assignment.reason,
            'notes': assignment.notes,
        }

        assignment.customer = get_object_or_404(Customer, id=request.POST.get('customer'))
        assignment.expiry_date = request.POST.get('expiry_date') or None
        assignment.is_active = bool(request.POST.get('is_active'))
        assignment.reason = request.POST.get('reason') or ''
        assignment.notes = request.POST.get('notes') or ''
        assignment.save()

        # Save to history
        AssignmentHistory.objects.create(
            assignment=assignment,
            changed_by=request.user,
            change_type='UPDATED',
            change_details={
                'old': old_data,
                'new': {
                    'customer': assignment.customer.id,
                    'expiry_date': assignment.expiry_date,
                    'is_active': assignment.is_active,
                    'reason': assignment.reason,
                    'notes': assignment.notes,
                }
            }
        )

        messages.success(request, 'SIM Assignment updated successfully.')
        return redirect('assignment_detail', pk=assignment.pk)

    return render(request, 'assignments/assignment_form.html', {
        'assignment': assignment,
        'customers': customers,
        'form_action': 'Update'
    })


@login_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(SimAssignment, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted.')
        return redirect('assignment_list')
    return render(request, 'assignments/assignment_confirm_delete.html', {'assignment': assignment})
