// MongoDB environment variables injected by Docker
var admin_username = 'flow';
var admin_password = 'flow';
var data_username = 'data';
var data_password = 'data';

// Create admin user with root and userAdminAnyDatabase roles
db = db.getSiblingDB('admin');  // Switch to the 'admin' database
print("Creating admin user...");
db.createUser({
  user: admin_username,         // Use the variable for the admin username
  pwd: admin_password,          // Use the variable for the admin password
  roles: [
    { role: "root", db: "admin" },              // Full admin access to all databases
    { role: "userAdminAnyDatabase", db: "admin" }  // Ability to manage users across all databases
  ]
});
print("Admin user created successfully.");

// Create data user with readWrite role on 'data' database
db = db.getSiblingDB('data');
print("Creating data user...");
db.createUser({
  user: data_username,       // Use the variable for the data username
  pwd: data_password,        // Use the variable for the data password
  roles: [{ role: 'readWrite', db: 'data' }]  // Read/Write access to the 'data' database
});
print("Data user created successfully.");

// Create collection in the data database
print("Creating 'datas' collection...");
db.createCollection('datas');  // Create the 'datas' collection
print("'datas' collection created successfully.");
