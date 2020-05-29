const express = require('express')          // requires install
const bodyParser = require('body-parser')   // requires install
const https = require('https')              // requires install
const fs = require('fs');
const app = express()                       // requires install

// pm2 start server.js    pm2 list    pm2 info server
// configuration required for https connection. switch to true
prod_flag = false;

// Connect to mongodb and create data models for querying
const mongoose = require('mongoose')
mongoose.connect('mongodb://localhost:27017/sonicboards',
    {useNewUrlParser: true, useUnifiedTopology: true})
const Canada = require('./models/canada')
const Reviews = require('./models/reviews')
const Config = require('./models/config')

// Adjust response by adding CORS headers.
app.use(bodyParser.json())
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*')
    res.header('Access-Control-Allow-Headers', '*')
    next();
})

app.post('/api/reviews', async (req, res) => {
    // Ensure that the post request is an array.
    if(!Array.isArray(req.body)){ req.body = [req.body] }
    releases = []
    for (var i = 0; i < req.body.length; i++) {
        releases.push(await Reviews.find({source: req.body[i].source})
            .sort({'score': -1}).limit(20))
    }

    // Ensure that the response is an array of arrays.
    if(!Array.isArray(releases[0])){ releases = [releases] }
    releases.map( r => { r.map(obj => {
            if (obj.genre === null) return obj
            obj.genre = obj.genre.toLowerCase();
            obj.genre = obj.genre.replace("rap", "hiphop");
            obj.genre = obj.genre.replace("pop/r&b", "pop");
            obj.genre = obj.genre.replace("pop/rock", "pop");
            obj.genre = obj.genre.replace("folk/country", "folk");
            return obj;
        })
    })
    res.send(releases)
})

app.post('/api/canada', async (req, res) => {
    // Ensure that the post request is an array.
    if(!Array.isArray(req.body)){ req.body = [req.body] }

    releases = []
    for (var i = 0; i < req.body.length; i++) {
        // Search with genres if the field received ~ A custom search.
        if(req.body[i].genres){
            var s = req.body[i].start_date;
            var e = req.body[i].end_date;
            var start_date = new Date(`${s.year}-${s.month}-${s.day}`);
            var end_date = new Date(`${e.year}-${e.month}-${e.day}`);
            releases.push(await Canada.find(
                {region: {$in: req.body[i].regions}, 
                    genre: {$in: req.body[i].genres},
                    sp_date: {$gte: start_date, $lte: end_date}})
                .sort({'score': -1}).limit(20))
        }else{
            releases.push(await Canada.find(
                {region: { $in: req.body[i].regions }})
                .sort({'score': -1}).limit(20))
        }
    }

    // Ensure that the response is an array of arrays.
    if(!Array.isArray(releases[0])){ releases = [releases] }
    releases.map( r => { r.map(obj => {
            if (obj['genre'] === null) return obj
            obj['genre'] = obj['genre'].toLowerCase();
            obj['genre'] = obj['genre'].replace("hip-hop/rap", "hiphop");
            obj['genre'] = obj['genre'].replace("r&b/soul", "rbsoul");
            return obj;
        }) 
    })
    res.send(releases)
})

// Get the recent update date for webpage "Updated on" timestamp.
app.post('/api/config', async (req, res) => {
    const c = await Config.findOne({})
    res.send(c.date)
})

// Get SSL keys if running in production mode.
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
