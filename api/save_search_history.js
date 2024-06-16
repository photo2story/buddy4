// api/save_search_history.js

const fs = require('fs');
const path = require('path');

module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).send({ message: 'Only POST requests are allowed' });
    return;
  }

  const { stock_name } = req.body;
  if (!stock_name) {
    res.status(400).send({ message: 'Stock name is required' });
    return;
  }

  const logFilePath = path.join(__dirname, '../../search_history.log');
  const logEntry = `${new Date().toISOString()}: ${stock_name}\n`;

  fs.appendFile(logFilePath, logEntry, (err) => {
    if (err) {
      res.status(500).send({ message: 'Failed to save search history' });
      return;
    }
    res.status(200).send({ success: true });
  });
};


