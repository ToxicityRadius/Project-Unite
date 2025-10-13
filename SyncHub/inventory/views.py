from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item
from .forms import ItemForm

def admin_or_superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='admin').exists())(view_func)

@login_required
def item_list(request):
    items = Item.objects.all()
    is_admin = request.user.is_superuser or request.user.groups.filter(name='admin').exists()
    return render(request, 'inventory/item_list.html', {'items': items, 'is_admin': is_admin})

@login_required
@admin_or_superuser_required
def item_add(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:item_list')
    else:
        form = ItemForm()
    return render(request, 'inventory/item_form.html', {'form': form, 'action': 'Add Item'})

@login_required
@admin_or_superuser_required
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('inventory:item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'inventory/item_form.html', {'form': form, 'action': 'Edit Item', 'item': item})

@login_required
@admin_or_superuser_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('inventory:item_list')
    return render(request, 'inventory/item_delete.html', {'item': item})
