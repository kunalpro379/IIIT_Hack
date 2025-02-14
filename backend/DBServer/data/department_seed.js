const { PrismaClient } = require('@prisma/client');
const csv = require('csv-parser');
const fs = require('fs');
const path = require('path');

const prisma = new PrismaClient();

async function seedDatabase() {
  try {
    console.log('Starting database seeding...');

    const existingAuthorities = await prisma.authority.findMany({
      where: { role: 'DEPARTMENT_HEAD' }
    });
    console.log('Found existing authorities:', existingAuthorities.map(a => a.name));

    // Create a map to store unique departments from CSV
    const uniqueDepartments = new Set();
    const departmentIdMap = new Map();

    // First pass: collect unique departments
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

    // For each department, find matching authority and create department
    for (const deptName of uniqueDepartments) {
      try {
        const authorityName = `${deptName} Department Head`;
        
        // Find matching authority
        const matchingAuthority = existingAuthorities.find(auth => 
          auth.name.toLowerCase() === authorityName.toLowerCase()
        );

        if (!matchingAuthority) {
          console.warn(`No matching authority found for ${deptName} - skipping`);
          continue;
        }

        // Create department with existing authority
        const department = await prisma.department.create({
          data: {
            departmentName: deptName,
            description: `Department of ${deptName}`,
            authorityId: matchingAuthority.id
          }
        });

        departmentIdMap.set(deptName, department.id);
        console.log(`Created department "${deptName}" with existing authority: ${matchingAuthority.name}`);
      } catch (err) {
        console.error(`Error creating department ${deptName}:`, err);
        continue;
      }
    }

    console.log('Department map:', Object.fromEntries(departmentIdMap));

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

        // Get department ID and verify it exists
        const deptId = departmentIdMap.get(row.departmentAssigned);
        if (!deptId) {
          console.warn(`No department found for "${row.departmentAssigned}" - skipping grievance`);
          continue;
        }

        // Verify department exists in database
        const departmentExists = await prisma.department.findUnique({
          where: { id: deptId }
        });

        if (!departmentExists) {
          console.error(`Department with ID ${deptId} not found in database`);
          continue;
        }

        // Create grievance with verified department ID
        const grievance = await prisma.grievance.create({
          data: {
            user: {
              connect: { id: user.id }
            },
            location: {
              connect: { id: location.id }
            },
            department: {
              connect: { id: deptId }
            },
            emailId: row.email,
            isAnonymous: row.isAnonymous === 'True',
            complaintType: row.complaintType || 'Not Specified',
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
            timestamp: new Date(row.CreatedAt)
          }
        });

        console.log(`Successfully created grievance for ${row.citizenName} with department ${deptId}`);
      } catch (err) {
        console.error(`Error processing grievance:`, err);
        console.error(`Department: "${row.departmentAssigned}", ID: ${departmentIdMap.get(row.departmentAssigned)}`);
        continue;
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



seedDatabase()
  .then(() => {
    console.log('Seeding complete!');
  })
  .catch((error) => {
    console.error('Error in seeding:', error);
    process.exit(1);
  });