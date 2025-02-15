const { PrismaClient } = require('@prisma/client');
const fs = require('fs').promises;
const path = require('path');

const prisma = new PrismaClient();

async function exportUsers() {
    try {
        // Fetch all users from database
        const users = await prisma.user.findMany({
            select: {
                name: true
            }
        });

        // Convert to CSV format
        const csvContent = ['Name']; // Header
        users.forEach(user => {
            csvContent.push(user.name);
        });

        // Save to file
        const filePath = path.join(__dirname, './users.csv');
        await fs.writeFile(filePath, csvContent.join('\n'));

        console.log(`Successfully exported ${users.length} users to users.csv`);
    } catch (error) {
        console.error('Error exporting users:', error);
    } finally {
        await prisma.$disconnect();
    }
}

exportUsers();
