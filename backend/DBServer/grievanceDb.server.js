// const express = require('express');
// const { Pool } = require('pg');
// const fs = require('fs');
// const csv = require('csv-parser');
// const multer = require('multer');
// require('dotenv').config();

// const app = express();
// const port = process.env.PORT || 3000;

// // PostgreSQL Database Connection
// const pool = new Pool({
//     user: 'postgres.wycnpqyoatffuvlhrwcz',
//     host: 'aws-0-ap-south-1.pooler.supabase.com',
//     database: 'postgres',
//     password: 'kunalpro379',
//     port: 6543,
// });

// app.use(express.json({ limit: '50mb' }));
// app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// // Multer setup for file upload
// const upload = multer({ dest: 'uploads/' });

// // Test DB Connection
// app.get('/ping', async (req, res) => {
//     try {
//         const client = await pool.connect();
//         await client.query('SELECT NOW()');
//         client.release();
//         res.send('Database connected successfully!');
//     } catch (err) {
//         res.status(500).send('Database connection failed');
//     }
// });

// // Upload CSV File and Insert Data into PostgreSQL
// app.post('/upload-csv', upload.single('file'), async (req, res) => {
//     if (!req.file) {
//         return res.status(400).send('No file uploaded.');
//     }

//     const results = [];
//     fs.createReadStream(req.file.path)
//         .pipe(csv())
//         .on('data', (data) => results.push(data))
//         .on('end', async () => {
//             try {
//                 const client = await pool.connect();
//                 for (const row of results) {
//                     await client.query(
//                         `INSERT INTO grievances (gpscoordinates_longitude, email, complaint_type, location, CreatedAt, title, citizenName, category, economicImpact, environmentalImpact, emotion, lastUpdatedDate, ResolutionTime, tehsil, complaintType, socialImpact, pincode, status, district, date, submissionDate, complaint, contactNumber, updatedAt, relatedPolicies, subcategory, urgencyLevel, ward, gpscoordinates_latitude, isAnonymous, estimated, departmentAssigned) 
//                         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29, $30, $31, $32)`,
//                         [row.gpscoordinates_longitude, row.email, row.complaint_type, row.location, row.CreatedAt, row.title, row.citizenName, row.category, row.economicImpact, row.environmentalImpact, row.emotion, row.lastUpdatedDate, row.ResolutionTime, row.tehsil, row.complaintType, row.socialImpact, row.pincode, row.status, row.district, row.date, row.submissionDate, row.complaint, row.contactNumber, row.updatedAt, row.relatedPolicies, row.subcategory, row.urgencyLevel, row.ward, row.gpscoordinates_latitude, row.isAnonymous, row.estimated, row.departmentAssigned]
//                     );
//                 }
//                 client.release();
//                 res.send('CSV data inserted successfully!');
//             } catch (err) {
//                 res.status(500).send(`Error inserting data: ${err.message}`);
//             }
//         });
// });

// // Start Server
// app.listen(port, () => {
//     console.log(`Server running on port ${port}`);
// });

const { PrismaClient } = require('@prisma/client');
const csv = require('csv-parser');
const fs = require('fs');
const path = require('path');

const prisma = new PrismaClient();

async function seedDatabase() {
  try {
    console.log('Starting database seeding...');

    // Create or update initial authority using upsert
    const authority = await prisma.authority.upsert({
      where: { email: "admin@authority.com" },
      update: {
        name: "Admin Authority",
        roleId: "ADMIN",
        assignedRegion: "Uttar Pradesh"
      },
      create: {
        name: "Admin Authority",
        email: "admin@authority.com",
        roleId: "ADMIN",
        assignedRegion: "Uttar Pradesh"
      }
    });

    // Create a map to store unique departments from CSV
    const uniqueDepartments = new Set();
    const departmentIdMap = new Map();
    let deptCounter = 1;

    // First pass: collect all unique department names
    const results = [];
    await new Promise((resolve, reject) => {
      fs.createReadStream(path.join(__dirname, './data/combined_data.csv'))
        .pipe(csv())
        .on('data', (data) => {
          results.push(data);
          if (data.departmentAssigned) {
            uniqueDepartments.add(data.departmentAssigned);
          }
        })
        .on('end', resolve)
        .on('error', reject);
    });

    // Create departments with sequential IDs
    for (const deptName of uniqueDepartments) {
      const deptId = `DEPT_${String(deptCounter).padStart(3, '0')}`;
      try {
        const department = await prisma.department.upsert({
          where: { departmentId: deptId },
          update: { departmentName: deptName },
          create: {
            departmentId: deptId,
            departmentName: deptName,
            description: `Department of ${deptName}`,
            departmentOfficers: {},
            workers: {},
            authorityId: authority.id
          }
        });
        departmentIdMap.set(deptName, department.departmentId);
        console.log(`Created/Updated department: ${deptName} with ID: ${deptId}`);
        deptCounter++;
      } catch (err) {
        console.error(`Error creating department ${deptName}:`, err);
      }
    }

    // Process grievances
    for (const row of results) {
      try {
        // Create or connect user
        const user = await prisma.user.upsert({
          where: { email: row.email },
          update: {},
          create: {
            email: row.email,
            name: row.citizenName,
            password: 'defaultpassword' // In production, use proper password hashing
          }
        });

        // Create or connect location
        const location = await prisma.location.create({
          data: {
            location: row.location,
            gpsCoordinatesLongitude: parseFloat(row.gpscoordinates_longitude),
            gpsCoordinatesLatitude: parseFloat(row.gpscoordinates_latitude),
            pincode: row.pincode,
            district: row.district,
            tehsil: row.tehsil,
            ward: row.ward
          }
        });

        // Map urgencyLevel to match the enum values
        const mapUrgencyLevel = (level) => {
          switch(level?.toUpperCase()) {
            case 'HIGH':
              return 'HIGH';
            case 'MEDIUM':
              return 'MEDIUM';
            case 'LOW':
              return 'LOW';
            case 'CRITICAL':
              return 'CRITICAL';
            default:
              return 'MEDIUM';
          }
        };

        // Get department ID from map
        const deptId = departmentIdMap.get(row.departmentAssigned) || departmentIdMap.get("Municipal Corporation");

        // Create grievance with department ID
        const grievance = await prisma.grievance.create({
          data: {
            userId: user.id,
            emailId: row.email,
            locationId: location.id,
            isAnonymous: row.isAnonymous === 'True',
            complaintType: row.complaintType,
            title: row.title,
            categorySubcategory: row.category + '/' + row.subcategory,
            economicImpact: row.economicImpact,
            envImpact: row.environmentalImpact,
            emotion: row.emotion,
            socialImpact: row.socialImpact,
            status: row.status === 'Open' ? 'PENDING' : 
                   row.status === 'In Progress' ? 'IN_PROGRESS' :
                   row.status === 'Closed' ? 'RESOLVED' : 'PENDING',
            urgencyLevel: mapUrgencyLevel(row.urgencyLevel),
            priorityLevel: 'MEDIUM',
            timestamp: new Date(row.CreatedAt),
            departmentAssigned: deptId
          }
        });

        console.log(`Processed grievance for ${row.citizenName} with department ${deptId}`);
      } catch (err) {
        console.error(`Error processing row:`, err);
        console.error(`Department assigned: ${row.departmentAssigned}`);
        continue; // Continue with next row even if current fails
      }
    }

    console.log('Database seeding completed successfully!');

  } catch (error) {
    console.error('Error seeding database:', error);
    throw error;
  } finally {
    await prisma.$disconnect();
  }
}

// Install required package first:
// npm install csv-parser

seedDatabase()
  .then(() => {
    console.log('Seeding complete!');
  })
  .catch((error) => {
    console.error('Error in seeding:', error);
    process.exit(1);
  });
