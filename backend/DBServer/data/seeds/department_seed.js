const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const csv = require('csv-parser');
const path = require('path');

const prisma = new PrismaClient();

async function findDepartmentHead(departmentName) {
  try {
    const authority = await prisma.Authority.findFirst({
      where: {
        role: 'DEPARTMENT_HEAD',
        jurisdiction: departmentName
      }
    });
    console.log(`Looking for authority with jurisdiction: ${departmentName}`);
    return authority?.id || null;
  } catch (error) {
    console.error(`Error finding department head for ${departmentName}:`, error);
    return null;
  }
}

async function seedDepartments() {
  try {
    const departments = new Set();
    
    fs.createReadStream(path.join(__dirname, '../combined_data.csv'))
      .pipe(csv())
      .on('data', (row) => {
        if (row.departmentAssigned) {
          departments.add(row.departmentAssigned);
        }
      })
      .on('end', async () => {
        for (const deptName of departments) {
          try {
            const authorityId = await findDepartmentHead(deptName);
            console.log(`Found authorityId: ${authorityId} for department: ${deptName}`);

            const departmentData = {
              departmentName: deptName,
              description: `Department of ${deptName}`,
              issues: { create: [] },
              timestamp: new Date(),
              announcements: { create: [] },
              feedbacks: { create: [] },
              communications: { create: [] },
              workers: { create: [] },
              resourceId: Math.floor(Math.random() * 1000).toString(),
              hierarchyLevel: 'MID',
             // headAuthorityId: authorityId,
              
              authority: authorityId ? {
                connect: { id: authorityId }
              } : undefined
            };

            await prisma.department.create({
              data: departmentData
            });

            console.log(`Created department: ${deptName}`);
          } catch (error) {
            console.error(`Error creating department ${deptName}:`, error);
          }
        }
        console.log('Department seeding completed');
      });
  } catch (error) {
    console.error('Error seeding departments:', error);
  }
}

seedDepartments()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
