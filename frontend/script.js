const API_URL = "http://127.0.0.1:8000";

const loadButton = document.getElementById("load-button");
const workItemsList = document.getElementById("work-items-list");

const workItemForm = document.getElementById("work-item-form");
const titleInput = document.getElementById("title");
const statusInput = document.getElementById("status");
const message = document.getElementById("message");
const filterForm = document.getElementById("filter-form");
const searchTitle = document.getElementById("search-title");
const filterStatus = document.getElementById("filter-status");
const filterMessage = document.getElementById("filter-message");

let latestLoad = 0;
let appliedFilters = "";

async function loadWorkItems() {
    const requestId = ++latestLoad;
    filterMessage.textContent = "Loading work items…";
    workItemsList.replaceChildren();

    try {
        const query = appliedFilters ? `?${appliedFilters}` : "";
        const response = await fetch(`${API_URL}/work-items${query}`);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const items = await response.json();

        if (requestId !== latestLoad) return;

        for (const item of items) {
            const listItem = document.createElement("li");
            listItem.textContent =
                `${item.id} - ${item.title} - ${item.status}`;
            workItemsList.appendChild(listItem);
        }

        filterMessage.textContent = items.length
            ? `${items.length} work item${items.length === 1 ? "" : "s"} found.`
            : "No work items found. Try another search or clear the filters.";
    } catch (error) {
        if (requestId !== latestLoad) return;

        filterMessage.textContent =
            "Could not load work items. Check that the API is running and try again.";
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

filterForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const params = new URLSearchParams();
    const query = searchTitle.value.trim();

    if (query) params.set("q", query);
    if (filterStatus.value) params.set("status", filterStatus.value);

    appliedFilters = params.toString();
    loadWorkItems();
});

document.getElementById("clear-filters").addEventListener("click", () => {
    filterForm.reset();
    appliedFilters = "";
    loadWorkItems();
});