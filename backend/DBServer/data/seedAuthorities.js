const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function seedAuthorities() {
  try {
    // First get all departments with their IDs
    const departments = await prisma.department.findMany({
      select: {
        id: true,
        departmentName: true
      }
    });

    console.log('Creating authorities for existing departments...');
    
    for (const dept of departments) {
      const authorityName = `${dept.departmentName} Department Head`;
      const emailPrefix = dept.departmentName.toLowerCase().replace(/\s+/g, '.');
      
      // Create authority
      const authority = await prisma.authority.upsert({
        where: {
          email: `${emailPrefix}.head@upgms.gov.in`
        },
        update: {
          name: authorityName,
          role: 'DEPARTMENT_HEAD',
          assignedRegion: `UP ${dept.departmentName} Region`
        },
        create: {
          name: authorityName,
          email: `${emailPrefix}.head@upgms.gov.in`,
          role: 'DEPARTMENT_HEAD',
          assignedRegion: `UP ${dept.departmentName} Region`
        }
      });

      // Update department with new authority using ID
      await prisma.department.update({
        where: { 
          id: dept.id  // Use the department's ID for the update
        },
        data: { 
          authorityId: authority.id 
        }
      });

      console.log(`Created/Updated authority for: ${dept.departmentName}`);
    }

    console.log('\nAuthorities created successfully!');

  } catch (error) {
    console.error('Error seeding authorities:', error);
    throw error;
  } finally {
    await prisma.$disconnect();
  }
}

seedAuthorities()
  .then(() => console.log('Authority seeding completed!'))
  .catch((error) => {
    console.error('Authority seeding failed:', error);
    process.exit(1);
  });
