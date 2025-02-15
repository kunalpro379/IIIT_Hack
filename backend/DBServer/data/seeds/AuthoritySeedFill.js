const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const csv = require('csv-parse');
const path = require('path');

const prisma = new PrismaClient();

function formatAuthorityEmail(name, level, role) {
    // Clean the name: remove special chars, spaces and convert to lowercase
    const cleanName = name.toLowerCase()
        .replace(/[^a-z\s]/g, '')
        .replace(/\s+/g, '.');
    
    // Get level abbreviation
    const levelAbbr = {
        'TOP': 't',
        'MID': 'm',
        'OPERATIONAL': 'o'
    }[level] || 'x';

    // Get role abbreviation (first 3 letters)
    const roleAbbr = role.substring(0, 3).toLowerCase();

    return `${cleanName}.${levelAbbr}${roleAbbr}@up.gov.in`;
}

function mapAuthorityLevel(level) {
    const levelMap = {
        'TOP': 'TOP',
        'TOP_LEVEL': 'TOP',
        'MID': 'MID',
        'MID_LEVEL': 'MID',
        'OPERATIONAL': 'OPERATIONAL',
        'OPERATIONAL_LEVEL': 'OPERATIONAL',
        'CITIZEN_LEVEL': 'OPERATIONAL',
        'DISTRICT_LEVEL': 'TOP',
    };
    return levelMap[level] || 'OPERATIONAL';
}

async function seedAuthorities() {
    try {
        // Update this line to use the correct path
        const csvFilePath = path.join(__dirname, 'Authority_Merged.csv');
        
        // Check if file exists before reading
        if (!fs.existsSync(csvFilePath)) {
            throw new Error(`CSV file not found at: ${csvFilePath}`);
        }

        const fileContent = fs.readFileSync(csvFilePath, 'utf-8');

        // Parse CSV data with improved casting
        const records = await new Promise((resolve, reject) => {
            csv.parse(fileContent, {
                columns: true,
                skip_empty_lines: true,
                cast: (value, context) => {
                    if (value === 'null' || value === '') return null;
                    // Handle boolean values properly
                    if (value === 'True' || value === 'true') return true;
                    if (value === 'False' || value === 'false') return false;
                    if (context.column === 'villageCount' && value) return parseInt(value);
                    if (value && typeof value === 'string' && value.startsWith('{')) {
                        try {
                            return JSON.parse(value);
                        } catch (e) {
                            return value;
                        }
                    }
                    return value;
                }
            }, (err, records) => {
                if (err) reject(err);
                else resolve(records);
            });
        });

        console.log(`Found ${records.length} authority records to process`);

        // First pass: Create authorities without relationships
        for (const record of records) {
            const formattedEmail = formatAuthorityEmail(record.name, record.level, record.role);
            
            const authorityData = {
                name: record.name,
                email: formattedEmail, // Use the new formatted email
                role: record.role,
                level: mapAuthorityLevel(record.level),
                assignedRegion: record.assignedRegion,
                jurisdiction: record.jurisdiction,
                designation: record.designation,
                contactNumber: record.contactNumber,
                officeAddress: record.officeAddress,
                isActive: Boolean(record.isActive === 'True' || record.isActive === true),
                blockJurisdiction: record.blockJurisdiction,
                panchayatArea: record.panchayatArea,
                wardNumber: record.wardNumber,
                specialization: record.specialization,
                fieldArea: record.fieldArea,
                gramSabhaArea: record.gramSabhaArea,
                villageCount: record.villageCount,
                panchayatDetails: record.panchayatDetails,
                panchayatWorkers: record.panchayatWorkers,
                panchayatOfficers: record.panchayatOfficers
            };

            try {
                await prisma.authority.upsert({
                    where: { email: formattedEmail },
                    update: authorityData,
                    create: authorityData
                });
                console.log(`Processed authority: ${record.name} with email: ${formattedEmail}`);
            } catch (error) {
                console.error(`Failed to create/update authority ${formattedEmail}:`, error);
                console.error('Data that caused error:', JSON.stringify(authorityData, null, 2));
            }
        }

        // Second pass: Update relationships
        for (const record of records) {
            try {
                const updates = {
                    where: { email: record.email },
                    data: {}
                };

                if (record.parentId) {
                    const parent = await prisma.authority.findFirst({
                        where: { id: record.parentId }
                    });
                    if (parent) {
                        updates.data.parentAuthority = { connect: { id: parent.id } };
                    }
                }

                if (record.departmentId) {
                    const department = await prisma.department.findFirst({
                        where: { id: record.departmentId }
                    });
                    if (department) {
                        updates.data.department = { connect: { id: department.id } };
                    }
                }

                if (Object.keys(updates.data).length > 0) {
                    await prisma.authority.update(updates);
                }
            } catch (error) {
                console.error(`Failed to update relationships for ${record.email}:`, error);
            }
        }

        console.log('Authority seeding completed successfully');
    } catch (error) {
        console.error('Error seeding authorities:', error);
        throw error;
    } finally {
        await prisma.$disconnect();
    }
}

// Execute seeding
seedAuthorities()
    .catch(error => {
        console.error('Failed to seed database:', error);
        process.exit(1);
    });
