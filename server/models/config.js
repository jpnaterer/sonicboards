// Referencing Mongoose
const mongoose = require('mongoose')

// Define the Schema
const ConfigSchema = new mongoose.Schema({
    date: Date
})

// Define the Model
const Config = mongoose.model('Config', ConfigSchema, 'config')

//Export the Model
module.exports = Config
