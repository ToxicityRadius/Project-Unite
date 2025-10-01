from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from .models import Item
from .forms import ItemForm

def admin_required(view_func):
    return user_passes_test(lambda u: u.groups.filter(name='admin').exists())(view_func)

@login_required
@admin_required
def item_list(request):
    items = Item.objects.all()
    return render(request, 'inventory/item_list.html', {'items': items})

@login_required
@admin_required
def item_add(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:item_list')
    else:
        form = ItemForm()
    return render(request, 'inventory/item_add.html', {'form': form})

@login_required
@admin_required
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('inventory:item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'inventory/item_edit.html', {'form': form, 'item': item})

@login_required
@admin_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('inventory:item_list')
    return render(request, 'inventory/item_delete.html', {'item': item})
