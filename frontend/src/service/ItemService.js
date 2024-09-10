export const ItemService = {
    getItemsData() {
        return [
            {
                id: '0',
                code: '123456',
                email: '***REMOVED***',
                box_id: '0',
                print_number: '123',
                status: '0',
            },
            {
                id: '1',
                code: '123456',
                email: 'galkodl@clarkson.edu',
                box_id: '1',
                print_number: '456',
                status: '1',
            },
            {
                id: '2',
                code: '123456',
                email: 'comeaucs@clarkson.edu',
                box_id: '2',
                print_number: '789',
                status: '2',
            },
        ];
    },

    getItems() {
        return Promise.resolve(this.getItemsData());
    },
};
