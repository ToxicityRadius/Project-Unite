import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.db.models import Count, Sum
from .models import Item
from .forms import ItemForm

def superadmin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=['Executive Officer', 'Staff']).exists())(view_func)

@login_required
def inventory_reports_view(request):
    is_admin = request.user.is_superuser or request.user.groups.filter(name__in=['Executive Officer', 'Staff']).exists()
    if not is_admin:
        return render(request, 'inventory/inventory_reports.html', {'error': 'Access denied. Admin privileges required.', 'is_admin': is_admin})

    # Get filter parameters from GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Base queryset for items_by_date
    items_by_date = Item.objects.values('date_added__date').annotate(
        total_items=Count('id'),
        total_quantity=Sum('quantity')
    )

    # Apply filters
    if start_date:
        items_by_date = items_by_date.filter(date_added__date__gte=start_date)
    if end_date:
        items_by_date = items_by_date.filter(date_added__date__lte=end_date)

    items_by_date = items_by_date.order_by('date_added__date')

    # Second aggregation: Total quantity per item for filtered dates
    filtered_items = Item.objects.filter()
    if start_date:
        filtered_items = filtered_items.filter(date_added__date__gte=start_date)
    if end_date:
        filtered_items = filtered_items.filter(date_added__date__lte=end_date)

    item_quantities = {}
    for item in filtered_items:
        name = item.name
        item_quantities[name] = item_quantities.get(name, 0) + item.quantity

    # Sort by total quantity descending
    sorted_items = sorted(item_quantities.items(), key=lambda x: x[1], reverse=True)
    item_names = [name for name, qty in sorted_items]
    item_total_quantities = [qty for name, qty in sorted_items]

    # Prepare data for first chart (items added by date)
    dates = [item['date_added__date'].strftime('%b %d') for item in items_by_date]
    items_count = [item['total_items'] for item in items_by_date]
    total_quantities_list = [item['total_quantity'] or 0 for item in items_by_date]

    return render(request, 'inventory/inventory_reports.html', {
        'items_by_date': items_by_date,
        'item_quantities': sorted_items,
        'dates': json.dumps(dates),
        'items_count': json.dumps(items_count),
        'total_quantities_list': json.dumps(total_quantities_list),
        'item_names': json.dumps(item_names),
        'item_total_quantities': json.dumps(item_total_quantities),
        'is_admin': is_admin,
        'filters': {'start_date': start_date, 'end_date': end_date}
    })

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
                location = data.get('location')

                try:
                    item = Item.objects.get(id=item_id)
                    item.name = name
                    item.description = description
                    item.quantity = int(quantity)
                    item.location = location
                    item.save()
                    return JsonResponse({'success': True})
                except Item.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Item not found'})
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Invalid quantity'})

            elif action == 'delete':
                item_ids = data.get('item_ids', [])
                deleted_count = Item.objects.filter(id__in=item_ids).delete()[0]
                return JsonResponse({'success': True, 'deleted_count': deleted_count, 'item_ids': item_ids})

            elif action == 'create':
                name = data.get('name')
                description = data.get('description')
                quantity = data.get('quantity')
                location = data.get('location')

                try:
                    Item.objects.create(
                        name=name,
                        description=description,
                        quantity=int(quantity),
                        location=location
                    )
                    return JsonResponse({'success': True})
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Invalid quantity'})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})

            elif action == 'save':
                items_data = data.get('items', [])
                new_items_data = data.get('new_items', [])

                # Update existing items
                for item_data in items_data:
                    if item_data['name'].strip():  # Only save if name is not empty
                        try:
                            item = Item.objects.get(id=item_data['id'])
                            item.name = item_data['name']
                            item.description = item_data['description'] or ''
                            item.quantity = int(item_data['quantity']) if str(item_data['quantity']).isdigit() else 0
                            item.location = item_data.get('location', '')
                            item.save()
                        except Item.DoesNotExist:
                            # If item doesn't exist, create it
                            Item.objects.create(
                                name=item_data['name'],
                                description=item_data['description'] or '',
                                quantity=int(item_data['quantity']) if str(item_data['quantity']).isdigit() else 0,
                                location=item_data.get('location', '')
                            )

                # Create new items
                for new_item_data in new_items_data:
                    if new_item_data['name'].strip():  # Only save if name is not empty
                        Item.objects.create(
                            name=new_item_data['name'],
                            description=new_item_data['description'] or '',
                            quantity=int(new_item_data['quantity']) if str(new_item_data['quantity']).isdigit() else 0,
                            location=new_item_data.get('location', '')
                        )

                return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    items = Item.objects.all()
    is_admin = request.user.is_superuser or request.user.groups.filter(name__in=['Executive Officer', 'Staff']).exists()
    return render(request, 'inventory/inventory.html', {'items': items, 'is_admin': is_admin})
