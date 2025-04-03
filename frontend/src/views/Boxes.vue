

<template>
  <div>
    <!-- Grid container for 24 boxes -->
    <div class="grid grid-cols-4 gap-4">
      <div v-for="box in boxes" :key="box" class="p-4 border rounded shadow-sm">
        <h3 class="font-bold text-lg mb-2">Box {{ box }}</h3>
        <div v-if="getPrintForBox(box)">
          <p class="mb-2">Print #: {{ getPrintForBox(box).print_number }}</p>
          <p class="mb-4">Status: {{ getStatus(getPrintForBox(box).status) }}</p>
          <div class="flex space-x-2">
            <Button label="Edit" icon="pi pi-pencil" @click="editItem(getPrintForBox(box))" />
          </div>
        </div>
        <div v-else>
          <p class="mb-4 italic">Empty</p>
          <Button label="New" icon="pi pi-plus" @click="createNew(box)" />
        </div>
        <div>
            <Button label="Open Box" icon="pi pi-unlock" class="p-button-info" @click="unlockPrint(getPrintForBox(box))" />
        </div>
      </div>
    </div>

    <!-- Dialog for creating/editing prints -->
    <Dialog v-model:visible="itemDialog" :style="{ width: '450px' }" header="Item Details" :modal="true">
      <div class="flex flex-col gap-6">
        <div>
          <label for="print_number" class="block font-bold mb-3">Print Number</label>
          <InputText id="print_number" v-model.trim="item.print_number" required autofocus 
                     :invalid="submitted && !item.print_number" fluid integeronly />
          <small v-if="submitted && !item.print_number" class="text-red-500">Print number is required.</small>
        </div>
        <div>
          <label for="email" class="block font-bold mb-3">Email</label>
          <InputText id="email" v-model.trim="item.email" fluid autocomplete="off" />
        </div>
        <div>
          <InputGroup>
            <InputGroupAddon>
              <label for="code" class="font-bold text-surface-700">Code</label>
            </InputGroupAddon>
            <InputText id="code" v-model.trim="item.code" disabled integeronly fluid />
          </InputGroup>
        </div>
        <div>
          <InputGroup>
            <InputGroupAddon>
              <label for="box_id" class="font-bold text-surface-700">Box Number</label>
            </InputGroupAddon>
            <InputText id="box_id" v-model.trim="item.box_id" required integeronly fluid />
            <Button label="Auto" icon="pi pi-bolt" severity="secondary"
                    @click="ItemService.getNextAvailableBox().then(box_id => item.box_id = box_id)" />
          </InputGroup>
        </div>
        <div v-if="!newItem">
          <label for="status" class="block font-bold mb-3">Status</label>
          <Select id="status" v-model="item.status" :options="statuses" optionLabel="name"
                  optionValue="status" class="w-full md:w-56" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" icon="pi pi-times" text @click="hideDialog" />
        <Button label="Save" icon="pi pi-check" @click="saveItem" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ItemService from '@/service/ItemService';
import { useToast } from 'primevue/usetoast';
import { FilterMatchMode } from '@primevue/core/api';

const toast = useToast();
const items = ref([]);

// On component mount, load prints from the service.
onMounted(() => {
  ItemService.getPrints().then(data => {
    items.value = data;
  });
});

// Create an array of box numbers from 1 to 24.
const boxes = Array.from({ length: 24 }, (_, i) => i + 1);

// Returns the print corresponding to the specified box number.
function getPrintForBox(boxId) {
  return items.value.find(print => Number(print.box_id) === boxId);
}

// Dialog-related reactive variables.
const itemDialog = ref(false);
const newItem = ref(false);
const submitted = ref(false);
const item = ref({});

// Predefined statuses.
const statuses = ref([
  { name: 'In Box', status: 0 },
  { name: 'Picked Up', status: 1 },
  { name: 'Abandoned', status: 2 }
]);

// Opens a new item dialog.
function openNew() {
  item.value = {};
  submitted.value = false;
  itemDialog.value = true;
  newItem.value = true;
  item.value.status = 0;
}

// Opens the dialog with the box number pre-assigned for creating a new print.
function createNew(boxId) {
  openNew();
  item.value.box_id = boxId;
}

// Hides the dialog.
function hideDialog() {
  itemDialog.value = false;
  submitted.value = false;
}

// Saves the item: creates a new print or updates an existing one.
function saveItem() {
  if (newItem.value) {
    ItemService.createPrint(item.value).then(() => {
      itemDialog.value = false;
      item.value = {};
      ItemService.getPrints().then(data => items.value = data);
      toast.add({ severity: 'success', summary: 'Successful', detail: 'Item Created', life: 3000 });
    });
  } else {
    ItemService.updatePrint(item.value).then(() => {
      itemDialog.value = false;
      item.value = {};
      ItemService.getPrints().then(data => items.value = data);
      toast.add({ severity: 'success', summary: 'Successful', detail: 'Item Updated', life: 3000 });
    });
  }
  submitted.value = true;
  itemDialog.value = false;
  item.value = {};
}

// Opens the edit dialog with the selected print.
function editItem(selectedItem) {
  item.value = { ...selectedItem };
  newItem.value = false;
  itemDialog.value = true;
}

// Unlocks the print in the specified box.
function unlockPrint(selectedItem) {
  ItemService.unlockPrint(selectedItem.id).then(() => {
    ItemService.getPrints().then(data => items.value = data);
    toast.add({ severity: 'success', summary: 'Successful', detail: 'Print unlocked', life: 3000 });
  });
}

// Returns a human-readable status string.
function getStatus(status) {
  switch (status) {
    case 0:
      return 'In Box';
    case 1:
      return 'Picked Up';
    case 2:
      return 'Abandoned';
    default:
      return 'Status error';
  }
}
</script>

<style scoped>
/* Example grid styling: adjust as needed */
.grid {
  display: grid;
}
.grid-cols-4 {
  grid-template-columns: repeat(4, 1fr);
}
.gap-4 {
  gap: 1rem;
}
.box-card {
  background-color: #fff;
  border: 1px solid #e5e7eb;
  padding: 1rem;
  text-align: center;
}
</style>
