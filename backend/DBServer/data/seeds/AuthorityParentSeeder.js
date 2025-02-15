const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function updateParentIds() {
    try {
        console.log('Starting parent ID updates...');

        // Define role relationships
        const roleRelationships = [
            { role: 'ADMINISTRATOR', parentRole: null },
            { role: 'BLOCK_OFFICER', parentRole: 'DISTRICT_MAGISTRATE' },
            { role: 'CITIZEN', parentRole: 'PANCHAYAT_OFFICER' },
            { role: 'COMMISSIONER', parentRole: 'ADMINISTRATOR' },
            { role: 'DEPARTMENT_HEAD', parentRole: 'COMMISSIONER' },
            { role: 'DEPARTMENT_OFFICER', parentRole: 'DEPARTMENT_HEAD' },
            { role: 'DISTRICT_MAGISTRATE', parentRole: 'COMMISSIONER' },
            { role: 'FIELD_WORKER', parentRole: 'BLOCK_OFFICER' },
            { role: 'NAGAR_SEVAK', parentRole: 'DISTRICT_MAGISTRATE' },
            { role: 'GRAM_PANCHAYAT', parentRole: 'PANCHAYAT_OFFICER' }
        ];

        for (const relationship of roleRelationships) {
            const authorities = await prisma.authority.findMany({
                where: { role: relationship.role }
            });

            if (relationship.parentRole === null) {
                console.log(`Setting null parentId for ${relationship.role} authorities`);
                for (const authority of authorities) {
                    await prisma.authority.update({
                        where: { id: authority.id },
                        data: { parentId: null }
                    });
                }
                continue;
            }

            const potentialParents = await prisma.authority.findMany({
                where: { role: relationship.parentRole }
            });

            if (potentialParents.length === 0) {
                console.log(`No ${relationship.parentRole} found for ${relationship.role}`);
                continue;
            }

            // Randomly select a parent from potential parents
            const randomParent = potentialParents[Math.floor(Math.random() * potentialParents.length)];

            console.log(`Updating ${authorities.length} ${relationship.role} authorities with parent ${randomParent.name} (${relationship.parentRole})`);

            for (const authority of authorities) {
                await prisma.authority.update({
                    where: { id: authority.id },
                    data: { parentId: randomParent.id }
                });
                console.log(`Updated ${authority.name} with parent ${randomParent.name}`);
            }
        }

        console.log('Parent ID updates completed successfully');
    } catch (error) {
        console.error('Error updating parent IDs:', error);
        throw error;
    } finally {
        await prisma.$disconnect();
    }
}

// Execute the update
updateParentIds()
    .catch(error => {
        console.error('Failed to update parent IDs:', error);
        process.exit(1);
    });
