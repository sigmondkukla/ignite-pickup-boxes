import axios from 'axios';

const getPrints = async () => {
  const response = await axios.get('/prints');
  return response.data;
};

const deletePrint = async (id) => {
  const response = await axios.delete('/prints', { data: { id } });
  return response.data;
};

const deletePrints = async (ids) => {
  const response = await axios.delete('/prints', { data: { ids } });
  return response.data;
};

const updatePrint = async (print) => {
  const response = await axios.put('/prints', print);
  return response.data;
};

const createPrint = async (print) => {
  const response = await axios.post('/prints', print);
  return response.data;
};

const unlockPrint = async (id) => {
  const response = await axios.post('/prints/unlock', { id });
  return response.data;
};

const getNextAvailableBox = async () => {
  const response = await axios.get('/get_next_available_box');
  return response.data;
};

// Disabled boxes
const getDisabledBoxes = async () => {
  const response = await axios.get('/disabled_boxes');
  return response.data;
};

const addDisabledBox = async (box_id, reason = '') => {
  const response = await axios.post('/disabled_boxes', { box_id, reason });
  return response.data;
};

const removeDisabledBox = async (box_id) => {
  const response = await axios.delete(`/disabled_boxes/${box_id}`);
  return response.data;
};

export default {
  // Print CRUD
  getPrints,
  deletePrint,
  deletePrints,
  updatePrint,
  createPrint,

  // Print unlock
  unlockPrint,

  // Boxes
  getNextAvailableBox,

  // Disabled boxes
  getDisabledBoxes,
  addDisabledBox,
  removeDisabledBox
};
