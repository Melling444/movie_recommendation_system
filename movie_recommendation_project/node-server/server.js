const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;
const BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://python:5000';

app.use(express.static('public'));
app.use(express.json());

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/index.html');
});

app.post('/recommend', async (req, res) => {
    const input = req.body.input || '';

    try {
        const response = await axios.post(`${BACKEND_URL}/recommend`, {
            input: input
        });

        res.json(response.data);

    } catch (error) {
        console.error('Error calling Python service:', error.message);
        res.status(500).send('Failed to get recommendations');
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
