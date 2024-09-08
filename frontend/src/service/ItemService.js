export const ItemService = {
    getItemsData() {
        return [
            {
                id: '0',
                code: '123456',
                email: '***REMOVED***',
                box_id: '0',
                print_number: '255',
            },
            {
                id: '1',
                code: '123456',
                email: '***REMOVED***',
                box_id: '1',
                print_number: '256',
            },
            {
                id: '1',
                code: '123456',
                email: '***REMOVED***',
                box_id: '2',
                print_number: '257',
            },
        ];
    },

    getItems() {
        return Promise.resolve(this.getItemsData());
    },
};
