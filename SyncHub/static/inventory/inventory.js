// Inventory management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    let isEditMode = false;
    let isDeleteMode = false;
    let selectedItems = new Set();

    // Get CSRF token
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Edit mode button
    const editModeBtn = document.getElementById('edit-mode-btn');
    const saveChangesBtn = document.getElementById('save-changes-btn');
    const deleteModeBtn = document.getElementById('delete-mode-btn');
    const deleteSelectedBtn = document.getElementById('delete-selected-btn');
    const addSingleBtn = document.getElementById('add-single-btn');

    // Toggle edit mode
    editModeBtn.addEventListener('click', function() {
        isEditMode = !isEditMode;
        document.body.classList.toggle('edit-mode', isEditMode);

        if (isEditMode) {
            editModeBtn.style.backgroundColor = '#007bff';
            saveChangesBtn.style.display = 'inline-block';
        } else {
            editModeBtn.style.backgroundColor = '';
            saveChangesBtn.style.display = 'none';
            // Save changes when exiting edit mode
            saveAllChanges();
        }
    });

    // Toggle delete mode
    deleteModeBtn.addEventListener('click', function() {
        isDeleteMode = !isDeleteMode;
        document.body.classList.toggle('delete-mode', isDeleteMode);

        if (isDeleteMode) {
            deleteModeBtn.style.backgroundColor = '#dc3545';
            deleteSelectedBtn.style.display = 'inline-block';
        } else {
            deleteModeBtn.style.backgroundColor = '';
            deleteSelectedBtn.style.display = 'none';
            selectedItems.clear();
        }
    });

    // Handle delete icon clicks
    document.addEventListener('click', function(e) {
        console.log('Click detected on:', e.target);
        if (e.target.closest('.delete-icon')) {
            e.preventDefault();
            const deleteIcon = e.target.closest('.delete-icon');
            console.log('Delete icon found:', deleteIcon);
            const itemId = deleteIcon.getAttribute('data-item-id');
            console.log('Item ID:', itemId);

            if (itemId === 'new') {
                // Handle new row deletion
                const row = deleteIcon.closest('.table-row');
                if (row && row.classList.contains('new-row')) {
                    row.remove();
                }
                return;
            }

            if (isDeleteMode) {
                // Batch delete mode: select/deselect
                if (selectedItems.has(itemId)) {
                    selectedItems.delete(itemId);
                    deleteIcon.style.backgroundColor = '';
                } else {
                    selectedItems.add(itemId);
                    deleteIcon.style.backgroundColor = 'rgba(220, 53, 69, 0.3)';
                }
            } else {
                // Single delete mode: delete immediately
                if (confirm('Delete this item?')) {
                    console.log('Sending delete request for item:', itemId);
                    fetch(window.location.href, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken()
                        },
                        body: JSON.stringify({
                            action: 'delete',
                            item_ids: [parseInt(itemId)]
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Response received:', data);
                        if (data.success) {
                            console.log('Deleted items:', data.deleted_count, data.item_ids);
                            location.reload();
                        } else {
                            alert('Error deleting item: ' + (data.error || 'Unknown error'));
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Error deleting item');
                    });
                }
            }
        }
    });

    // Add single item button
    addSingleBtn.addEventListener('click', function() {
        addNewRow();
    });

    // Save changes button
    saveChangesBtn.addEventListener('click', function() {
        saveAllChanges();
        isEditMode = false;
        document.body.classList.remove('edit-mode');
        editModeBtn.style.backgroundColor = '';
        saveChangesBtn.style.display = 'none';
    });

    // Make table cells editable in edit mode
    document.addEventListener('click', function(e) {
        if (isEditMode && e.target.classList.contains('display-text')) {
            const span = e.target;
            const currentValue = span.textContent.trim();
            const input = document.createElement('input');
            input.type = 'text';
            input.value = currentValue;
            input.className = 'edit-input';
            input.style.width = '100%';
            input.style.border = '1px solid #007bff';
            input.style.borderRadius = '4px';
            input.style.padding = '4px';

            span.parentNode.replaceChild(input, span);
            input.focus();
            input.select();

            input.addEventListener('blur', function() {
                const newValue = input.value.trim();
                const newSpan = document.createElement('span');
                newSpan.className = 'display-text';
                newSpan.textContent = newValue || currentValue;
                input.parentNode.replaceChild(newSpan, input);
            });

            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    input.blur();
                } else if (e.key === 'Escape') {
                    const newSpan = document.createElement('span');
                    newSpan.className = 'display-text';
                    newSpan.textContent = currentValue;
                    input.parentNode.replaceChild(newSpan, input);
                }
            });
        }
    });

    // Add new row function
    function addNewRow() {
        const table = document.querySelector('.inventory-table');
        const addButtonContainer = document.querySelector('.add-button-container');

        // Create new row
        const newRow = document.createElement('div');
        newRow.className = 'table-row new-row';
        newRow.innerHTML = `
            <div class="table-col" data-label="ITEM">
                <input type="text" class="edit-input" placeholder="Item name" style="width: 100%; border: 1px solid #007bff; border-radius: 4px; padding: 4px;">
            </div>
            <div class="table-col" data-label="DESCRIPTION">
                <input type="text" class="edit-input" placeholder="Description" style="width: 100%; border: 1px solid #007bff; border-radius: 4px; padding: 4px;">
            </div>
            <div class="table-col" data-label="QUANTITY">
                <input type="number" class="edit-input" placeholder="0" min="0" style="width: 100%; border: 1px solid #007bff; border-radius: 4px; padding: 4px;">
            </div>
            <div class="table-col" data-label="LOCATION">
                <input type="text" class="edit-input" placeholder="Location" style="width: 100%; border: 1px solid #007bff; border-radius: 4px; padding: 4px;">
            </div>
            <div class="table-col" data-label="DATE ADDED">
                <button class="delete-icon" data-item-id="new" title="Remove item">
                    <img src="{% static 'inventory/images/f2a618d9d063a5a882d9001a79266c8923e43b84.png' %}" alt="Delete" />
                </button>
            </div>
        `;

        // Insert before the add button container
        table.insertBefore(newRow, addButtonContainer);
    }

    // Save all changes function
    function saveAllChanges() {
        const items = [];
        const newItems = [];

        // Collect existing items
        document.querySelectorAll('.table-row:not(.new-row)').forEach(row => {
            const itemId = row.getAttribute('data-item-id');
            if (itemId) {
                const cols = row.querySelectorAll('.table-col');
                const name = cols[0].querySelector('.display-text')?.textContent.trim() ||
                           cols[0].querySelector('.edit-input')?.value.trim() || '';
                const description = cols[1].querySelector('.display-text')?.textContent.trim() ||
                                 cols[1].querySelector('.edit-input')?.value.trim() || '';
                const quantity = cols[2].querySelector('.display-text')?.textContent.trim() ||
                               cols[2].querySelector('.edit-input')?.value.trim() || '0';
                const location = cols[3].querySelector('.display-text')?.textContent.trim() ||
                               cols[3].querySelector('.edit-input')?.value.trim() || '';

                if (name) {
                    items.push({
                        id: itemId,
                        name: name,
                        description: description,
                        quantity: parseInt(quantity) || 0,
                        location: location
                    });
                }
            }
        });

        // Collect new items
        document.querySelectorAll('.table-row.new-row').forEach(row => {
            const cols = row.querySelectorAll('.table-col');
            const name = cols[0].querySelector('.edit-input')?.value.trim() || '';
            const description = cols[1].querySelector('.edit-input')?.value.trim() || '';
            const quantity = cols[2].querySelector('.edit-input')?.value.trim() || '0';
            const location = cols[3].querySelector('.edit-input')?.value.trim() || '';

            if (name) {
                newItems.push({
                    name: name,
                    description: description,
                    quantity: parseInt(quantity) || 0,
                    location: location
                });
            }
        });

        // Send data to server
        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                action: 'save',
                items: items,
                new_items: newItems
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Reload to show updated data
            } else {
                alert('Error saving changes: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error saving changes');
        });
    }

    // Handle delete selected items button
    deleteSelectedBtn.addEventListener('click', function() {
        if (selectedItems.size > 0) {
            if (confirm(`Delete ${selectedItems.size} selected item(s)?`)) {
                fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        action: 'delete',
                        item_ids: Array.from(selectedItems).map(id => parseInt(id))
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('Batch deleted items:', data.deleted_count, data.item_ids);
                        location.reload();
                    } else {
                        alert('Error deleting items: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error deleting items');
                });
            }
        }
    });

    // Handle delete selected items
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Delete' && isDeleteMode && selectedItems.size > 0) {
            if (confirm(`Delete ${selectedItems.size} selected item(s)?`)) {
                fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                        body: JSON.stringify({
                            action: 'delete',
                            item_ids: Array.from(selectedItems).map(id => parseInt(id))
                        })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('Batch deleted items:', data.deleted_count, data.item_ids);
                        location.reload();
                    } else {
                        alert('Error deleting items: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error deleting items');
                });
            }
        }
    });

    // Remove the redundant handler since it's now handled in the main delete icon handler
});
