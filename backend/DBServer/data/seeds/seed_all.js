const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const csv = require('csv-parser');
const path = require('path');

const prisma = new PrismaClient();

function generateTitle(row) {
  // Get location and type
  const location = row.location?.split(',')[0] || '';
  const issueType = row.complaintType || row.category || '';
  const complaint = row.complaint || '';
  const shortComplaint = complaint.split(' ').slice(0, 4).join(' ');

  // Generate meaningful title
  if (issueType && location) {
    return `${issueType} Issue in ${location}`;
  }
  if (issueType && shortComplaint) {
    return `${issueType}: ${shortComplaint}`;
  }
  if (location && shortComplaint) {
    return `${location} - ${shortComplaint}`;
  }
  if (shortComplaint) {
    return shortComplaint;
  }
  return `Civic Issue #${row.id || ''}`;
}

async function createOrGetUser(row) {
  try {
    const cleanName = row.citizenName?.toLowerCase().replace(/\s+/g, '') || 'anonymous';
    const randomNum = Math.floor(10 + Math.random() * 900);
    const email = `${cleanName}${randomNum}@gmail.com`;
    const citizenName = row.citizenName || 'Anonymous User';

    // Check if user exists
    let user = await prisma.user.findUnique({
      where: { email: email }
    });

    // If user doesn't exist, create new user
    if (!user) {
      user = await prisma.user.create({
        data: {
          name: citizenName,
          email: email,
          password: cleanName, // Using cleaned name as password
          role: 'CITIZEN'
        }
      });
      console.log(`Created new user: ${citizenName} with email: ${email}`);
    }

    return user;
  } catch (error) {
    console.error(`Error creating/getting user ${row.citizenName}:`, error);
    throw error;
  }
}

async function getDepartmentId(departmentName) {
  try {
    // First find the department
    let department = await prisma.department.findFirst({
      where: { departmentName: departmentName }
    });

    // If department exists, return its ID
    if (department) {
      return department.id;
    }

    // If department doesn't exist, create it
    const authority = await prisma.authority.findFirst();
    if (!authority) {
      throw new Error('No authority found in database.');
    }

    department = await prisma.department.create({
      data: {
        departmentName: departmentName,
        description: `Department of ${departmentName}`,
        hierarchyLevel: "DEPARTMENT",
        resourceId: Math.random().toString(36).substring(7),
        timestamp: new Date(),
        authority: {
          connect: { id: authority.id }
        }
      }
    });
    console.log(`Created new department: ${departmentName}`);
    return department.id;
  } catch (error) {
    console.error(`Error creating/getting department ${departmentName}:`, error);
    throw error;
  }
}

async function createOrGetLocation(row) {
  try {
    const locationName = row.location?.split(',')[0] || 'Unknown';
    const district = row.district || locationName;
    const pincode = row.pincode || '';
    const gpsCoordinatesLatitude = parseFloat(row.gpscoordinates_latitude) || 0;
    const gpsCoordinatesLongitude = parseFloat(row.gpscoordinates_longitude) || 0;

    // Check if location exists using only schema fields
    let location = await prisma.location.findFirst({
      where: {
        ward: locationName,
        district: district,
        location: locationName,
        gpsCoordinatesLatitude: gpsCoordinatesLatitude,
        gpsCoordinatesLongitude: gpsCoordinatesLongitude
      }
    });

    // If location doesn't exist, create new location
    if (!location) {
      location = await prisma.location.create({
        data: {
          ward: locationName,
          district: district,
          pincode: pincode,
          gpsCoordinatesLatitude: gpsCoordinatesLatitude,
          gpsCoordinatesLongitude: gpsCoordinatesLongitude,
          location: locationName // Add location field to creation
        }
      });
      console.log(`Created new location: ${locationName}, ${district}`);
    }

    return location;
  } catch (error) {
    console.error(`Error creating/getting location:`, error);
    throw error;
  }
}

async function seedGrievances() {
  try {
    const results = [];
    const csvPath = path.join(__dirname, '../combined_data.csv');
    console.log('Reading CSV from:', csvPath);

    fs.createReadStream(csvPath)
      .pipe(csv())
      .on('data', (row) => results.push(row))
      .on('end', async () => {
        for (const row of results) {
          try {
            const generatedTitle = generateTitle(row);
            const departmentId = await getDepartmentId(row.departmentAssigned);
            
            // Create or get user and location
            const user = await createOrGetUser(row);
            const location = await createOrGetLocation(row);

            await prisma.grievance.create({
              data: {
                title: generatedTitle,
                category: row.category || '',
                subcategory: row.subcategory || '',
                status: row.status || 'Open',
                urgencyLevel: row.urgencyLevel || 'Low',
                submissionDate: new Date(row.submissionDate || row.date || row.CreatedAt),
                lastUpdatedDate: new Date(row.lastUpdatedDate || row.updatedAt || row.CreatedAt),
                estimatedResolutionTime: row.ResolutionTime || null,
                economicImpact: row.economicImpact || '',
                socialImpact: row.socialImpact || '',
                environmentalImpact: row.environmentalImpact || '',
                emotion: row.emotion || '',
                relatedPolicies: row.relatedPolicies,
                complaintType: row.complaintType || '',
                priorityLevel: row.priorityLevel || 'MEDIUM',
                currentLevel: '',
                complaint: row.complaint,
                department: {
                  connect: { id: departmentId }
                },
                user: {
                  connect: { id: user.id }
                },
                location: {
                  connect: { id: location.id }  // Use location.id instead of locationId
                }
              }
            });

            console.log(`Created grievance: ${generatedTitle} for user: ${user.name} in location: ${location.name}`);
          } catch (error) {
            console.error(`Error processing row:`, error);
          }
        }
        console.log('Grievance and user seeding completed');
      });
  } catch (error) {
    console.error('Error seeding grievances:', error);
  }
}

seedGrievances()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
