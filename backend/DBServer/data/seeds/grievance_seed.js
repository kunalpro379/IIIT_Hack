const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const csv = require('csv-parse');
const prisma = new PrismaClient();

async function getDefaultAuthority() {
  const authority = await prisma.authority.findFirst();
  if (!authority) {
    throw new Error('No authority found in database. Please ensure authorities exist before seeding.');
  }
  return authority;
}

async function ensureDepartment(departmentName) {
  let department = await prisma.department.findFirst({
    where: { departmentName: departmentName }
  });

  if (!department) {
    const authority = await getDefaultAuthority();
    department = await prisma.department.create({
      data: {
        departmentName: departmentName,
        description: `Department of ${departmentName}`,
        hierarchyLevel: "DEPARTMENT",
        resourceId: Math.random().toString(36).substring(7),
        authority: {
          connect: {
            id: authority.id
          }
        },
        timestamp: new Date(),
      }
    });
    console.log(`Created new department: ${departmentName}`);
  }

  return department;
}

async function ensureLocation(locationString) {
  const [city, state] = locationString.split(',').map(s => s.trim());

  let location = await prisma.location.findFirst({
    where: { location: city }
  });

  if (!location) {
    location = await prisma.location.create({
      data: {
        location: city,
        gpsCoordinatesLatitude: 26 + Math.random() * 4,
        gpsCoordinatesLongitude: 78 + Math.random() * 5,
        tehsil: 'N/A',
        pincode: Math.floor(200000 + Math.random() * 99999).toString(),
        district: city,
        ward: 'N/A'
      }
    });
    console.log(`Created new location: ${city}`);
  }

  return location;
}

async function ensureUser(record) {
  let user = await prisma.user.findFirst({
    where: { email: record.email }
  });

  if (!user) {
    user = await prisma.user.create({
      data: {
        name: record.citizenName || 'Anonymous User',
        email: record.email,
        password: 'abcd1234', // In production, use proper password hashing
        role: 'CITIZEN',
        createdAt: new Date(),
        updatedAt: new Date()
      }
    });
    console.log(`Created new user: ${user.email}`);
  }

  return user;
}

function mapStatus(status) {
  if (!status) return 'PENDING';
  
  // Convert to uppercase and normalize
  const normalizedStatus = String(status).toUpperCase().trim();
  
  // Direct mapping of normalized status to enum values
  const statusMap = {
    'OPEN': 'PENDING',
    'PENDING': 'PENDING',
    'IN_PROGRESS': 'IN_PROGRESS',
    'IN PROGRESS': 'IN_PROGRESS',
    'INPROGRESS': 'IN_PROGRESS',
    'CLOSED': 'CLOSED'
  };
  
  return statusMap[normalizedStatus] || 'PENDING';
}

function mapUrgencyLevel(level) {
  if (!level) return 'MEDIUM';
  
  // Convert to uppercase and normalize
  const normalizedLevel = String(level).toUpperCase().trim();
  
  // Direct mapping of normalized urgency to enum values
  const levelMap = {
    'LOW': 'LOW',
    'MEDIUM': 'MEDIUM',
    'MED': 'MEDIUM',
    'HIGH': 'HIGH',
    'CRITICAL': 'CRITICAL'
  };
  
  return levelMap[normalizedLevel] || 'MEDIUM';
}

async function main() {
  const fileContent = fs.readFileSync('../combined_data.csv', 'utf-8');
  
  const parser = csv.parse(fileContent, {
    columns: true,
    skip_empty_lines: true
  });

  for await (const record of parser) {
    try {
      const department = await ensureDepartment(record.departmentAssigned || 'General Department');
      const location = await ensureLocation(record.location || 'Unknown Location, Uttar Pradesh');
      const user = await ensureUser(record);

      const status = mapStatus(record.status);
      const urgencyLevel = mapUrgencyLevel(record.urgencyLevel);
      
      console.log(`Processing record [${record.id}]:`);
      console.log(`Raw status: "${record.status}" -> "${status}"`);
      console.log(`Raw urgency: "${record.urgencyLevel}" -> "${urgencyLevel}"`);

      const grievanceData = {
        id: record.id,
        title: record.title,
        complaint: record.complaint || null,
        complaintType: record.complaintType || 'General',
        category: record.category || 'General',
        subcategory: record.subcategory || 'General',
        status,
        urgencyLevel,
        priorityLevel: 'MEDIUM',
        isAnonymous: record.isAnonymous === 'True',
        economicImpact: record.economicImpact || null,
        socialImpact: record.socialImpact || null,
        environmentalImpact: record.environmentalImpact ||'',
        emotion: record.emotion || null,
        estimated: parseInt(record.estimated) || null,
        ResolutionTime: parseInt(record.ResolutionTime) || null,
        estimatedResolutionTime: record.ResolutionTime || null,
        relatedPolicies: record.relatedPolicies || null,
        timestamp: new Date(),
        lastUpdatedDate: record.lastUpdatedDate ? new Date(record.lastUpdatedDate) : null,
        submissionDate: record.submissionDate ? new Date(record.submissionDate) : null,
        currentLevel: 'INITIAL',
        escalationHistory: null,
        assignedAuthorities: null,
        resolutionPath: [],
        
        // Relations
        departmentId: department.id,
        
        // // Timestamps
        // createdAt: record.CreatedAt ? new Date(record.CreatedAt) : new Date(),
        // updatedAt: record.updatedAt ? new Date(record.updatedAt) : new Date()
      };

      await prisma.grievance.create({ data: grievanceData });
      console.log(`Created grievance: ${record.title}`);
    } catch (error) {
      console.error(`Error processing record ${record.id}:`);
      console.error(`Input status: "${record.status}"`);
      console.error(`Input urgencyLevel: "${record.urgencyLevel}"`);
      console.error(error);
    }
  }
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });