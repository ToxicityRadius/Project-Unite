import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.http import JsonResponse
from .models import Item
from .forms import ItemForm

def superadmin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['Executive Officer', 'Staff']).exists())(view_func)

@login_required
def item_list(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'update_single':
                item_id = data.get('item_id')
                name = data.get('name')
                description = data.get('description')
                quantity = data.get('quantity')
                
                try:
                    item = Item.objects.get(id=item_id)
                    item.name = name
                    item.description = description
                    item.quantity = int(quantity)
                    item.save()
                    return JsonResponse({'success': True})
                except Item.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Item not found'})
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Invalid quantity'})

            elif action == 'delete':
                item_ids = data.get('item_ids', [])
                Item.objects.filter(id__in=item_ids).delete()
                return JsonResponse({'success': True})

            elif action == 'create':
                name = data.get('name')
                description = data.get('description')
                quantity = data.get('quantity')
                
                try:
                    Item.objects.create(
                        name=name,
                        description=description,
                        quantity=int(quantity)
                    )
                    return JsonResponse({'success': True})
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Invalid quantity'})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})

            elif action == 'save':
                items_data = data.get('items', [])
                # Clear existing items and save new ones
                Item.objects.all().delete()
                for item_data in items_data:
                    if item_data['name'].strip():  # Only save if name is not empty
                        Item.objects.create(
                            name=item_data['name'],
                            description=item_data['description'] or '',
                            quantity=int(item_data['quantity']) if item_data['quantity'].isdigit() else 0
                        )
                return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    items = Item.objects.all()
    is_admin = request.user.is_superuser or request.user.groups.filter(name__in=['Executive Officer', 'Staff']).exists()
    return render(request, 'inventory/inventory.html', {'items': items, 'is_admin': is_admin})
