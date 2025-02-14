const { execSync } = require('child_process');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);
const { PrismaClient } = require('@prisma/client');
const csv = require('csv-parser');
const fs = require('fs');
const path = require('path');

const prisma = new PrismaClient();

async function setupDatabase() {
    try {
        console.log('Setting up database...');
        
        // Run Prisma commands
        console.log('Generating Prisma Client...');
        execSync('npx prisma generate', { stdio: 'inherit' });
        
        console.log('Pushing database schema...');
        execSync('npx prisma db push', { stdio: 'inherit' });
        
        console.log('Database setup completed successfully');
    } catch (error) {
        console.error('Database setup failed:', error);
        process.exit(1);
    }
}

async function migrateDatabase() {
  try {
    console.log('Migrating database...');
    
    const { stdout, stderr } = await execAsync('npx prisma migrate dev --name init');
    console.log('stdout:', stdout);
    if (stderr) console.error('stderr:', stderr);
    
    console.log('Database migration completed successfully');
  } catch (error) {
    console.error('Migration error:', error);
    process.exit(1);
  }
}

async function createUser(row) {
    try {
        return await prisma.user.create({
            data: {
                email: row.email,
                name: row.citizenName || 'Anonymous User',
                password: 'defaultPassword123', // You should implement proper password hashing
            }
        });
    } catch (error) {
        if (error.code === 'P2002') {
            // If user already exists, fetch the user
            return await prisma.user.findUnique({
                where: { email: row.email }
            });
        }
        console.error('Error creating user:', error);
        return null;
    }
}

async function createLocation(row) {
    try {
        return await prisma.location.create({
            data: {
                gpsCoordinatesLongitude: parseFloat(row.gpscoordinates_longitude),
                gpsCoordinatesLatitude: parseFloat(row.gpscoordinates_latitude),
                location: row.location || 'Unknown Location',
                tehsil: row.tehsil,
                pincode: row.pincode,
                district: row.district,
                ward: row.ward
            }
        });
    } catch (error) {
        console.error('Error creating location:', error);
        return null;
    }
}

async function createDepartments() {
  const departments = [
    { id: 'DEPT_001', name: 'Municipal Corporation' },
    { id: 'DEPT_002', name: 'Public Works' },
    { id: 'DEPT_003', name: 'Health' },
    { id: 'DEPT_004', name: 'Education' },
    { id: 'DEPT_005', name: 'Water Supply' },
    // Add more departments as needed
  ];

  for (const dept of departments) {
    await prisma.department.upsert({
      where: { departmentId: dept.id },
      update: {},
      create: {
        departmentId: dept.id,
        departmentName: dept.name,
        description: `Department of ${dept.name}`,
        departmentOfficers: [],
        workers: [],
        authorityId: '1' // Make sure to use a valid authority ID
      }
    });
  }
}

async function createGrievance(row, userId, locationId) {
  try {
    // Default to DEPT_001 if no department is assigned
    const departmentId = row.departmentAssigned || 'DEPT_001';

    return await prisma.grievance.create({
      data: {
        userId: userId,
        emailId: row.email,
        locationId: locationId,
        isAnonymous: row.isAnonymous === 'True',
        complaintType: row.complaintType || 'General',
        title: row.title,
        categorySubcategory: `${row.category || 'General'}/${row.subcategory || 'Other'}`,
        economicImpact: row.economicImpact,
        envImpact: row.environmentalImpact,
        emotion: row.emotion,
        socialImpact: row.socialImpact,
        status: 'PENDING',
        urgencyLevel: 'MEDIUM',
        priorityLevel: 'MEDIUM',
        departmentAssigned: departmentId,
        timestamp: new Date()
      }
    });
  } catch (error) {
    console.error('Error creating grievance:', error);
    throw error;
  }
}

function mapStatus(status) {
    const statusMap = {
        'Open': 'PENDING',
        'In Progress': 'IN_PROGRESS',
        'Closed': 'RESOLVED'
    };
    return statusMap[status] || 'PENDING';
}

function mapUrgencyLevel(level) {
    const levelMap = {
        'High': 'HIGH',
        'Medium': 'MEDIUM',
        'Low': 'LOW'
    };
    return levelMap[level] || 'MEDIUM';
}

function mapPriorityLevel(urgency) {
    const priorityMap = {
        'High': 'HIGH',
        'Medium': 'MEDIUM',
        'Low': 'LOW'
    };
    return priorityMap[urgency] || 'MEDIUM';
}

async function migrateData() {
    const results = [];
    
    fs.createReadStream(path.join(__dirname, 'data', 'combined_data.csv'))
        .pipe(csv())
        .on('data', (data) => results.push(data))
        .on('end', async () => {
            try {
                console.log(`Starting migration of ${results.length} records...`);
                let successCount = 0;
                let errorCount = 0;

                for (const row of results) {
                    try {
                        // Create or get existing user
                        const user = await createUser(row);
                        if (!user) continue;

                        // Create location
                        const location = await createLocation(row);
                        if (!location) continue;

                        // Create grievance
                        const grievance = await createGrievance(row, user.id, location.id);
                        if (grievance) {
                            successCount++;
                            if (successCount % 10 === 0) {
                                console.log(`Processed ${successCount} records successfully`);
                            }
                        }
                    } catch (error) {
                        errorCount++;
                        console.error(`Error processing row:`, error);
                    }
                }

                console.log('\nMigration completed:');
                console.log(`Successfully migrated: ${successCount} records`);
                console.log(`Failed to migrate: ${errorCount} records`);
            } catch (error) {
                console.error('Migration failed:', error);
            } finally {
                await prisma.$disconnect();
            }
        });
}

async function main() {
    try {
        // First create departments
        await createDepartments();
        
        // Then setup the database
        await setupDatabase();
        
        // Then run the data migration
        await migrateData();
    } catch (error) {
        console.error('Error:', error);
        process.exit(1);
    } finally {
        await prisma.$disconnect();
    }
}

// Run the main function
main().catch(console.error);
