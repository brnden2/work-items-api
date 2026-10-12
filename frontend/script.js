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

const previousPage = document.getElementById("previous-page");
const nextPage = document.getElementById("next-page");
const pageLabel = document.getElementById("page-label");

const pageSize = 10;
let currentOffset = 0;
let hasNextPage = false;
let pageLoaded = false;


async function loadWorkItems(targetOffset = currentOffset) {
    const requestId = ++latestLoad;
    previousPage.disabled = true;
    nextPage.disabled = true;
    filterMessage.textContent = "Loading work items…";

    try {
        const params = new URLSearchParams(appliedFilters);
        params.set("offset", targetOffset);
        params.set("limit", pageSize + 1);
        const response = await fetch(`${API_URL}/work-items?${params.toString()}`);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const items = await response.json();

        if (requestId !== latestLoad) return;

        if (!items.length && targetOffset > 0){
            return await loadWorkItems(
                Math.max(0, targetOffset - pageSize)
            );
        }

        currentOffset = targetOffset;
        hasNextPage = items.length > pageSize;
        pageLoaded = true;

        const visibleItems = items.slice(0, pageSize);
        workItemsList.replaceChildren();

        for (const item of visibleItems) {
            const listItem = document.createElement("li");
            listItem.textContent = `${item.id} - ${item.title} - ${item.status}`;
            workItemsList.appendChild(listItem);
        }

        pageLabel.textContent =
            `Page ${Math.floor(currentOffset / pageSize) + 1}`;

        filterMessage.textContent = visibleItems.length
            ? `Showing results ${currentOffset + 1}-${currentOffset + visibleItems.length}.`
            : "No work items found. Try another search or clear the filters.";
    } catch (error) {
        if (requestId !== latestLoad) return;

        filterMessage.textContent =
            "Could not load work items. Check that the API is running and select Refresh results.";
        console.error("Failed to load work items:", error);
    } finally {
        if (requestId === latestLoad) {
            previousPage.disabled = !pageLoaded || currentOffset === 0;
            nextPage.disabled = !pageLoaded || !hasNextPage;
        }
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


loadButton.addEventListener("click", () => loadWorkItems());

workItemForm.addEventListener("submit", createWorkItem);

filterForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const params = new URLSearchParams();
    const query = searchTitle.value.trim();

    if (query) params.set("q", query);
    if (filterStatus.value) params.set("status", filterStatus.value);

    appliedFilters = params.toString();
    currentOffset = 0;
    pageLoaded = false;
    hasNextPage = false;
    workItemsList.replaceChildren();
    pageLabel.textContent = "Page 1";
    loadWorkItems(0);
});

document.getElementById("clear-filters").addEventListener("click", () => {
    filterForm.reset();
    appliedFilters = "";
    currentOffset = 0;
    pageLoaded = false;
    hasNextPage = false;
    workItemsList.replaceChildren();
    pageLabel.textContent = "Page 1";
    loadWorkItems(0);
});

previousPage.addEventListener("click", () => {
    if (currentOffset > 0) {
        loadWorkItems(currentOffset - pageSize);
    }
});

nextPage.addEventListener("click", () => {
    if (hasNextPage) {
        loadWorkItems(currentOffset + pageSize);
    }
});
