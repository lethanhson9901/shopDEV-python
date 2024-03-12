// src/services/apikey.service.js

'use strict'

const {item, clothing, electronic} = require('../models/item.model')

// define Factory class to create item
class ItemFactory {
    /**
     * Type: 'Clothing'
     * payload
     */
    static async createItem(){
        switch (type) {
            case 'Electronics':
                return new Electronics(payload).createItem()
            case 'Clothing':
                return new Clothing(payload).createItem()
            default:
                throw new BadRequestError('Invalid Product Types ${type}')


        }
    }
}

// define base item class
class Item {
    constructor({
        id, name,
        thumbnail,
        description,
        price,
        stock_quantity,
        category,
        user,
        tags,
        state,
        attributes,
    }){
        this.id = id,
        this.name = name,
        // ...
    }

    async createItem(id){
        return await item.create({...this, _id:id})
    }
}

// Define sub-class for diffrent item types: Clothing
class Clothing extends Item {
    async createItem() {
        const newClothing = await clothing.create(this.attributes)
        if (!newClothing) throw new BadRequestError('Create new Clothing Error')
        const newItem = await super.createItem()
        if(!newItem) throw new BadRequestError('Create new Item Error')
        return newItem;
    }
}

// Define sub-class for diffrent item types: Electronics
class Electronics extends Item {
    async createItem() {
        const newElectronics = await electronic.create({...this.attributes, shop_owner: this.user})
        if (!newElectronics) throw new BadRequestError('Create new Electronics Error')
        const newItem = await super.createItem(newElectronics._id)
        if(!newItem) throw new BadRequestError('Create new Item Error')
        return newItem;
    }
}