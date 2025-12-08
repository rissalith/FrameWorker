#!/usr/bin/env node
/**
 * MaxGamer Frontend Static Server
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = 3000;
const HOST = '127.0.0.1';

// MIME types mapping
const mimeTypes = {
    '.html': 'text/html',
    '.js': 'application/javascript',
    '.mjs': 'application/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav'
};

const server = http.createServer((req, res) => {
    console.log(`${req.method} ${req.url}`);

    // Parse URL
    let filePath = '.' + decodeURIComponent(req.url.split('?')[0]);
    if (filePath === './') {
        filePath = './index.html';
    }

    // Resolve absolute path
    const absolutePath = path.join(__dirname, filePath);

    // Get file extension
    const extname = String(path.extname(filePath)).toLowerCase();
    const contentType = mimeTypes[extname] || 'application/octet-stream';

    // Read and serve file
    fs.readFile(absolutePath, (error, content) => {
        if (error) {
            if (error.code === 'ENOENT') {
                // Try index.html for SPA routing
                if (!extname) {
                    fs.readFile(path.join(__dirname, 'index.html'), (err, indexContent) => {
                        if (err) {
                            res.writeHead(404, { 'Content-Type': 'text/html' });
                            res.end('<h1>404 - File Not Found</h1>', 'utf-8');
                        } else {
                            res.writeHead(200, {
                                'Content-Type': 'text/html',
                                'Access-Control-Allow-Origin': '*'
                            });
                            res.end(indexContent, 'utf-8');
                        }
                    });
                } else {
                    res.writeHead(404, { 'Content-Type': 'text/html' });
                    res.end('<h1>404 - File Not Found</h1>', 'utf-8');
                }
            } else {
                res.writeHead(500);
                res.end(`Server Error: ${error.code}`, 'utf-8');
            }
        } else {
            // Success
            res.writeHead(200, {
                'Content-Type': contentType,
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Cache-Control': 'no-store, no-cache, must-revalidate'
            });
            res.end(content, 'utf-8');
        }
    });
});

server.listen(PORT, HOST, () => {
    const url = `http://${HOST}:${PORT}`;
    console.log('\n============================================================');
    console.log('MaxGamer 前端服务器已启动');
    console.log('============================================================');
    console.log(`服务地址: ${url}`);
    console.log(`服务目录: ${__dirname}`);
    console.log('============================================================');
});

server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
        console.error(`\n❌ 端口 ${PORT} 已被占用`);
    } else {
        console.error('\n❌ 服务器错误:', err.message);
    }
    process.exit(1);
});
