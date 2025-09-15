from django.shortcuts import render, redirect
from .models import Item
from .forms import ItemForm

def item_list(request):
    items = Item.objects.all()
    return render(request, 'inventory/item_list.html', {'items': items})

def item_add(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:item_list')
    else:
        form = ItemForm()
    return render(request, 'inventory/item_add.html', {'form': form})
