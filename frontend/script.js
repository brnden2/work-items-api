const API_URL = "http://127.0.0.1:8000";

const loadButton = document.getElementById("load-button");
const workItemsList = document.getElementById("work-items-list");

const workItemForm = document.getElementById("work-item-form");
const titleInput = document.getElementById("title");
const statusInput = document.getElementById("status");
const message = document.getElementById("message");


async function loadWorkItems() {
    try {
        const response = await fetch(`${API_URL}/work-items`);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const items = await response.json();

        workItemsList.innerHTML = "";

        for (const item of items) {
            const listItem = document.createElement("li");

            listItem.textContent =
                `${item.id} - ${item.title} - ${item.status}`;

            workItemsList.appendChild(listItem);
        }

    } catch (error) {
        console.error("Failed to load work items:", error);
    }
}


async function createWorkItem(event) {
    event.preventDefault();

    const newItem = {
        title: titleInput.value.trim(),
        status: statusInput.value
    };

    try {
        const response = await fetch(`${API_URL}/work-items`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(newItem)
        });

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const createdItem = await response.json();

        message.textContent =
            `Created work item ${createdItem.id} successfully.`;

        workItemForm.reset();

        await loadWorkItems();

    } catch (error) {
        message.textContent = "Failed to create work item.";
        console.error("Failed to create work item:", error);
    }
}


loadButton.addEventListener("click", loadWorkItems);

workItemForm.addEventListener("submit", createWorkItem);