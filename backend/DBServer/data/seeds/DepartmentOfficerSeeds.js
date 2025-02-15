const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const csv = require('csv-parser');
const path = require('path');

const prisma = new PrismaClient();

const ranks = [
    'Junior Officer', 
    'Senior Officer', 
    'Deputy Officer', 
    'Assistant Officer', 
    'Chief Officer',
    'Principal Officer',
    'Associate Officer',
    'Executive Officer',
    'Head Officer',
    'Technical Officer'
];

const qualifications = [
    'BTech', 'MTech', 'PhD', 'MSc', 'MBA', 
    'BBA', 'MCA', 'MA Public Administration',
    'MSc Environmental Science', 'BTech Civil',
    'MTech Environmental', 'BSc', 'MSc Urban Planning'
];

const specializations = [
    'Civil Engineering',
    'Environmental Engineering',
    'Urban Planning',
    'Public Administration',
    'Infrastructure Management',
    'Water Resources',
    'Transportation',
    'Waste Management',
    'Rural Development',
    'Urban Development',
    'Public Health',
    'Smart City Planning',
    'Disaster Management',
    'Environmental Impact Assessment',
    'Geographic Information Systems'
];

async function loadCSVData() {
    try {
        console.log('Starting to load CSV data...');
        const users = [];
        const addresses = [];
        const existingOfficers = [];

        // Load users
        console.log('Loading users from CSV...');
        await new Promise((resolve, reject) => {
            fs.createReadStream(path.join(__dirname, './users.csv'))
                .pipe(csv())
                .on('data', (row) => users.push(row.Name))
                .on('end', () => {
                    console.log(`Loaded ${users.length} users`);
                    resolve();
                })
                .on('error', reject);
        });

        // Load addresses
        console.log('Loading addresses from CSV...');
        await new Promise((resolve, reject) => {
            fs.createReadStream(path.join(__dirname, './addr.csv'))
                .pipe(csv())
                .on('data', (row) => {
                    addresses.push(`${row['_1']}, ${row['_2']}, ${row['_3']}, ${row['_4']}, ${row['_5']}, ${row['_6']}, ${row['_7']}`);
                })
                .on('end', () => {
                    console.log(`Loaded ${addresses.length} addresses`);
                    resolve();
                })
                .on('error', reject);
        });

        // Load existing officers
        console.log('Loading existing officers from CSV...');
        await new Promise((resolve, reject) => {
            fs.createReadStream(path.join(__dirname, '../departmentofficers.csv'))
                .pipe(csv())
                .on('data', (row) => existingOfficers.push(row))
                .on('end', () => {
                    console.log(`Loaded ${existingOfficers.length} existing officers`);
                    resolve();
                })
                .on('error', reject);
        });

        return { users, addresses, existingOfficers };
    } catch (error) {
        console.error('Error loading CSV data:', error);
        throw error;
    }
}

async function generateOfficer(name, address, departmentId, rank) {
    const nameParts = name.split(' ');
    const firstName = nameParts[0];
    const lastName = nameParts[1] || '';
    const existingOfficer = await getRandomExistingOfficer();
    
    // Calculate experience-appropriate age based on rank
    const baseAge = rank.includes('Senior') || rank.includes('Chief') ? 35 : 25;
    const ageRange = rank.includes('Senior') || rank.includes('Chief') ? 25 : 35;
    
    return {
        name: name,
        email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}${Math.floor(Math.random() * 999)}@gmail.com`,
        age: baseAge + Math.floor(Math.random() * ageRange),
        gender: Math.random() > 0.7 ? 'Female' : 'Male', // 30% female representation
        address: address,
        departmentId: departmentId,
        rank: rank,
        dateAssigned: new Date(2018 + Math.floor(Math.random() * 7), Math.floor(Math.random() * 12), Math.floor(Math.random() * 28)),
        contactNumber: `9${Math.floor(Math.random() * 1000000000)}`.padEnd(10, '0'),
        aadharNumber: `${Math.floor(Math.random() * 10000)} ${Math.floor(Math.random() * 10000)} ${Math.floor(Math.random() * 10000)}`,
        qualification: existingOfficer?.qualification || qualifications[Math.floor(Math.random() * qualifications.length)],
        specialization: existingOfficer?.specialization || specializations[Math.floor(Math.random() * specializations.length)]
    };
}

async function getDepartments() {
    console.log('Fetching departments from database...');
    const departments = await prisma.department.findMany({
        select: {
            id: true,
            departmentName: true
        }
    });
    console.log(`Found ${departments.length} departments`);
    return departments;
}

let existingOfficersData = [];
async function getRandomExistingOfficer() {
    if (existingOfficersData.length === 0) {
        const { existingOfficers } = await loadCSVData();
        existingOfficersData = existingOfficers;
    }
    return existingOfficersData[Math.floor(Math.random() * existingOfficersData.length)];
}

async function seedDepartmentOfficers() {
    try {
        console.log('Starting department officers seeding...');
        
        const { users, addresses } = await loadCSVData();
        const departments = await getDepartments();

        if (departments.length === 0) {
            throw new Error('No departments found in the database. Please seed departments first.');
        }

        console.log(`Creating 250 officers across ${departments.length} departments...`);
        const allOfficers = [];

        // Calculate officers per department (minimum 2)
        const officersPerDepartment = Math.max(2, Math.ceil(250 / departments.length));

        // Create officers for each department
        for (const department of departments) {
            console.log(`Processing department: ${department.departmentName}`);
            
            // Ensure each department gets a mix of ranks
            const departmentRanks = [...ranks].sort(() => Math.random() - 0.5)
                                            .slice(0, officersPerDepartment);
            
            for (const rank of departmentRanks) {
                const randomUser = users[Math.floor(Math.random() * users.length)];
                const randomAddress = addresses[Math.floor(Math.random() * addresses.length)];
                
                const officer = await generateOfficer(randomUser, randomAddress, department.id, rank);
                allOfficers.push(officer);
                console.log(`Created ${rank} for department ${department.departmentName}`);

                // Stop if we've reached 250 officers
                if (allOfficers.length >= 250) break;
            }
            if (allOfficers.length >= 250) break;
        }

        // Insert all officers
        for (const officer of allOfficers) {
            await prisma.departmentOfficer.create({
                data: officer
            });
            console.log(`Inserted officer: ${officer.name} as ${officer.rank}`);
        }

        console.log(`Successfully seeded ${allOfficers.length} department officers`);
    } catch (error) {
        console.error('Error seeding department officers:', error);
        console.error('Stack trace:', error.stack);
        if (error.meta) {
            console.error('Prisma error details:', error.meta);
        }
    } finally {
        await prisma.$disconnect();
    }
}

// Execute with proper error handling
seedDepartmentOfficers().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
