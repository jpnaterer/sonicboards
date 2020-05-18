// Referencing Mongoose
const mongoose = require('mongoose')

// Define the Schema
const CanadaSchema = new mongoose.Schema({
    artist: String,
    title: String,
    genre: String,
    region: String,
    url: String,
    sp_date: String,
    sp_album_id: String,
    sp_img: String,
    sp_artist_id: String,
    sp_popularity: Number,
    score: Number
})

// Define the Model
const Canada = mongoose.model('Canada', CanadaSchema, 'canada')

//Export the Model
module.exports = Canada
