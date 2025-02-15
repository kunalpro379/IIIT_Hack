const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const csv = require('csv-parser');
const path = require('path');

const prisma = new PrismaClient();

async function getDepartmentAndAuthorities() {
  const departments = await prisma.department.findMany({ select: { id: true } });
  const authorities = await prisma.authority.findMany({ select: { id: true } });

  if (departments.length === 0) {
    throw new Error('No departments found. Please seed departments first.');
  }
  if (authorities.length === 0) {
    throw new Error('No authorities found. Please seed authorities first.');
  }

  return { departments, authorities };
}

function getRandomId(array) {
  return array[Math.floor(Math.random() * array.length)];
}

async function seedCommunications() {
  try {
    const results = [];
    const csvPath = path.join(__dirname, '../communication.csv');
    console.log('Reading CSV from:', csvPath);

    const { departments, authorities } = await getDepartmentAndAuthorities();

    fs.createReadStream(csvPath)
      .pipe(csv())
      .on('data', (row) => results.push(row))
      .on('end', async () => {
        for (const row of results) {
          try {
            const sender = getRandomId(departments);
            const receiver = getRandomId(authorities);

            await prisma.communication.create({
              data: {
                senderId: sender.id,
                receiverId: receiver.id,
                message: row.message || 'No message content',
                timestamp: new Date(row.timestamp || Date.now()),
                attachments: row.attachments ? JSON.parse(row.attachments) : []
              }
            });
            console.log(`Created communication from Department:${sender.id} to Authority:${receiver.id}`);
          } catch (error) {
            console.error(`Error processing row:`, error);
          }
        }
        console.log('Communication seeding completed');
      });
  } catch (error) {
    console.error('Error seeding communications:', error);
  }
}

seedCommunications()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
