const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const csv = require('csv-parser');
const path = require('path');

const prisma = new PrismaClient();

async function getOrCreateLocation(row) {
  try {
    // Check if location already exists to avoid duplicates
    const existingLocation = await prisma.location.findFirst({
      where: {
        AND: [
          { location: row.location || '' },
          { district: row.district || '' },
          { pincode: row.pincode || '' }
        ]
      }
    });

    if (existingLocation) {
      return existingLocation.id;
    }

    // Create new location if it doesn't exist
    const location = await prisma.location.create({
      data: {
        gpsCoordinatesLongitude: row.gpscoordinates_longitude ? parseFloat(row.gpscoordinates_longitude) : null,
        gpsCoordinatesLatitude: row.gpscoordinates_latitude ? parseFloat(row.gpscoordinates_latitude) : null,
        location: row.location || '',
        tehsil: row.tehsil || null,
        pincode: row.pincode || '',
        district: row.district || '',
        ward: row.ward || null
      }
    });

    console.log(`Created location: ${location.location}, ${location.district}`);
    return location.id;
  } catch (error) {
    console.error(`Error creating location for ${row.location}:`, error);
    throw error;
  }
}

async function seedLocations() {
  try {
    const results = [];
    const csvPath = path.join(__dirname, '../combined_data.csv');

    return new Promise((resolve, reject) => {
      fs.createReadStream(csvPath)
        .pipe(csv())
        .on('data', (row) => results.push(row))
        .on('end', async () => {
          try {
            const locationIds = new Map();

            for (const row of results) {
              const locationKey = `${row.location}-${row.district}-${row.pincode}`;
              
              if (!locationIds.has(locationKey)) {
                const locationId = await getOrCreateLocation(row);
                locationIds.set(locationKey, locationId);
              }
            }

            console.log('Location seeding completed!');
            resolve(locationIds);
          } catch (error) {
            reject(error);
          }
        });
    });
  } catch (error) {
    console.error('Error seeding locations:', error);
    throw error;
  }
}

// Export for use in grievance seeding
module.exports = { seedLocations, getOrCreateLocation };

// If running directly
if (require.main === module) {
  seedLocations()
    .catch(console.error)
    .finally(async () => {
      await prisma.$disconnect();
    });
}
