import pandas as pd
import random

# Sample data for cities and localities in Uttar Pradesh
cities = [
    ("Lucknow", "226001"), ("Kanpur", "208001"), ("Varanasi", "221001"), ("Agra", "282001"),
    ("Meerut", "250001"), ("Prayagraj", "211001"), ("Ghaziabad", "201001"), ("Noida", "201301"),
    ("Bareilly", "243001"), ("Gorakhpur", "273001"), ("Aligarh", "202001"), ("Moradabad", "244001"),
    ("Saharanpur", "247001"), ("Jhansi", "284001"), ("Rampur", "244901"), ("Firozabad", "283203"),
    ("Muzaffarnagar", "251001"), ("Mathura", "281001"), ("Ayodhya", "224123"), ("Sitapur", "261001"),
    ("Bijnor", "246701"), ("Faizabad", "224001"), ("Basti", "272001"), ("Etawah", "206001"),
    ("Shahjahanpur", "242001"), ("Farrukhabad", "209625"), ("Mau", "275101"), ("Etah", "207001"),
    ("Deoria", "274001"), ("Mainpuri", "205001"), ("Hapur", "245101"), ("Unnao", "209801")
]

localities = [
    "Civil Lines", "Gomti Nagar", "Raj Nagar", "Aminabad", "Chowk", "Indira Nagar",
    "Kakadeo", "Sigra", "Rambagh", "Sikandra", "Kavi Nagar", "Shastri Nagar",
    "Lal Bangla", "Shyam Nagar", "Kalyanpur", "Kamla Nagar", "GT Road", "Alambagh", 
    "Cantt Area", "Shahganj", "Tajganj", "Ashiyana", "Charbagh", "Model Town",
    "Mahanagar", "Hazratganj", "Aliganj", "Vikas Nagar", "Jankipuram", "Chinhat",
    "Nirala Nagar", "Aashiana", "Sarvodaya Nagar", "Kidwai Nagar", "Swaroop Nagar",
    "Kalyanpur", "Shyam Nagar", "Vijay Nagar", "Nehru Nagar", "Saket Nagar", "Keshav Nagar"
]

streets = [
    "Mahatma Gandhi Road", "Station Road", "Mall Road", "Nehru Marg", "Subhash Chauraha", 
    "Vivekananda Path", "Rajendra Nagar Road", "University Road", "Ravindrapuri Road", 
    "Shivaji Marg", "Tagore Road", "Shastri Marg", "Ramghat Road", "Jawahar Road",
    "Tilak Road", "Gandhi Chowk", "Ambedkar Road", "Patel Marg", "Nehru Road",
    "Lal Bahadur Shastri Road", "Vikas Marg", "Rajpath", "Ashok Marg", "Sardar Patel Road"
]

landmarks = [
    "Near Railway Station", "Opposite City Mall", "Behind Post Office", "Next to Central Park",
    "Close to Bus Stand", "Adjacent to Police Station", "Near Main Market", "Opposite Hospital",
    "Behind Govt. School", "Near Metro Station", "Next to Temple", "Near District Court",
    "Near University", "Opposite Shopping Complex", "Next to Community Center", "Near Stadium",
    "Close to Airport", "Adjacent to Fire Station", "Near Industrial Area", "Opposite Bank"
]

addresses = []

for _ in range(500):
    city, pincode = random.choice(cities)
    locality = random.choice(localities)
    street = random.choice(streets)
    landmark = random.choice(landmarks)
    house_no = f"{random.randint(1, 500)}, {random.choice(['Apt.', 'Flat', 'House', 'Villa', 'Bungalow', 'Cottage'])} {random.randint(1, 30)}"
    
    address = {
        "House No / Apt": house_no,
        "Street Name": street,
        "Landmark": landmark,
        "Locality / Area": locality,
        "City / District": city,
        "State": "Uttar Pradesh",
        "Pincode": pincode
    }
    
    addresses.append(address)

# Create DataFrame and Save to CSV
df = pd.DataFrame(addresses)
file_path = "addr.csv"
df.to_csv(file_path, index=False)

file_path