import express from 'express';
import http from 'http';
import { fileURLToPath } from 'url';
import path from 'path';

let gameServers = {};

var app = express();
const server = http.createServer(app);

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.use(express.static(__dirname));

var defaultPort = 3000;
server.listen(process.env.PORT || defaultPort);

console.log('express server started on port http://localhost:%s', process.env.PORT || defaultPort);

server.on('error', function (e) {
  if (e.code == 'EADDRINUSE') {
    console.error('Address in use, exiting...');
  }
});
