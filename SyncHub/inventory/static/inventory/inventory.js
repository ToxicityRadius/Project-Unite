document.addEventListener('DOMContentLoaded', function() {
    const inventorySection = document.getElementById('inventory-section');
    const editModeBtn = document.getElementById('edit-mode-btn');
    const deleteModeBtn = document.getElementById('delete-mode-btn');
    const addSingleBtn = document.getElementById('add-single-btn');
    let currentMode = null;
    let originalValues = new Map();

    // Edit mode functionality - replace spans with input fields
    editModeBtn.addEventListener('click', function() {
        if (currentMode === 'edit') {
            // Exit edit mode
            inventorySection.classList.remove('edit-mode');
            currentMode = null;
            editModeBtn.style.opacity = '1';

            // Replace inputs back to spans
            document.querySelectorAll('.edit-input').forEach(input => {
                const span = document.createElement('span');
                span.className = 'display-text';
                span.textContent = input.value;
                input.parentNode.replaceChild(span, input);
            });
        } else {
            // Enter edit mode
            if (inventorySection.classList.contains('delete-mode')) {
                inventorySection.classList.remove('delete-mode');
                deleteModeBtn.style.opacity = '1';
            }
            inventorySection.classList.add('edit-mode');
            currentMode = 'edit';
            editModeBtn.style.opacity = '0.5';

            // Replace spans with input fields
            document.querySelectorAll('.display-text').forEach(span => {
                const input = document.createElement('input');
                input.type = 'text';
                input.className = 'edit-input';
                input.value = span.textContent;
                input.addEventListener('keydown', handleEnterKey);
                input.addEventListener('blur', handleBlur);
                span.parentNode.replaceChild(input, span);
            });
        }
    });

    // Handle Enter key to save changes
    function handleEnterKey(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            saveSingleChange(this);
        } else if (event.key === 'Escape') {
            // Cancel edit and restore original value
            this.value = originalValues.get(this);
            this.blur();
        }
    }

    // Handle blur (losing focus) to save changes
    function handleBlur() {
        saveSingleChange(this);
    }

    // Save a single change
    function saveSingleChange(element) {
        const row = element.closest('.table-row');
        const editInputs = row.querySelectorAll('.edit-input');
        const itemId = row.getAttribute('data-item-id');

        if (editInputs.length >= 3) {
            const name = editInputs[0].value.trim();
            const description = editInputs[1].value.trim();
            const quantity = editInputs[2].value.trim();

            // Validate data
            if (!name) {
                alert('Item name cannot be empty');
                element.focus();
                return;
            }

            if (isNaN(quantity) || quantity < 0) {
                alert('Quantity must be a valid number');
                element.focus();
                return;
            }

            // Send update to server
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    action: 'update_single',
                    item_id: itemId,
                    name: name,
                    description: description,
                    quantity: quantity
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Replace inputs back to spans
                    editInputs.forEach(input => {
                        const span = document.createElement('span');
                        span.className = 'display-text';
                        span.textContent = input.value;
                        input.parentNode.replaceChild(span, input);
                    });

                    // Exit edit mode
                    inventorySection.classList.remove('edit-mode');
                    currentMode = null;
                    editModeBtn.style.opacity = '1';
                } else {
                    alert('Error saving changes: ' + data.error);
                    // Restore original value
                    element.value = originalValues.get(element);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error saving changes');
                // Restore original value
                element.value = originalValues.get(element);
            });
        }
    }

    // Delete mode functionality
    if (deleteModeBtn) {
        deleteModeBtn.addEventListener('click', function() {
            if (currentMode === 'delete') {
                // Exit delete mode
                inventorySection.classList.remove('delete-mode');
                currentMode = null;
                deleteModeBtn.style.opacity = '1';
            } else {
                // Enter delete mode
                if (inventorySection.classList.contains('edit-mode')) {
                    inventorySection.classList.remove('edit-mode');
                    editModeBtn.style.opacity = '1';

                    // Remove edit styling and event listeners
                    document.querySelectorAll('.display-text').forEach(text => {
                        text.contentEditable = 'false';
                        text.style.border = 'none';
                        text.style.padding = '0';
                        text.style.backgroundColor = 'transparent';
                        text.removeEventListener('keydown', handleEnterKey);
                        text.removeEventListener('blur', handleBlur);
                    });
                }
                inventorySection.classList.add('delete-mode');
                currentMode = 'delete';
                deleteModeBtn.style.opacity = '0.5';
            }
        });
    }

    // Individual delete icon functionality
    document.addEventListener('click', function(event) {
        if (event.target.closest('.delete-icon')) {
            event.preventDefault();
            const deleteIcon = event.target.closest('.delete-icon');
            const itemId = deleteIcon.getAttribute('data-item-id');
            const row = deleteIcon.closest('.table-row');

            // Show confirmation dialog
            if (confirm('Are you sure you want to delete this item?')) {
                // Send delete request to server
                fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({
                        action: 'delete',
                        item_ids: [itemId]
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove the row from the table
                        row.remove();
                    } else {
                        alert('Error deleting item: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error deleting item');
                });
            }
        }
    });

    // Add single item functionality
    addSingleBtn.addEventListener('click', function() {
        // Create a new row with empty input fields
        const table = document.querySelector('.inventory-table');
        const newRow = document.createElement('div');
        newRow.className = 'table-row new-item-row';
        newRow.setAttribute('data-item-id', 'new');

        newRow.innerHTML = `
            <div class="table-col" data-label="ITEM">
                <input type="text" class="new-item-input new-item-name" placeholder="Item name">
            </div>
            <div class="table-col" data-label="DESCRIPTION">
                <input type="text" class="new-item-input new-item-description" placeholder="Description">
            </div>
            <div class="table-col" data-label="QUANTITY">
                <input type="number" class="new-item-input new-item-quantity" placeholder="Quantity">
            </div>
            <div class="table-col" data-label="DATE ADDED">
                <span class="new-item-date">New Item</span>
            </div>
        `;

        // Insert the new row before the add button container
        const addButtonContainer = document.querySelector('.add-button-container');
        table.insertBefore(newRow, addButtonContainer);

        // Style the inputs and add event listeners
        const inputs = newRow.querySelectorAll('.new-item-input');
        inputs.forEach(input => {
            input.addEventListener('keydown', handleNewItemEnter);
            input.addEventListener('blur', handleNewItemBlur);
        });

        // Focus on the name field
        inputs[0].focus();
    });

    // Handle Enter key for new items
    function handleNewItemEnter(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            saveNewItem(this);
        } else if (event.key === 'Escape') {
            // Cancel and remove the new row
            const row = this.closest('.table-row');
            row.remove();
        }
    }

    // Handle blur for new items - only save if all fields are filled
    function handleNewItemBlur() {
        const row = this.closest('.table-row');
        const inputs = row.querySelectorAll('.new-item-input');
        const name = inputs[0].value.trim();
        const description = inputs[1].value.trim();
        const quantity = inputs[2].value.trim();

        // Only save if all fields have content
        if (name && description && quantity) {
            saveNewItem(this);
        }
    }

    // Save new item
    function saveNewItem(element) {
        const row = element.closest('.table-row');
        const inputs = row.querySelectorAll('.new-item-input');

        if (inputs.length >= 3) {
            const name = inputs[0].value.trim();
            const description = inputs[1].value.trim();
            const quantity = inputs[2].value.trim();

            // Validate data
            if (!name) {
                alert('Item name cannot be empty');
                inputs[0].focus();
                return;
            }

            if (isNaN(quantity) || quantity < 0) {
                alert('Quantity must be a valid number');
                inputs[2].focus();
                return;
            }

            // Send create request to server
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    action: 'create',
                    name: name,
                    description: description,
                    quantity: quantity
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload the page to show the new item
                    window.location.reload();
                } else {
                    alert('Error creating item: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error creating item');
            });
        }
    }
});
