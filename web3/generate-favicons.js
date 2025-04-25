// Simple script to create favicon files
// This is a placeholder - in a real scenario, you would use sharp or another
// image processing library to generate proper favicons

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get current file's directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create the webmanifest file
const webmanifest = {
  "name": "Asireon AI",
  "short_name": "Asireon AI",
  "icons": [
    {
      "src": "/favicon-96x96.png",
      "sizes": "96x96",
      "type": "image/png"
    },
    {
      "src": "/favicon-64x64.png",
      "sizes": "64x64",
      "type": "image/png"
    },
    {
      "src": "/favicon-48x48.png",
      "sizes": "48x48",
      "type": "image/png"
    },
    {
      "src": "/android-chrome-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/android-chrome-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "theme_color": "#ffffff",
  "background_color": "#ffffff",
  "display": "standalone"
};

// Write webmanifest file
fs.writeFileSync(
  path.join(__dirname, 'public', 'site.webmanifest'),
  JSON.stringify(webmanifest, null, 2)
);

// For development purposes, let's copy the favicon.png to all required sizes
const sizes = [
  { name: 'favicon-16x16.png', size: '16x16' },
  { name: 'favicon-32x32.png', size: '32x32' },
  { name: 'favicon-48x48.png', size: '48x48' },
  { name: 'favicon-64x64.png', size: '64x64' },
  { name: 'favicon-96x96.png', size: '96x96' },
  { name: 'apple-touch-icon.png', size: '180x180' },
  { name: 'android-chrome-192x192.png', size: '192x192' },
  { name: 'android-chrome-512x512.png', size: '512x512' }
];

// Simple copy of the original favicon for development
sizes.forEach(size => {
  fs.copyFileSync(
    path.join(__dirname, 'public', 'favicon.png'),
    path.join(__dirname, 'public', size.name)
  );
  console.log(`Created ${size.name} (${size.size})`);
});

console.log('Created site.webmanifest');
console.log('In a production environment, you should resize these images properly.'); 