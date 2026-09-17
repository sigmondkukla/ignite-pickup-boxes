<template>
  <div class="layout-page">
    <!-- 4x8 logical layout -->
    <div class="layout-grid">
      <div
        v-for="(cell, idx) in flatLayout"
        :key="idx"
        class="cell"
        :class="cellClass(cell)"
      >
        <!-- SCANNER SLOT -->
        <template v-if="cell === null">
          <div class="scanner-label">SCANNER</div>
        </template>

        <!-- REAL BOX -->
        <template v-else>
          <div class="cell-header">
            <div class="box-title">Box {{ cell }}</div>

            <span class="status-pill" :class="pillClass(cell)">
              {{ pillText(cell) }}
            </span>
          </div>

          <div class="cell-body">
            <div v-if="printsByBox[cell]" class="meta">
              <div class="line">
                <span class="k">Print</span>
                <span class="v">#{{ printsByBox[cell].print_number }}</span>
              </div>
            </div>

            <div v-else class="meta meta-empty">
              Ready
            </div>

            <div class="actions">
              <template v-if="!isDisabled(cell)">
                <Button
                  v-if="printsByBox[cell]"
                  icon="pi pi-pencil"
                  size="small"
                  outlined
                  rounded
                  v-tooltip.bottom="'Edit'"
                  @click="editItem(printsByBox[cell])"
                />

                <Button
                  v-else
                  icon="pi pi-plus"
                  size="small"
                  outlined
                  rounded
                  v-tooltip.bottom="'New'"
                  @click="createNew(cell)"
                />

                <Button
                  icon="pi pi-unlock"
                  size="small"
                  outlined
                  rounded
                  severity="info"
                  v-tooltip.bottom="'Open Box'"
                  :disabled="!printsByBox[cell]"
                  @click="unlockPrint(printsByBox[cell])"
                />

                <Button
                  icon="pi pi-trash"
                  size="small"
                  outlined
                  rounded
                  severity="danger"
                  v-tooltip.bottom="'Delete'"
                  :disabled="!printsByBox[cell]"
                  @click="deletePrint(printsByBox[cell])"
                />
              </template>

              <template v-else>
                <div class="disabled-note">Disabled</div>
              </template>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Bottom: Disabled Boxes manager -->
    <div class="disabled-panel">
      <div class="panel-title">Disabled Boxes</div>

      <div class="panel-row">
        <div class="add-row">
          <InputNumber
            v-model="newDisabledBoxId"
            :min="1"
            :max="32"
            :step="1"
            showButtons
            buttonLayout="horizontal"
            incrementButtonIcon="pi pi-plus"
            decrementButtonIcon="pi pi-minus"
          />
          <InputText
            v-model="newDisabledReason"
            placeholder="Reason (optional)"
            class="reason"
          />
          <Button label="Disable" icon="pi pi-ban" severity="danger" @click="addDisabled()" />
        </div>

        <div class="hint">
          Boxes in this list become <b>RED</b> and cannot be used anywhere.
        </div>
      </div>

      <DataTable
        :value="disabledBoxes"
        dataKey="box_id"
        class="disabled-table"
        :rows="5"
        :paginator="true"
      >
        <Column field="box_id" header="Box #" style="width: 90px" />
        <Column field="reason" header="Reason" />
        <Column header="Actions" style="width: 120px">
          <template #body="slotProps">
            <Button
              icon="pi pi-trash"
              outlined
              rounded
              severity="danger"
              size="small"
              v-tooltip.bottom="'Remove'"
              @click="removeDisabled(slotProps.data.box_id)"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Dialog for creating/editing prints -->
    <Dialog v-model:visible="itemDialog" :style="{ width: '450px' }" header="Item Details" :modal="true">
      <div class="flex flex-col gap-6">
        <div>
          <label for="print_number" class="block font-bold mb-3">Print Number</label>
          <InputText
            id="print_number"
            v-model.trim="item.print_number"
            @blur="fetchEmailForPrintNumber"
            required
            autofocus
            :invalid="submitted && !item.print_number"
            fluid
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
            <InputText id="code" v-model.trim="item.code" disabled fluid />
          </InputGroup>
        </div>

        <div>
          <InputGroup>
            <InputGroupAddon>
              <label for="box_id" class="font-bold text-surface-700">Box Number</label>
            </InputGroupAddon>

            <InputNumber
              id="box_id"
              v-model="item.box_id"
              :min="1"
              :max="30"
              :step="1"
              showButtons
              buttonLayout="horizontal"
              incrementButtonIcon="pi pi-plus"
              decrementButtonIcon="pi pi-minus"
              fluid
            />

            <Button label="Auto" icon="pi pi-bolt" severity="secondary" @click="setAutoBox()" />
          </InputGroup>

          <small v-if="submitted && boxErrorMessage" class="text-red-500">
            {{ boxErrorMessage }}
          </small>
        </div>

        <div v-if="!newItem">
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
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import ItemService from '@/service/ItemService';
import { useToast } from 'primevue/usetoast';

import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputGroup from 'primevue/inputgroup';
import InputGroupAddon from 'primevue/inputgroupaddon';
import Select from 'primevue/select';

const toast = useToast();

const items = ref([]);
const disabledBoxes = ref([]);

// New logical layout (1..32)
// Scanner positions are 31 and 32, displayed as scanner tiles.
const layout = [
  [1, 2, 3, 4, 5, 6, 7, 8],
  [9, null, 10, 11, 12, 13, 14, null],
  [15, 16, 17, 18, 19, 20, 21, 22],
  [23, 24, 25, 26, 27, 28, 29, 30]
];

const flatLayout = computed(() => layout.flat());

// Permanently reserved scanner slots
const scannerSlots = new Set([31, 32]);

// Disabled boxes from API
const disabledSet = computed(
  () => new Set((disabledBoxes.value || []).map((x) => Number(x.box_id)))
);

async function refreshAll() {
  items.value = await ItemService.getPrints();
  disabledBoxes.value = await ItemService.getDisabledBoxes();
}

onMounted(refreshAll);

// Map prints by logical box_id
const printsByBox = computed(() => {
  const map = {};
  for (const p of items.value || []) {
    const b = Number(p.box_id);
    if (!Number.isNaN(b)) {
      map[b] = p;
    }
  }
  return map;
});

function isDisabled(boxId) {
  return disabledSet.value.has(Number(boxId));
}

function isValidBox(v) {
  const n = Number(v);
  if (!Number.isInteger(n) || n < 1 || n > 30) return false;
  if (scannerSlots.has(n)) return false;
  if (isDisabled(n)) return false;
  return true;
}

function normalizeBox(v) {
  if (v === null || v === undefined || v === '') return v;

  let n = Number(v);
  if (!Number.isInteger(n)) n = 1;
  if (n < 1) n = 1;
  if (n > 30) n = 30;

  const bad = (x) => scannerSlots.has(x) || isDisabled(x);

  if (bad(n)) {
    let f = n + 1;
    while (f <= 30 && bad(f)) f++;
    if (f <= 30) return f;

    let b = n - 1;
    while (b >= 1 && bad(b)) b--;
    if (b >= 1) return b;

    return null;
  }

  return n;
}

function cellClass(cell) {
  if (cell === null) return 'scanner';
  if (isDisabled(cell)) return 'disabled';
  if (!printsByBox.value[cell]) return 'empty';

  const st = Number(printsByBox.value[cell].status);
  if (st === 1) return 'picked';
  if (st === 3) return 'awaiting';
  return 'occupied';
}

function pillText(cell) {
  if (cell === null) return 'SCANNER';
  if (isDisabled(cell)) return 'Disabled';
  if (!printsByBox.value[cell]) return 'Empty';
  return getStatus(printsByBox.value[cell].status);
}

function pillClass(cell) {
  if (cell === null) return 'pill-scanner';
  if (isDisabled(cell)) return 'pill-disabled';
  if (!printsByBox.value[cell]) return 'pill-empty';

  const st = Number(printsByBox.value[cell].status);
  if (st === 1) return 'pill-picked';
  if (st === 3) return 'pill-awaiting';
  return 'pill-occupied';
}

const itemDialog = ref(false);
const newItem = ref(false);
const submitted = ref(false);
const item = ref({});
const boxErrorMessage = ref('');

watch(
  () => item.value.box_id,
  (v) => {
    const fixed = normalizeBox(v);
    if (fixed !== v) item.value.box_id = fixed;
  }
);

const statuses = ref([
  { name: 'In Box', status: 0 },
  { name: 'Picked Up', status: 1 },
  { name: 'Abandoned', status: 2 },
  { name: 'Awaiting Pickup', status: 3 }
]);

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
      return 'Unknown';
  }
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

function openNew() {
  item.value = { status: 0 };
  submitted.value = false;
  boxErrorMessage.value = '';
  itemDialog.value = true;
  newItem.value = true;
}

function createNew(boxId) {
  if (isDisabled(boxId)) {
    toast.add({ severity: 'error', summary: 'Box Disabled', detail: `Box ${boxId} is disabled.`, life: 3000 });
    return;
  }

  openNew();
  item.value.box_id = normalizeBox(boxId);
}

function hideDialog() {
  itemDialog.value = false;
  submitted.value = false;
  boxErrorMessage.value = '';
}

async function setAutoBox() {
  const box_id = await ItemService.getNextAvailableBox();
  item.value.box_id = normalizeBox(box_id);
}

async function saveItem() {
  submitted.value = true;
  boxErrorMessage.value = '';
  item.value.box_id = normalizeBox(item.value.box_id);

  if (!isValidBox(item.value.box_id)) {
    const b = item.value.box_id;
    if (isDisabled(b)) {
      boxErrorMessage.value = `Box ${b} is disabled, Please enter another valid box number.`;
    } else if (scannerSlots.has(b)) {
      boxErrorMessage.value = `Box ${b} is reserved for the scanner slot.`;
    } else {
      boxErrorMessage.value = 'Box number must be 1–30 and cannot be disabled.';
    }
    return;
  }

  try {
    if (newItem.value) {
      await ItemService.createPrint(item.value);
    } else {
      await ItemService.updatePrint(item.value);
    }

    itemDialog.value = false;
    item.value = {};
    await refreshAll();

    toast.add({
      severity: 'success',
      summary: 'Successful',
      detail: newItem.value ? 'Item Created' : 'Item Updated',
      life: 2500
    });
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Save Failed',
      detail: e?.response?.data?.message || 'Error saving',
      life: 4000
    });
  }
}

function editItem(selectedItem) {
  const b = Number(selectedItem.box_id);
  if (isDisabled(b)) {
    toast.add({ severity: 'error', summary: 'Box Disabled', detail: `Box ${b} is disabled.`, life: 3000 });
    return;
  }

  item.value = { ...selectedItem };
  newItem.value = false;
  itemDialog.value = true;
  item.value.box_id = normalizeBox(item.value.box_id);
}

async function unlockPrint(selectedItem) {
  if (!selectedItem) return;
  await ItemService.unlockPrint(selectedItem.id);
  toast.add({ severity: 'success', summary: 'Successful', detail: 'Box opened', life: 2500 });
  await refreshAll();
}

async function deletePrint(selectedItem) {
  if (!selectedItem) return;
  await ItemService.deletePrint(selectedItem.id);
  toast.add({
    severity: 'success',
    summary: 'Deleted',
    detail: `Print removed from Box ${selectedItem.box_id}`,
    life: 2500
  });
  await refreshAll();
}

// Disabled manager
const newDisabledBoxId = ref(1);
const newDisabledReason = ref('');

async function addDisabled() {
  const b = Number(newDisabledBoxId.value);

  if (!Number.isInteger(b) || b < 1 || b > 30) {
    toast.add({ severity: 'error', summary: 'Invalid', detail: 'Box must be 1–30', life: 2500 });
    return;
  }

  if (scannerSlots.has(b)) {
    toast.add({ severity: 'error', summary: 'Invalid', detail: `Box ${b} is reserved for scanner.`, life: 2500 });
    return;
  }

  await ItemService.addDisabledBox(b, newDisabledReason.value || '');
  newDisabledReason.value = '';
  await refreshAll();
  toast.add({ severity: 'success', summary: 'Disabled', detail: `Box ${b} disabled`, life: 2500 });
}

async function removeDisabled(box_id) {
  await ItemService.removeDisabledBox(box_id);
  await refreshAll();
  toast.add({ severity: 'success', summary: 'Enabled', detail: `Box ${box_id} enabled`, life: 2500 });
}
</script>

<style scoped>
.layout-page {
  min-height: calc(100vh - 110px);
  display: flex;
  flex-direction: column;
}

.layout-grid {
  width: 100%;
  flex: 1;
  display: grid;
  grid-template-columns: repeat(8, minmax(0, 1fr));
  grid-template-rows: repeat(4, 1fr);
  gap: 10px;
  padding: 10px;
}

.cell {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
}

.cell.scanner {
  background: #0b0b0b;
  border-color: #0b0b0b;
  color: #fff;
  align-items: center;
  justify-content: center;
}

.scanner-label {
  font-weight: 900;
  letter-spacing: 0.5px;
}

.cell.empty {
  background: #f3f4f6;
}

.cell.occupied {
  background: #e0f2fe;
  border-color: #bae6fd;
}

.cell.picked {
  background: #dcfce7;
  border-color: #bbf7d0;
}

.cell.awaiting {
  background: #fef3c7;
  border-color: #fde68a;
}

.cell.disabled {
  background: #fee2e2;
  border-color: #fecaca;
}

.cell-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.box-title {
  font-weight: 800;
  font-size: 0.95rem;
  white-space: nowrap;
}

.status-pill {
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 999px;
  white-space: nowrap;
  border: 1px solid transparent;
}

.pill-empty {
  background: #fff;
  color: #374151;
  border-color: #e5e7eb;
}

.pill-occupied {
  background: #fff;
  color: #075985;
  border-color: #bae6fd;
}

.pill-picked {
  background: #fff;
  color: #166534;
  border-color: #bbf7d0;
}

.pill-awaiting {
  background: #fff;
  color: #92400e;
  border-color: #fde68a;
}

.pill-disabled {
  background: #fff;
  color: #991b1b;
  border-color: #fecaca;
}

.pill-scanner {
  background: #0b0b0b;
  color: #fff;
  border-color: #0b0b0b;
}

.cell-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.meta-empty {
  color: #6b7280;
  font-weight: 600;
}

.line {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.k {
  font-weight: 700;
  color: #6b7280;
}

.v {
  font-weight: 700;
}

.actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.disabled-note {
  font-weight: 700;
  color: #991b1b;
}

.disabled-panel {
  border-top: 1px solid #e5e7eb;
  padding: 10px 12px;
  background: #fff;
}

.panel-title {
  font-weight: 900;
  margin-bottom: 8px;
}

.panel-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.add-row {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.reason {
  min-width: 260px;
}

.hint {
  font-size: 0.85rem;
  color: #6b7280;
}

.disabled-table {
  margin-top: 10px;
}
</style>
