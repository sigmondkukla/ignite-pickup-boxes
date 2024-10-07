<script setup>
import ItemService from '@/service/ItemService';
import { FilterMatchMode } from '@primevue/core/api';
import { useToast } from 'primevue/usetoast';
import { onMounted, ref } from 'vue';

onMounted(() => {
    ItemService.getPrints().then((data) => (items.value = data));
});

const toast = useToast();
const items = ref();
const itemDialog = ref(false);
const newItem = ref(false);
const deleteItemDialog = ref(false);
const deleteItemsDialog = ref(false);
const item = ref({});
const selectedItems = ref();
const filters = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS }
});
const submitted = ref(false);

function openNew() {
    item.value = {};
    submitted.value = false;
    itemDialog.value = true;
    newItem.value = true;
}

function hideDialog() {
    itemDialog.value = false;
    submitted.value = false;
}

function saveItem() {
    submitted.value = true;

    if (item?.value.name?.trim()) {
        if (item.value.id) {
            item.value.inventoryStatus = item.value.inventoryStatus.value ? item.value.inventoryStatus.value : item.value.inventoryStatus;
            items.value[findIndexById(item.value.id)] = item.value;
            toast.add({ severity: 'success', summary: 'Successful', detail: 'Item Updated', life: 3000 });
        } else {
            item.value.id = createId();
            item.value.code = createId();
            item.value.image = 'item-placeholder.svg';
            item.value.inventoryStatus = item.value.inventoryStatus ? item.value.inventoryStatus.value : 'INSTOCK';
            items.value.push(item.value);
            toast.add({ severity: 'success', summary: 'Successful', detail: 'Item Created', life: 3000 });
        }

        itemDialog.value = false;
        item.value = {};
    }
}

function editItem(item) {
    item.value = { ...item };
    newItem.value = false;
    itemDialog.value = true;
}

function confirmDeleteItem(item) {
    item.value = item;
    deleteItemDialog.value = true;
}

function deleteItem() {
    ItemService.deleteItem(item.value.id).then(() => {
        deleteItemDialog.value = false;
        ItemService.getPrints().then((data) => (items.value = data));
        toast.add({ severity: 'success', summary: 'Successful', detail: 'Item Deleted', life: 3000 });
    });
}

function findIndexById(id) {
    let index = -1;
    for (let i = 0; i < items.value.length; i++) {
        if (items.value[i].id === id) {
            index = i;
            break;
        }
    }
    return index;
}

function confirmDeleteSelected() {
    deleteItemsDialog.value = true;
}

function deleteSelectedItems() {
    items.value = items.value.filter((val) => !selectedItems.value.includes(val));
    deleteItemsDialog.value = false;
    selectedItems.value = null;
    toast.add({ severity: 'success', summary: 'Successful', detail: 'Items Deleted', life: 3000 });
}
</script>

<template>
    <div>
        <div class="card">
            <Toolbar class="mb-6">
                <template #start>
                    <Button label="New" icon="pi pi-plus" severity="secondary" class="mr-2" @click="openNew" />
                    <Button label="Delete" icon="pi pi-trash" severity="danger" @click="confirmDeleteSelected"
                        :disabled="!selectedItems || !selectedItems.length" />
                </template>

                <template #end>
                </template>
            </Toolbar>
            <!-- FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown -->
            <DataTable ref="dt" v-model:selection="selectedItems" :value="items" dataKey="id" :paginator="true"
                :rows="10" :filters="filters"
                paginatorTemplate="PrevPageLink PageLinks NextPageLink CurrentPageReport RowsPerPageDropdown"
                :rowsPerPageOptions="[10, 20, 30]"
                currentPageReportTemplate="Showing {first} to {last} of {totalRecords} items">

                <!-- Header and searchbar -->
                <template #header>
                    <div class="flex flex-wrap gap-2 items-center justify-between">
                        <h4 class="m-0 font-bold">Manage Prints</h4>
                        <IconField>
                            <InputIcon>
                                <i class="pi pi-search" />
                            </InputIcon>
                            <InputText v-model="filters['global'].value" placeholder="Search" />
                        </IconField>
                    </div>
                </template>

                <Column selectionMode="multiple" style="width: 3rem"></Column>
                <Column field="print_number" header="Print #" sortable style="min-width: 8rem"></Column>
                <Column field="email" header="Email" sortable style="min-width: 16rem"></Column>
                <Column field="box_id" header="Box #" sortable style="min-width: 8rem"></Column>
                <Column field="code" header="Code" style="min-width: 6rem"></Column>
                <Column field="status" header="Status" sortable style="min-width: 6rem"></Column>
                <Column style="min-width: 8rem" header="Actions">
                    <template #body="slotProps">
                        <Button v-tooltip.bottom="{ value: 'Edit', showDelay: 250 }" icon="pi pi-pencil" outlined
                            rounded class="mr-2" @click="editItem(slotProps.data)" />
                        <Button v-tooltip.bottom="{ value: 'Open box', showDelay: 250 }" icon="pi pi-unlock" outlined
                            rounded severity="info" class="mr-2" @click="" />
                        <Button v-tooltip.bottom="{ value: 'Delete', showDelay: 250 }" icon="pi pi-trash" outlined
                            rounded severity="danger" @click="confirmDeleteItem(slotProps.data)" />
                    </template>
                </Column>
            </DataTable>
        </div>

        <!-- Add/edit item dialog -->
        <Dialog v-model:visible="itemDialog" :style="{ width: '450px' }" header="Item Details" :modal="true">
            <div class="flex flex-col gap-6">
                <div>
                    <label for="print_number" class="block font-bold mb-3">Print Number</label>
                    <InputText id="print_number" v-model.trim="item.print_number" required="true" autofocus
                        :invalid="submitted && !item.print_number" fluid integeronly />
                    <small v-if="submitted && !item.print_number" class="text-red-500">Print number is required.</small>
                </div>
                <div>
                    <label for="email" class="block font-bold mb-3">Email</label>
                    <InputText id="email" v-model.trim="item.email" required="false" fluid autocomplete="false" />
                </div>
                <div>
                    <InputGroup>
                        <InputGroupAddon>
                            <label for="code" class="font-bold text-surface-700">Code</label>
                        </InputGroupAddon>
                        <InputText id="code" v-model.trim="item.code" disabled="true" integeronly fluid />
                        <!-- <Button label="Regenerate" icon="pi pi-refresh" severity="secondary" @click="" /> -->
                    </InputGroup>
                </div>
                <div>
                    <InputGroup>
                        <InputGroupAddon>
                            <label for="box_id" class="font-bold text-surface-700">Box Number</label>
                        </InputGroupAddon>
                        <InputText id="box_id" v-model.trim="item.box_id" required="true" integeronly fluid />
                        <Button label="Auto" icon="pi pi-bolt" severity="secondary" @click="" />
                    </InputGroup>
                </div>
                <div>
                    <label for="status" class="block font-bold mb-3">Status</label>
                    <InputText id="status" v-model.trim="item.status" required="false" fluid autocomplete="false" />
                </div>
            </div>

            <template #footer>
                <Button label="Cancel" severity="secondary" icon="pi pi-times" text @click="hideDialog" />
                <Button label="Save" icon="pi pi-check" @click="saveItem" />
            </template>
        </Dialog>

        <!-- Delete item confirmation -->
        <Dialog v-model:visible="deleteItemDialog" :style="{ width: '450px' }" header="Confirm deletion" :modal="true">
            <div class="flex items-center gap-4">
                <i class="pi pi-exclamation-triangle !text-3xl" />
                <span v-if="item">Are you sure you want to delete <b>{{ item.name }}</b>?</span>
            </div>
            <template #footer>
                <Button label="No" icon="pi pi-times" severity="secondary" text @click="deleteItemDialog = false" />
                <Button label="Yes" icon="pi pi-trash" severity="danger" @click="deleteItem" />
            </template>
        </Dialog>

        <!-- Delete multiple items confirmation -->
        <Dialog v-model:visible="deleteItemsDialog" :style="{ width: '450px' }" header="Confirm deletion" :modal="true">
            <div class="flex items-center gap-4">
                <i class="pi pi-exclamation-triangle !text-3xl" />
                <span v-if="item">Are you sure you want to delete all of the selected items?</span>
            </div>
            <template #footer>
                <Button label="No" icon="pi pi-times" severity="secondary" text @click="deleteItemsDialog = false" />
                <Button label="Yes" icon="pi pi-trash" severity="danger" text @click="deleteSelectedItems" />
            </template>
        </Dialog>
    </div>
</template>
