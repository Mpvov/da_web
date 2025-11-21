from app.ml_engine import predictor

# This is the connection string you provided
DB_CONNECTION = "mongodb+srv://minhquannguyendo0705_db_user:12345@cluster0.kgz4rtm.mongodb.net/?appName=Cluster0"

if __name__ == "__main__":
    print("--- Starting Batch Training Process for ALL Countries ---")
    print("This may take a minute depending on your connection...")
    
    # We call the function without specifying a country, so it fetches all of them
    predictor.train_model_from_db(connection_string=DB_CONNECTION)
    
    print("--- Process Complete ---")
    print("Restart your FastAPI server to use the new models.")