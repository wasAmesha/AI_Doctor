const { MongoClient } = require('mongodb');

async function testConnection() {
  const uri = process.env.MONGODB_URI || 'mongodb+srv://nethmi:3iwR4xsrpxkDIU2B@cluster0.pr0qmcr.mongodb.net/ai-doctor-chatbot?retryWrites=true&w=majority';
  
  console.log('Testing connection to:', uri.replace(/:[^:]*@/, ':****@'));
  
  const client = new MongoClient(uri, {
    serverSelectionTimeoutMS: 5000,
    connectTimeoutMS: 5000,
  });

  try {
    await client.connect();
    console.log('✅ Successfully connected to MongoDB');
    
    // Test database operations
    const db = client.db('ai-doctor-chatbot');
    const collections = await db.listCollections().toArray();
    console.log('📊 Collections:', collections.map(c => c.name));
    
    await client.close();
    console.log('✅ Connection test completed successfully');
    
  } catch (error) {
    console.error('❌ Connection failed:', error.message);
    
    if (error.code === 'ENOTFOUND') {
      console.log('\n💡 Troubleshooting tips:');
      console.log('1. Check your internet connection');
      console.log('2. Verify your MongoDB Atlas cluster is running');
      console.log('3. Check if your IP is whitelisted in MongoDB Atlas');
      console.log('4. Try using the standard connection string (without +srv)');
    }
    
    throw error;
  }
}

testConnection().catch(() => process.exit(1));