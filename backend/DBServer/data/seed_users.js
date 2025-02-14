const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const path = require('path');

const prisma = new PrismaClient();

function parseDate(dateStr) {
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) {
    return new Date(); // Return current date as fallback
  }
  return date;
}

// Sample data in case CSV parsing fails
const sampleWorkers = [
  {
    position: "Field Worker",
    dateJoined: new Date(),
    contactNumber: "9876543210",
  },
  {
    position: "Site Engineer",
    dateJoined: new Date(),
    contactNumber: "9876543211",
  }
];

const sampleOfficers = [
  {
    rank: "Senior Officer",
    dateAssigned: new Date(),
    contactNumber: "9876543220",
  },
  {
    rank: "Junior Officer",
    dateAssigned: new Date(),
    contactNumber: "9876543221",
  }
];

async function seedData() {
  try {
    const departments = await prisma.department.findMany({
      select: { id: true }
    });

    if (departments.length === 0) {
      throw new Error('No departments found in database');
    }

    function getRandomDepartmentId() {
      const randomIndex = Math.floor(Math.random() * departments.length);
      return departments[randomIndex].id;
    }

    let workersToCreate = [];
    try {
      const workersCsv = fs.readFileSync(path.join(__dirname, 'workers.csv'), 'utf-8');
      workersToCreate = workersCsv
        .split('\n')
        .slice(1)  // Skip header row
        .filter(line => line.trim())
        .map(line => {
          const [position, email, date_joined, contact_number] = line.split(',').map(item => item.trim());
          if (!position || !email || !contact_number) {
            throw new Error('Missing required fields in workers.csv');
          }
          return {
            position,
            email,
            dateJoined: parseDate(date_joined),
            contactNumber: contact_number,
            departmentId: getRandomDepartmentId()
          };
        });
    } catch (error) {
      console.warn('Using sample data for workers:', error.message);
      workersToCreate = sampleWorkers.map(w => ({
        ...w,
        email: `worker${Math.random().toString(36).slice(2)}@up.gov.in`,
        departmentId: getRandomDepartmentId()
      }));
    }

    console.log('Creating workers...');
    for (const worker of workersToCreate) {
      await prisma.worker.create({
        data: worker
      });
    }

    let officersToCreate = [];
    try {
      const officersCsv = fs.readFileSync(path.join(__dirname, 'departmentofficers.csv'), 'utf-8');
      officersToCreate = officersCsv
        .split('\n')
        .slice(1)  // Skip header row
        .filter(line => line.trim())
        .map(line => {
          const [rank, email, date_assigned, contact_number] = line.split(',').map(item => item.trim());
          if (!rank || !email || !contact_number) {
            throw new Error('Missing required fields in departmentofficers.csv');
          }
          return {
            rank,
            email,
            dateAssigned: parseDate(date_assigned),
            contactNumber: contact_number,
            departmentId: getRandomDepartmentId()
          };
        });
    } catch (error) {
      console.warn('Using sample data for officers:', error.message);
      officersToCreate = sampleOfficers.map(o => ({
        ...o,
        email: `officer${Math.random().toString(36).slice(2)}@up.gov.in`,
        departmentId: getRandomDepartmentId()
      }));
    }

    console.log('Creating department officers...');
    for (const officer of officersToCreate) {
      await prisma.departmentOfficer.create({
        data: officer
      });
    }

    console.log('Data seeding completed successfully');
  } catch (error) {
    console.error('Error seeding data:', error);
    throw error;
  } finally {
    await prisma.$disconnect();
  }
}

seedData().catch(console.error);
