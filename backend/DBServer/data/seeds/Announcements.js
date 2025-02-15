const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const csv = require('csv-parser');
const path = require('path');
const { v4: uuidv4 } = require('uuid'); // Add this line at the top

const prisma = new PrismaClient();

const audienceRoles = [
  'DISTRICT_MAGISTRATE', 'COMMISSIONER', 'ADMINISTRATOR', 'DEPARTMENT_HEAD', 
  'NAGAR_SEVAK', 'CITIZEN', 'DEPARTMENT_OFFICER', 'PANCHAYAT_OFFICER', 
  'FIELD_WORKER', 'BLOCK_OFFICER'
];

function getRandomRoles() {
  const shuffled = audienceRoles.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, Math.floor(Math.random() * (audienceRoles.length - 1)) + 2);
}

async function createOrGetAuthority() {
  let authority = await prisma.authority.findFirst();
  
  if (!authority) {
    authority = await prisma.authority.create({
      data: {
        name: "Default Authority",
        description: "Default authority for announcements",
        resourceId: "default-authority",
        timestamp: new Date(),
        hierarchyLevel: "STATE"
      }
    });
    console.log('Created default authority');
  }
  
  return authority;
}

async function seedAnnouncements() {
  try {
    const results = [];
    const csvPath = path.join(__dirname, '../Announcements.csv');
    console.log('Reading CSV from:', csvPath);

    const authority = await createOrGetAuthority();

    fs.createReadStream(csvPath)
      .pipe(csv())
      .on('data', (row) => results.push(row))
      .on('end', async () => {
        for (const row of results) {
          try {
            if (!row.title || !row.description) {
              console.log('Skipping row with missing title or description');
              continue;
            }

            const authority = await prisma.authority.findFirst();
            if (!authority) {
              throw new Error('No authority found in database.');
            }

            // Find or create a default department if needed
            const department = await prisma.department.findFirst();

            await prisma.announcement.create({
              data: {
                title: row.title,
                description: row.description,
                announceForRole: getRandomRoles(),
                channels: [], // Empty array instead of null
                attachments: [], // Empty array instead of null
                citizenReactions: row.citizenReactions || "{}",
                comments: row.comments || "[]",
                authority: {
                  connect: { id: authority.id }
                },
                department: department ? {
                  connect: { id: department.id }
                } : undefined
              }
            });
            console.log(`Created announcement: ${row.title}`);
          } catch (error) {
            console.error(`Error processing row:`, error);
          }
        }
        console.log('Announcement seeding completed');
      });
  } catch (error) {
    console.error('Error seeding announcements:', error);
  }
}

seedAnnouncements()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
