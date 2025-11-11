document.addEventListener('DOMContentLoaded', function() {
    const inventorySection = document.getElementById('inventory-section');
    const editModeBtn = document.getElementById('edit-mode-btn');
    const deleteModeBtn = document.getElementById('delete-mode-btn');
    const addSingleBtn = document.getElementById('add-single-btn');
    let currentMode = null;
    let originalValues = new Map();

    // Edit mode functionality - direct inline editing with Enter to save
    editModeBtn.addEventListener('click', function() {
        if (currentMode === 'edit') {
            // Exit edit mode
            inventorySection.classList.remove('edit-mode');
            currentMode = null;
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
        } else {
            // Enter edit mode
            if (inventorySection.classList.contains('delete-mode')) {
                inventorySection.classList.remove('delete-mode');
                deleteModeBtn.style.opacity = '1';
            }
            inventorySection.classList.add('edit-mode');
            currentMode = 'edit';
            editModeBtn.style.opacity = '0.5';

            // Store original values and make all display texts editable
            document.querySelectorAll('.display-text').forEach(text => {
                originalValues.set(text, text.textContent);
                text.contentEditable = 'true';
                text.style.cursor = 'text';
                text.addEventListener('keydown', handleEnterKey);
                text.addEventListener('blur', handleBlur);
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
            this.textContent = originalValues.get(this);
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
        const displayTexts = row.querySelectorAll('.display-text');
        const itemId = row.getAttribute('data-item-id');

        if (displayTexts.length >= 3) {
            const name = displayTexts[0].textContent.trim();
            const description = displayTexts[1].textContent.trim();
            const quantity = displayTexts[2].textContent.trim();

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
                    // Update original values
                    originalValues.set(displayTexts[0], name);
                    originalValues.set(displayTexts[1], description);
                    originalValues.set(displayTexts[2], quantity);

                    // Remove edit styling
                    displayTexts.forEach(text => {
                        text.contentEditable = 'false';
                        text.style.border = 'none';
                        text.style.padding = '0';
                        text.style.backgroundColor = 'transparent';
                    });

                    // Exit edit mode
                    inventorySection.classList.remove('edit-mode');
                    currentMode = null;
                    editModeBtn.style.opacity = '1';
                } else {
                    alert('Error saving changes: ' + data.error);
                    // Restore original value
                    element.textContent = originalValues.get(element);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error saving changes');
                // Restore original value
                element.textContent = originalValues.get(element);
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
        // Create a new row with empty fields
        const table = document.querySelector('.inventory-table');
        const newRow = document.createElement('div');
        newRow.className = 'table-row new-item-row';
        newRow.setAttribute('data-item-id', 'new');

        newRow.innerHTML = `
            <div class="table-col" data-label="ITEM">
                <span class="display-text new-item-name"></span>
            </div>
            <div class="table-col" data-label="DESCRIPTION">
                <span class="display-text new-item-description"></span>
            </div>
            <div class="table-col" data-label="QUANTITY">
                <span class="display-text new-item-quantity"></span>
            </div>
            <div class="table-col" data-label="DATE ADDED">
                <span class="new-item-date">New Item</span>
            </div>
        `;

        // Insert the new row before the add button container
        const addButtonContainer = document.querySelector('.add-button-container');
        table.insertBefore(newRow, addButtonContainer);

        // Make the new row editable immediately
        const displayTexts = newRow.querySelectorAll('.display-text');
        displayTexts.forEach(text => {
            text.contentEditable = 'true';
            text.style.border = '1px solid #007bff';
            text.style.padding = '4px';
            text.style.borderRadius = '4px';
            text.style.backgroundColor = '#f8f9fa';
            text.style.cursor = 'text';
            text.addEventListener('keydown', handleNewItemEnter);
        });

        // Focus on the name field
        displayTexts[0].focus();
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
        const displayTexts = row.querySelectorAll('.display-text');
        const name = displayTexts[0].textContent.trim();
        const description = displayTexts[1].textContent.trim();
        const quantity = displayTexts[2].textContent.trim();

        // Only save if all fields have content
        if (name && description && quantity) {
            saveNewItem(this);
        }
    }

    // Save new item
    function saveNewItem(element) {
        const row = element.closest('.table-row');
        const displayTexts = row.querySelectorAll('.display-text');

        if (displayTexts.length >= 3) {
            const name = displayTexts[0].textContent.trim();
            const description = displayTexts[1].textContent.trim();
            const quantity = displayTexts[2].textContent.trim();

            // Validate data
            if (!name) {
                alert('Item name cannot be empty');
                displayTexts[0].focus();
                return;
            }

            if (isNaN(quantity) || quantity < 0) {
                alert('Quantity must be a valid number');
                displayTexts[2].focus();
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
