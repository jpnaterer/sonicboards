// Referencing Mongoose
const mongoose = require('mongoose')

// Define the Schema
const ReviewsSchema = new mongoose.Schema({
    artist: String,
    title: String,
    genre: String,
    rating: Number,
    url: String,
    source: String,
    sp_date: Date,
    sp_album_id: String,
    sp_img: String,
    sp_artist_id: String,
    sp_popularity: Number,
    score: Number
})

// Define the Model
const Reviews = mongoose.model('Reviews', ReviewsSchema, 'reviews')

//Export the Model
module.exports = Reviews
