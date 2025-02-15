const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const csv = require('csv-parser');
const path = require('path');

const prisma = new PrismaClient();

const positions = ['first', 'second', 'third'];

async function getDepartmentIds() {
    const departments = await prisma.department.findMany({
        select: {
            id: true
        }
    });
    return departments.map(dep => dep.id);
}

async function loadCSVData() {
    const users = [];
    const addresses = [];
    const workers = [];

    // Load users
    await new Promise((resolve, reject) => {
        fs.createReadStream(path.join(__dirname, './users.csv'))
            .pipe(csv())
            .on('data', (row) => users.push(row.Name))
            .on('end', resolve)
            .on('error', reject);
    });

    // Load addresses
    await new Promise((resolve, reject) => {
        fs.createReadStream(path.join(__dirname, './addr.csv'))
            .pipe(csv())
            .on('data', (row) => {
                addresses.push(`${row['_1']}, ${row['_2']}, ${row['_3']}, ${row['_4']}, ${row['_5']}, ${row['_6']}, ${row['_7']}`);
            })
            .on('end', resolve)
            .on('error', reject);
    });

    // Load existing workers
    await new Promise((resolve, reject) => {
        fs.createReadStream(path.join(__dirname, '../workers.csv'))
            .pipe(csv())
            .on('data', (row) => workers.push(row))
            .on('end', resolve)
            .on('error', reject);
    });

    return { users, addresses, workers };
}

async function generateWorker(name, address, departmentIds) {
    const isMale = Math.random() < 0.8;
    const nameParts = name.split(' ');
    const firstName = nameParts[0];
    const lastName = nameParts[1] || '';
    
    return {
        name: name,
        email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}${Math.floor(Math.random() * 999)}@gmail.com`,
        age: 20 + Math.floor(Math.random() * 40),
        gender: isMale ? 'Male' : 'Female',
        address: address,
        departmentId: departmentIds[Math.floor(Math.random() * departmentIds.length)],
        position: positions[Math.floor(Math.random() * positions.length)],
        dateJoined: new Date(2020 + Math.floor(Math.random() * 3), Math.floor(Math.random() * 12), Math.floor(Math.random() * 28)),
        contactNumber: `9${Math.floor(Math.random() * 1000000000)}`.padEnd(10, '0'),
        emergencyContact: null,
        bloodGroup: null,
        aadharNumber: `${Math.floor(Math.random() * 10000)} ${Math.floor(Math.random() * 10000)} ${Math.floor(Math.random() * 10000)}`
    };
}

async function seedWorkers() {
    try {
        const { users, addresses, workers: existingWorkers } = await loadCSVData();
        const departmentIds = await getDepartmentIds();

        if (departmentIds.length === 0) {
            throw new Error('No departments found in the database. Please seed departments first.');
        }

        // Start with existing workers - Fix field mappings
        let allWorkers = [...existingWorkers.map(w => ({
            name: w.name,
            email: w.email,
            age: parseInt(w.age),
            gender: w.gender,
            address: w.address,
            position: w.position,
            dateJoined: new Date(w.date_joined),
            contactNumber: w.contact_number, // Map to correct field name
            emergencyContact: w.emergency_contact,
            bloodGroup: w.blood_group,
            aadharNumber: w.aadhar_number,
            departmentId: departmentIds[Math.floor(Math.random() * departmentIds.length)]
        }))];

        // Generate remaining workers
        const remainingCount = 300 - allWorkers.length;
        for (let i = 0; i < remainingCount; i++) {
            const randomUser = users[Math.floor(Math.random() * users.length)];
            const randomAddress = addresses[Math.floor(Math.random() * addresses.length)];
            allWorkers.push(await generateWorker(randomUser, randomAddress, departmentIds));
        }

        // Insert all workers
        for (const worker of allWorkers) {
            await prisma.worker.create({
                data: worker
            });
        }

        console.log('Successfully seeded 300 workers');
    } catch (error) {
        console.error('Error seeding workers:', error);
        console.error('Failed worker data:', error.meta?.cause);
    } finally {
        await prisma.$disconnect();
    }
}

seedWorkers();
