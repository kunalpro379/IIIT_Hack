const express = require('express');
const { Pool } = require('pg');
const fs = require('fs');
const csv = require('csv-parser');
const multer = require('multer');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// PostgreSQL Database Connection
const pool = new Pool({
    user: 'postgres.wycnpqyoatffuvlhrwcz',
    host: 'aws-0-ap-south-1.pooler.supabase.com',
    database: 'postgres',
    password: 'kunalpro379',
    port: 6543,
});

app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Multer setup for file upload
const upload = multer({ dest: 'uploads/' });

// Test DB Connection
app.get('/ping', async (req, res) => {
    try {
        const client = await pool.connect();
        await client.query('SELECT NOW()');
        client.release();
        res.send('Database connected successfully!');
    } catch (err) {
        res.status(500).send('Database connection failed');
    }
});

// Upload CSV File and Insert Data into PostgreSQL
app.post('/upload-csv', upload.single('file'), async (req, res) => {
    if (!req.file) {
        return res.status(400).send('No file uploaded.');
    }

    const results = [];
    fs.createReadStream(req.file.path)
        .pipe(csv())
        .on('data', (data) => results.push(data))
        .on('end', async () => {
            try {
                const client = await pool.connect();
                for (const row of results) {
                    await client.query(
                        `INSERT INTO grievances (gpscoordinates_longitude, email, complaint_type, location, CreatedAt, title, citizenName, category, economicImpact, environmentalImpact, emotion, lastUpdatedDate, ResolutionTime, tehsil, complaintType, socialImpact, pincode, status, district, date, submissionDate, complaint, contactNumber, updatedAt, relatedPolicies, subcategory, urgencyLevel, ward, gpscoordinates_latitude, isAnonymous, estimated, departmentAssigned) 
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29, $30, $31, $32)`,
                        [row.gpscoordinates_longitude, row.email, row.complaint_type, row.location, row.CreatedAt, row.title, row.citizenName, row.category, row.economicImpact, row.environmentalImpact, row.emotion, row.lastUpdatedDate, row.ResolutionTime, row.tehsil, row.complaintType, row.socialImpact, row.pincode, row.status, row.district, row.date, row.submissionDate, row.complaint, row.contactNumber, row.updatedAt, row.relatedPolicies, row.subcategory, row.urgencyLevel, row.ward, row.gpscoordinates_latitude, row.isAnonymous, row.estimated, row.departmentAssigned]
                    );
                }
                client.release();
                res.send('CSV data inserted successfully!');
            } catch (err) {
                res.status(500).send(`Error inserting data: ${err.message}`);
            }
        });
});

// Start Server
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
