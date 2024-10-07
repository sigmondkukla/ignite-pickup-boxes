import axios from 'axios';

const getPrints = async () => {
    try {
        const response = await axios.get('/prints');
        return response.data;
    } catch (error) {
        console.error('Error fetching prints:', error);
        throw error;
    }
};

const deletePrint = async (id) => {
    try {
        const response = await axios.delete(`/prints`, { data: { id } });
        return response.data;
    } catch (error) {
        console.error('Error deleting print:', error);
        throw error;
    }
};

const updatePrint = async (print) => {
    try {
        const response = await axios.put(`/prints`, print);
        return response.data;
    } catch (error) {
        console.error('Error updating print:', error);
        throw error;
    }
};

const createPrint = async (print) => {
    try {
        const response = await axios.post(`/prints`, print);
        return response.data;
    } catch (error) {
        console.error('Error creating print:', error);
        throw error;
    }
}

const getNextAvailableBox = async () => {
    try {
        const response = await axios.get('/get_next_available_box');
        console.log('getNextAvailableBox data:', response.data);
        return response.data;
    } catch (error) {
        console.error('Error fetching next available box:', error);
        throw error;
    }
}

const deletePrints = async (ids) => {
    try {
        const response = await axios.delete(`/prints`, { data: { ids } });
        return response.data;
    } catch (error) {
        console.error('Error deleting prints:', error);
        throw error;
    }
};

const unlockPrint = async (id) => {
    try {
        const response = await axios.post(`/prints/unlock`, { id });
        return response.data;
    } catch (error) {
        console.error('Error unlocking print:', error);
        throw error;
    }
}

const ItemService = {
    // Print CRUD
    getPrints,
    deletePrint,
    deletePrints,
    updatePrint,
    createPrint,

    // Print unlock
    unlockPrint,
    
    // Boxes
    getNextAvailableBox
};

export default ItemService;