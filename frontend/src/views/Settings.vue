<script setup>
import { ref, onMounted } from 'vue';

const sheetUrl = ref('');
const currentSheetUrl = ref('');
const message = ref('');
const error = ref('');
const loading = ref(false);

// adjust if needed
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000';

async function loadCurrentSheet() {
    try {
        const res = await fetch(`${API_BASE}/api/settings/google-sheet`);
        const data = await res.json();

        if (data.status === 'success') {
            currentSheetUrl.value = data.sheet_url || '';
            sheetUrl.value = data.sheet_url || '';
        }
    } catch (err) {
        error.value = 'Could not load current Google Sheet setting.';
    }
}

async function saveSheet() {
    message.value = '';
    error.value = '';
    loading.value = true;

    try {
        const res = await fetch(`${API_BASE}/api/settings/google-sheet`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sheet_url: sheetUrl.value
            })
        });

        const data = await res.json();

        if (!res.ok || data.status !== 'success') {
            throw new Error(data.message || 'Failed to update Google Sheet.');
        }

        currentSheetUrl.value = data.sheet_url;
        message.value = 'Google Sheet updated successfully.';
    } catch (err) {
        error.value = err.message || 'Something went wrong.';
    } finally {
        loading.value = false;
    }
}

onMounted(loadCurrentSheet);
</script>

<template>
    <div class="settings-page">
        <div class="settings-card">
            <h1>Settings</h1>
            <h2>Google Sheet Setup</h2>

            <p class="help-text">
                Paste the new semester Google Sheet link here. Make sure the sheet is shared with the system service account.
            </p>

            <label>Google Sheet Link</label>

            <input
                v-model="sheetUrl"
                type="text"
                placeholder="https://docs.google.com/spreadsheets/d/..."
            />

            <button @click="saveSheet" :disabled="loading">
                {{ loading ? 'Saving...' : 'Save Google Sheet' }}
            </button>

            <p v-if="message" class="success">{{ message }}</p>
            <p v-if="error" class="error">{{ error }}</p>

            <div v-if="currentSheetUrl" class="current-sheet">
                <strong>Current Sheet:</strong>
                <a :href="currentSheetUrl" target="_blank">
                    Open Google Sheet
                </a>
            </div>
        </div>
    </div>
</template>

<style scoped>
.settings-page {
    padding: 2rem;
}

.settings-card {
    max-width: 700px;
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

h2 {
    font-size: 1.3rem;
    margin-bottom: 1rem;
}

.help-text {
    margin-bottom: 1.5rem;
    color: #555;
}

label {
    display: block;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ccc;
    border-radius: 8px;
    margin-bottom: 1rem;
}

button {
    background: #143d73;
    color: white;
    border: none;
    padding: 0.75rem 1.25rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
}

button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.success {
    color: green;
    margin-top: 1rem;
}

.error {
    color: #b00020;
    margin-top: 1rem;
}

.current-sheet {
    margin-top: 1.5rem;
}
</style>
