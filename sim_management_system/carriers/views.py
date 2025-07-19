from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Carrier

@login_required
def carrier_list(request):
    carriers = Carrier.objects.all()
    return render(request, 'carriers/carrier_list.html', {'carriers': carriers})


@login_required
def carrier_detail(request, pk):
    carrier = get_object_or_404(Carrier, pk=pk)
    return render(request, 'carriers/carrier_detail.html', {'carrier': carrier})


@login_required
def carrier_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        support_email = request.POST.get('support_email') or None
        support_phone = request.POST.get('support_phone') or None
        website = request.POST.get('website') or None
        is_active = bool(request.POST.get('is_active'))

        if not name or not code:
            messages.error(request, 'Name and Code are required.')
            return redirect('carrier_create')

        carrier = Carrier.objects.create(
            name=name,
            code=code,
            support_email=support_email,
            support_phone=support_phone,
            website=website,
            is_active=is_active
        )
        messages.success(request, 'Carrier created successfully.')
        return redirect('carrier_list')

    return render(request, 'carriers/carrier_form.html', {'form_action': 'Create'})


@login_required
def carrier_update(request, pk):
    carrier = get_object_or_404(Carrier, pk=pk)

    if request.method == 'POST':
        carrier.name = request.POST.get('name')
        carrier.code = request.POST.get('code')
        carrier.support_email = request.POST.get('support_email') or None
        carrier.support_phone = request.POST.get('support_phone') or None
        carrier.website = request.POST.get('website') or None
        carrier.is_active = bool(request.POST.get('is_active'))
        carrier.save()
        messages.success(request, 'Carrier updated successfully.')
        return redirect('carrier_detail', pk=carrier.pk)

    return render(request, 'carriers/carrier_form.html', {'carrier': carrier, 'form_action': 'Update'})


@login_required
def carrier_delete(request, pk):
    carrier = get_object_or_404(Carrier, pk=pk)
    if request.method == 'POST':
        carrier.delete()
        messages.success(request, 'Carrier deleted.')
        return redirect('carrier_list')
    return render(request, 'carriers/carrier_confirm_delete.html', {'carrier': carrier})
