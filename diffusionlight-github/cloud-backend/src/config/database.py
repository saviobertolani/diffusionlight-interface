import os
from flask_sqlalchemy import SQLAlchemy
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# SQLAlchemy instance
db = SQLAlchemy()

# Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

def init_database(app):
        """Initialize database with Flask app"""

    # Configure PostgreSQL for Supabase
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
                    # Fallback to SQLite for local development
                    database_url =     
    # Log database configuration
    if 'postgresql' in database_url:
        print(f"✅ Using PostgreSQL database: {database_url[:50]}...")
    else:
        print("⚠️ Using SQLite fallback database")

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 20,
            'max_overflow': 0
        }

    # Initialize SQLAlchemy with app
        db.init_app(app)

    # Create tables
        with app.app_context():
                    db.create_all(try:
                db.create_all()
                print("✅ Database tables created successfully")
            except Exception as e:
                print(f"⚠️ Database initialization warning: {e}")
                # Continue without database for resilience

        return db
