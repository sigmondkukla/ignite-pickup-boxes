<template>
  <div class="kiosk">
    <div v-if="mode === 'idle'" class="idle-screen">
      <h1>WELCOME TO THE MAKERSPACE</h1>
      <p>Scan your QR code to open your box</p>

      <h2>BOX LOCATION MAP</h2>

      <div class="box-map">
        <div
          v-for="slot in BOX_LAYOUT"
          :key="slot.label"
          class="box"
          :class="{
            scanner: slot.type === 'scanner',
            highlight: highlightedBox === slot.label
          }"
        >
          <span v-if="slot.type === 'scanner'">SCANNER</span>
          <span v-else-if="highlightedBox === slot.label">YOU<br />{{ slot.label }}</span>
          <span v-else>{{ slot.label }}</span>
        </div>
      </div>
    </div>

    <div v-else class="result-screen" :class="resultType">
      <h1>{{ resultTitle }}</h1>
      <p>{{ resultMessage }}</p>
      <p class="small">Returning to home screen in {{ countdown }}s</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue"

const params = new URLSearchParams(window.location.search)
const screen = params.get("screen") || "left"

const API_BASE = "http://127.0.0.1:5000/api"

const BOX_LAYOUT = [
  { type: "box", label: 1 },
  { type: "box", label: 2 },
  { type: "box", label: 3 },
  { type: "box", label: 4 },
  { type: "box", label: 5 },
  { type: "box", label: 6 },
  { type: "box", label: 7 },
  { type: "box", label: 8 },

  { type: "box", label: 9 },
  { type: "scanner", label: "S1" },
  { type: "box", label: 10 },
  { type: "box", label: 11 },
  { type: "box", label: 12 },
  { type: "box", label: 13 },
  { type: "box", label: 14 },
  { type: "scanner", label: "S2" },

  { type: "box", label: 15 },
  { type: "box", label: 16 },
  { type: "box", label: 17 },
  { type: "box", label: 18 },
  { type: "box", label: 19 },
  { type: "box", label: 20 },
  { type: "box", label: 21 },
  { type: "box", label: 22 },

  { type: "box", label: 23 },
  { type: "box", label: 24 },
  { type: "box", label: 25 },
  { type: "box", label: 26 },
  { type: "box", label: 27 },
  { type: "box", label: 28 },
  { type: "box", label: 29 },
  { type: "box", label: 30 },
]

const mode = ref("idle")
const resultTitle = ref("")
const resultMessage = ref("")
const resultType = ref("success")
const highlightedBox = ref(null)
const countdown = ref(10)
const latestEventIdSeen = ref(0)

let pollTimer = null
let resetTimer = null
let countdownTimer = null

function resetToIdle() {
  mode.value = "idle"
  highlightedBox.value = null
  resultTitle.value = ""
  resultMessage.value = ""
  resultType.value = "success"
  countdown.value = 10

  if (resetTimer) clearTimeout(resetTimer)
  if (countdownTimer) clearInterval(countdownTimer)
}

function showResult(title, message, type, boxId = null) {
  mode.value = "result"
  resultTitle.value = title
  resultMessage.value = message
  resultType.value = type
  highlightedBox.value = boxId ? Number(boxId) : null
  countdown.value = 10

  if (resetTimer) clearTimeout(resetTimer)
  if (countdownTimer) clearInterval(countdownTimer)

  countdownTimer = setInterval(() => {
    if (countdown.value > 0) countdown.value -= 1
  }, 1000)

  resetTimer = setTimeout(resetToIdle, 10000)
}

async function pollLatestScan() {
  try {
    const response = await fetch(`${API_BASE}/kiosk/latest-scan?screen=${screen}`)
    const event = await response.json()

    const eventId = Number(event.event_id || 0)
    if (!eventId || eventId === latestEventIdSeen.value) return

    latestEventIdSeen.value = eventId

    if (event.status === "success") {
      showResult(
        event.title || "Access Granted",
        event.message || `Your Print is in BOX ${event.box_id}`,
        "success",
        event.box_id
      )
    } else if (event.status === "error") {
      showResult(
        event.title || "Invalid Code",
        event.message || "Ask a Maker Mentor for help.",
        "error"
      )
    }
  } catch (err) {
    console.error("Kiosk API error:", err)
  }
}

onMounted(() => {
  pollLatestScan()
  pollTimer = setInterval(pollLatestScan, 1000)
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (resetTimer) clearTimeout(resetTimer)
  if (countdownTimer) clearInterval(countdownTimer)
})
</script>

<style scoped>
.kiosk {
  width: 100vw;
  height: 100vh;
  background: #f7f7f7;
  color: #0b1736;
  font-family: Arial, sans-serif;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 14px;
  box-sizing: border-box;
  cursor: none;
}

.idle-screen {
  width: 100%;
  max-width: 780px;
  text-align: center;
}

h1 {
  margin: 0;
  font-size: 36px;
  font-weight: 800;
}

p {
  font-size: 20px;
  font-weight: 700;
  color: #d4af37;
}

h2 {
  margin: 18px 0 12px;
  font-size: 24px;
}

.box-map {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 8px;
}

.box {
  height: 64px;
  background: #8fd19e;
  border: 2px solid #d4af37;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 800;
}

.scanner {
  background: #70798c;
  color: white;
  font-size: 12px;
}

.highlight {
  background: #d4af37;
  border: 3px solid black;
  animation: pulse 1s infinite;
}

.result-screen {
  width: 90%;
  max-width: 760px;
  margin-top: 60px;
  padding: 40px;
  border-radius: 20px;
  text-align: center;
  color: white;
}

.result-screen.success {
  background: #166534;
}

.result-screen.error {
  background: #8b1e1e;
}

.result-screen h1 {
  color: white;
  font-size: 48px;
}

.result-screen p {
  color: white;
  font-size: 28px;
}

.small {
  font-size: 16px !important;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.06); }
  100% { transform: scale(1); }
}
</style>
