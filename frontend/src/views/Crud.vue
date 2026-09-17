<script setup>
import ItemService from '@/service/ItemService';
import { FilterMatchMode } from '@primevue/core/api';
import { useToast } from 'primevue/usetoast';
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const toast = useToast();
const router = useRouter();

const items = ref([]);
const itemDialog = ref(false);
const newItem = ref(false);
const deleteItemDialog = ref(false);
const deleteItemsDialog = ref(false);
const showReadMe = ref(false);

const item = ref({});
const selectedItems = ref([]);

const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS }
});

const submitted = ref(false);

async function refreshItems() {
  items.value = await ItemService.getPrints();
}

onMounted(async () => {
  await refreshItems();
});

function goToSettings() {
  router.push('/settings');
}

function openNew() {
  item.value = { status: 0 };
  submitted.value = false;
  itemDialog.value = true;
  newItem.value = true;
}

function hideDialog() {
  itemDialog.value = false;
  submitted.value = false;
}

async function fetchEmailForPrintNumber() {
  if (!item.value?.print_number) {
    item.value.email = '';
    return;
  }

  try {
    const response = await fetch(`/api/print-email/${item.value.print_number}`);
    const data = await response.json();

    if (response.ok && data.email) {
      item.value.email = data.email;
    } else {
      item.value.email = '';
    }
  } catch (error) {
    console.error('Failed to fetch email:', error);
    item.value.email = '';
  }
}

function isValidBoxNumber(boxId) {
  const n = Number(boxId);
  if (!Number.isInteger(n)) return false;
  if (n < 1 || n > 30) return false;
  if (n === 31 || n === 32) return false;
  return true;
}

async function saveItem() {
  submitted.value = true;

  if (!item.value?.print_number) return;

  if (!isValidBoxNumber(item.value?.box_id)) {
    toast.add({
      severity: 'warn',
      summary: 'Invalid Box Number',
      detail: 'Enter numbers between 1 and 30',
      life: 3500
    });
    return;
  }

  if (newItem.value) {
    await ItemService.createPrint(item.value);
    toast.add({ severity: 'success', summary: 'Successful', detail: 'Item Created', life: 3000 });
  } else {
    await ItemService.updatePrint(item.value);
    toast.add({ severity: 'success', summary: 'Successful', detail: 'Item Updated', life: 3000 });
  }

  await refreshItems();
  itemDialog.value = false;
  item.value = {};
}

function editItem(selectedItem) {
  item.value = { ...selectedItem };
  newItem.value = false;
  itemDialog.value = true;
}

function confirmDeleteItem(selectedItem) {
  item.value = { ...selectedItem };
  deleteItemDialog.value = true;
}

async function deleteItemFn() {
  await ItemService.deletePrint(item.value.id);
  deleteItemDialog.value = false;
  await refreshItems();
  toast.add({ severity: 'success', summary: 'Successful', detail: 'Item Deleted', life: 3000 });
}

function confirmDeleteSelected() {
  deleteItemsDialog.value = true;
}

async function deleteSelectedItems() {
  const ids = (selectedItems.value || []).map((x) => x.id);
  if (!ids.length) return;

  await ItemService.deletePrints(ids);
  await refreshItems();

  deleteItemsDialog.value = false;
  selectedItems.value = [];
  toast.add({ severity: 'success', summary: 'Successful', detail: 'Items Deleted', life: 3000 });
}

async function unlockPrint(selectedItem) {
  await ItemService.unlockPrint(selectedItem.id);
  await refreshItems();
  toast.add({ severity: 'success', summary: 'Successful', detail: 'Print unlocked', life: 3000 });
}

function getStatus(status) {
  switch (status) {
    case 0:
      return 'In Box';
    case 1:
      return 'Picked Up';
    case 2:
      return 'Abandoned';
    case 3:
      return 'Awaiting Pickup';
    default:
      return 'Status error';
  }
}

function getStatusColor(status) {
  switch (status) {
    case 0:
      return 'info';
    case 1:
      return 'success';
    case 2:
      return 'danger';
    case 3:
      return 'warning';
    default:
      return 'info';
  }
}

const statuses = ref([
  { name: 'In Box', status: 0 },
  { name: 'Picked Up', status: 1 },
  { name: 'Abandoned', status: 2 },
  { name: 'Awaiting Pickup', status: 3 }
]);
</script>

<template>
  <div>
    <div class="card">
      <Toolbar class="mb-6">
        <template #start>
          <Button label="New" icon="pi pi-plus" severity="secondary" class="mr-2" @click="openNew" />
          <Button
            label="Delete"
            icon="pi pi-trash"
            severity="danger"
            @click="confirmDeleteSelected"
            :disabled="!selectedItems || !selectedItems.length"
          />
        </template>

        <template #end>
          <Button
            label="Read Me"
            icon="pi pi-book"
            severity="secondary"
            class="mr-2"
            @click="showReadMe = !showReadMe"
          />

          <Button
            label="Settings"
            icon="pi pi-cog"
            severity="secondary"
            class="mr-2"
            @click="goToSettings"
          />

          <Button label="Refresh" icon="pi pi-refresh" @click="refreshItems" outlined />
        </template>
      </Toolbar>

      <div v-if="showReadMe" class="readme-card mb-6">
        <h3 class="readme-title">Welcome (Read Me First)</h3>

        <p>Use this panel to <strong>add, manage, and remove prints</strong> from pickup boxes.</p>

        <h4>Add a Print</h4>
        <ol>
          <li>Click the <strong>New</strong> button.</li>
          <li>Enter the <strong>print number</strong>. The email fills automatically.</li>
          <li>Enter a <strong>box number</strong> or click <strong>Auto</strong>.</li>
          <li>Click <strong>Save</strong>.</li>
          <li>Click <strong>Unlock</strong> to open the box.</li>
          <li>Place the print inside and close the door.</li>
        </ol>

        <h4>Update or Move a Print</h4>
        <ol>
          <li>Click <strong>Edit</strong> next to the print.</li>
          <li>Change the box number or status.</li>
          <li>Click <strong>Save</strong>.</li>
        </ol>

        <h4>Delete a Print</h4>
        <ol>
          <li>
            For one print, click the <strong>Delete</strong> button next to that print.
          </li>
          <li>
            For multiple prints, select the checkboxes first, then click the top <strong>Delete</strong> button.
          </li>
          <li>Confirm the deletion.</li>
        </ol>

        <h4>Important</h4>
        <ol>
          <li>Users receive an email with a pickup code.</li>
          <li>Use <strong>Unlock</strong> if a user needs help opening a box.</li>
          <li>If a code expires, create a new print record.</li>
        </ol>
      </div>

      <DataTable
        ref="dt"
        v-model:selection="selectedItems"
        :value="items"
        dataKey="id"
        :paginator="true"
        :rows="10"
        :filters="filters"
        paginatorTemplate="PrevPageLink PageLinks NextPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[10, 20, 30]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} items"
        sort-field="print_number"
        :sort-order="-1"
      >
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

        <Column field="status" header="Status" sortable style="min-width: 6rem">
          <template #body="slotProps">
            <Tag :value="getStatus(slotProps.data.status)" :severity="getStatusColor(slotProps.data.status)" />
          </template>
        </Column>

        <Column style="min-width: 8rem" header="Actions">
          <template #body="slotProps">
            <Button
              v-tooltip.bottom="{ value: 'Edit', showDelay: 250 }"
              icon="pi pi-pencil"
              outlined
              rounded
              class="mr-2"
              @click="editItem(slotProps.data)"
            />
            <Button
              v-tooltip.bottom="{ value: 'Open box', showDelay: 250 }"
              icon="pi pi-unlock"
              outlined
              rounded
              severity="info"
              class="mr-2"
              @click="unlockPrint(slotProps.data)"
            />
            <Button
              v-tooltip.bottom="{ value: 'Delete', showDelay: 250 }"
              icon="pi pi-trash"
              outlined
              rounded
              severity="danger"
              @click="confirmDeleteItem(slotProps.data)"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <Dialog v-model:visible="itemDialog" :style="{ width: '450px' }" header="Item Details" :modal="true">
      <div class="flex flex-col gap-6">
        <div>
          <label for="print_number" class="block font-bold mb-3">Print Number</label>
          <InputText
            id="print_number"
            v-model.trim="item.print_number"
            @blur="fetchEmailForPrintNumber"
            required="true"
            autofocus
            :invalid="submitted && !item.print_number"
            fluid
            integeronly
          />
          <small v-if="submitted && !item.print_number" class="text-red-500">Print number is required.</small>
        </div>

        <div>
          <label for="email" class="block font-bold mb-3">Email</label>
          <InputText id="email" v-model.trim="item.email" fluid autocomplete="off" readonly />
        </div>

        <div>
          <InputGroup>
            <InputGroupAddon>
              <label for="code" class="font-bold text-surface-700">Code</label>
            </InputGroupAddon>
            <InputText id="code" v-model.trim="item.code" disabled="true" integeronly fluid />
          </InputGroup>
        </div>

        <div>
          <InputGroup>
            <InputGroupAddon>
              <label for="box_id" class="font-bold text-surface-700">Box Number</label>
            </InputGroupAddon>
            <InputText id="box_id" v-model.trim="item.box_id" required="true" integeronly fluid />
            <Button
              label="Auto"
              icon="pi pi-bolt"
              severity="secondary"
              @click="ItemService.getNextAvailableBox().then((box_id) => (item.box_id = box_id))"
            />
          </InputGroup>
        </div>

        <div v-if="!newItem.valueOf()">
          <label for="status" class="block font-bold mb-3">Status</label>
          <Select
            id="status"
            v-model="item.status"
            :options="statuses"
            optionLabel="name"
            optionValue="status"
            class="w-full md:w-56"
          />
        </div>
      </div>

      <template #footer>
        <Button label="Cancel" severity="secondary" icon="pi pi-times" text @click="hideDialog" />
        <Button label="Save" icon="pi pi-check" @click="saveItem" />
      </template>
    </Dialog>

    <Dialog v-model:visible="deleteItemDialog" :style="{ width: '450px' }" header="Confirm deletion" :modal="true">
      <div class="flex items-center gap-4">
        <i class="pi pi-exclamation-triangle !text-3xl" />
        <span v-if="item">
          Are you sure you want to delete print <strong>#{{ item.print_number }}</strong>?
        </span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" severity="secondary" text @click="deleteItemDialog = false" outlined />
        <Button label="Yes" icon="pi pi-trash" severity="danger" @click="deleteItemFn" outlined />
      </template>
    </Dialog>

    <Dialog v-model:visible="deleteItemsDialog" :style="{ width: '450px' }" header="Confirm deletion" :modal="true">
      <div class="flex items-center gap-4">
        <i class="pi pi-exclamation-triangle !text-3xl" />
        <span>Are you sure you want to delete all of the selected items?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" severity="secondary" text @click="deleteItemsDialog = false" outlined />
        <Button label="Yes" icon="pi pi-trash" severity="danger" text @click="deleteSelectedItems" outlined />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.readme-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 1.25rem;
  line-height: 1.6;
}

.readme-title {
  font-weight: 700;
  margin-bottom: 0.75rem;
}

.readme-card h4 {
  font-weight: 700;
  margin-top: 1rem;
  margin-bottom: 0.4rem;
}

.readme-card ol {
  list-style-type: decimal;
  margin-left: 1.5rem;
  margin-top: 0.5rem;
  margin-bottom: 1rem;
  padding-left: 1rem;
}

.readme-card li {
  margin-bottom: 0.35rem;
}
</style>
