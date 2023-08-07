const express = require('express');
const path = require('path');
var cors = require('cors')

const app = express();
const port = process.env.PORT || 443;

// sendFile will go here
app.use(express.static(path.join(__dirname, 'public')));
app.use(cors())
app.get("/styles",  express.static(__dirname + '/public/stylesheets'));
app.get("/scripts", express.static(__dirname + '/public/js'));
app.get("/images",  express.static(__dirname + '/public/images'));

app.get('/', function (req, res) {
    res.sendFile(__dirname + '/public/index.html');
});

app.get('/sp', function (req, res) {
    res.sendFile(__dirname + '/public/index-sp.html');
});

app.get('/ru', function (req, res) {
    res.sendFile(__dirname + '/public/index-ru.html');
});

app.listen(port);
console.log('Server started listening at port:' + port); 