const express = require('express')          // requires install
const bodyParser = require('body-parser')   // requires install
const https = require('https')              // requires install
const fs = require('fs');
const app = express()                       // requires install

// pm2 start server.js    pm2 list    pm2 info server
// configuration required for https connection
prod_flag = false;

// Connect to mongodb and create data models for querying
const mongoose = require('mongoose')
mongoose.connect('mongodb://localhost:27017/sonicboards',
    {useNewUrlParser: true, useUnifiedTopology: true})
const Canada = require('./models/canada')
const Reviews = require('./models/reviews')

// Adjust response by adding CORS headers.
app.use(bodyParser.json())
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*')
    res.header('Access-Control-Allow-Headers', '*')
    next();
})

app.post('/api/reviews', async (req, res) => {
    const releases = await Reviews.find({source: req.body.source})
        .sort({'score': -1}).limit(20)
    releases.map(obj => {
        if (obj.genre === null) return obj
        obj.genre = obj.genre.toLowerCase();
        obj.genre = obj.genre.replace("rap", "hiphop");
        obj.genre = obj.genre.replace("pop/r&b", "pop");
        obj.genre = obj.genre.replace("pop/rock", "pop");
        obj.genre = obj.genre.replace("folk/country", "folk");
        return obj;
    })
    res.send(releases)
})

app.post('/api/canada', async (req, res) => {
    // Search with genres if the field received.
    if(req.body.genres){
        releases = await Canada.find(
            {region: {$in: req.body.regions}, genre: {$in: req.body.genres}})
            .sort({'score': -1}).limit(20)
    }else{
        releases = await Canada.find(
            {region: { $in: req.body.regions }}).sort({'score': -1}).limit(20)
    }
    releases.map(obj => {
        if (obj.genre === null) return obj
        obj.genre = obj.genre.toLowerCase();
        obj.genre = obj.genre.replace("hip-hop/rap", "hiphop");
        obj.genre = obj.genre.replace("r&b/soul", "rbsoul");
        return obj;
    })
    res.send(releases)
})

if (prod_flag){
    const options = {
        key: fs.readFileSync('/etc/letsencrypt/live/sonicboards.com/privkey.pem'),
        cert: fs.readFileSync('/etc/letsencrypt/live/sonicboards.com/cert.pem')
    };
    server = https.createServer(options, app);
    server.listen(3000, () => console.log('Server listening at 3000'));
}else{
    app.listen(3000, () => console.log('Server listening at 3000'));
}
