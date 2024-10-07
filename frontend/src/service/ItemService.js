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

const ItemService = {
    getPrints,
    deletePrint,
    updatePrint,
    createPrint
};

export default ItemService;