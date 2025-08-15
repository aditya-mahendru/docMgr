#!/usr/bin/env python3
"""
Sample Data Setup Script for DocMgr

This script populates the DocMgr system with sample documents and data
for testing and demonstration purposes.

Usage:
    python setup_sample_data.py
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.document import Document
from repository.sqlDB import DatabaseManager
from repository.vector_pipeline import VectorPipeline

class SampleDataSetup:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.db_manager = DatabaseManager()
        self.vector_pipeline = VectorPipeline()
        
    def create_sample_text_files(self):
        """Create sample text files with various content"""
        sample_files = {
            "AI_Concepts.txt": """
Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that work and react like humans. 

Key Concepts:
1. Machine Learning: Algorithms that allow computers to learn from data
2. Deep Learning: Neural networks with multiple layers for complex pattern recognition
3. Natural Language Processing: Understanding and generating human language
4. Computer Vision: Interpreting and analyzing visual information
5. Robotics: Physical systems that can interact with the environment

Applications:
- Virtual assistants (Siri, Alexa)
- Recommendation systems (Netflix, Amazon)
- Autonomous vehicles
- Medical diagnosis
- Financial trading
- Content generation
            """,
            
            "Machine_Learning_Basics.txt": """
Machine Learning is a subset of AI that focuses on algorithms and statistical models that enable computers to improve their performance on a specific task through experience.

Types of Machine Learning:
1. Supervised Learning: Learning from labeled examples
2. Unsupervised Learning: Finding patterns in unlabeled data
3. Reinforcement Learning: Learning through trial and error with rewards

Popular Algorithms:
- Linear Regression
- Decision Trees
- Random Forests
- Support Vector Machines
- Neural Networks
- K-Means Clustering

Real-world Examples:
- Email spam detection
- Credit card fraud detection
- Product recommendations
- Image classification
- Speech recognition
            """,
            
            "Data_Science_Overview.txt": """
Data Science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data.

Data Science Process:
1. Data Collection: Gathering data from various sources
2. Data Cleaning: Removing errors and inconsistencies
3. Data Exploration: Understanding patterns and relationships
4. Feature Engineering: Creating relevant variables
5. Model Building: Developing predictive models
6. Model Evaluation: Assessing model performance
7. Deployment: Implementing models in production

Tools and Technologies:
- Python (pandas, numpy, scikit-learn)
- R programming language
- SQL databases
- Big data platforms (Hadoop, Spark)
- Visualization tools (Tableau, Power BI)
- Cloud platforms (AWS, Azure, GCP)

Career Paths:
- Data Analyst
- Data Scientist
- Machine Learning Engineer
- Data Engineer
- Business Intelligence Analyst
            """,
            
            "Python_Programming.txt": """
Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in data science, web development, automation, and more.

Python Features:
- Simple and readable syntax
- Extensive standard library
- Cross-platform compatibility
- Strong community support
- Multiple programming paradigms

Popular Libraries:
- Data Science: pandas, numpy, matplotlib, seaborn
- Web Development: Django, Flask, FastAPI
- Machine Learning: scikit-learn, TensorFlow, PyTorch
- Automation: requests, beautifulsoup4, selenium
- GUI: tkinter, PyQt, Kivy

Best Practices:
- Use meaningful variable names
- Write docstrings and comments
- Follow PEP 8 style guide
- Use virtual environments
- Write unit tests
- Handle exceptions properly

Example Code:
```python
def calculate_fibonacci(n):
    '''Calculate the nth Fibonacci number'''
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"F({i}) = {calculate_fibonacci(i)}")
```
            """,
            
            "Web_Development.txt": """
Web Development involves creating websites and web applications that run on the internet. It encompasses both frontend and backend development.

Frontend Development:
- HTML: Structure and content
- CSS: Styling and layout
- JavaScript: Interactivity and behavior
- Frameworks: React, Vue, Angular
- CSS Frameworks: Bootstrap, Tailwind CSS

Backend Development:
- Server-side languages: Python, Node.js, Java, C#
- Web frameworks: Django, Flask, Express, Spring
- Databases: MySQL, PostgreSQL, MongoDB, Redis
- APIs: REST, GraphQL, gRPC
- Authentication: JWT, OAuth, sessions

Full-Stack Development:
- Understanding both frontend and backend
- Database design and management
- API development and integration
- Deployment and DevOps
- Performance optimization
- Security best practices

Modern Web Technologies:
- Progressive Web Apps (PWAs)
- Single Page Applications (SPAs)
- Server-Side Rendering (SSR)
- Static Site Generators (SSGs)
- Microservices architecture
- Containerization (Docker)
            """
        }
        
        print("📝 Creating sample text files...")
        
        for filename, content in sample_files.items():
            file_path = Path("uploads") / filename
            file_path.parent.mkdir(exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            
            print(f"  ✅ Created {filename}")
        
        return list(sample_files.keys())
    
    def upload_sample_files(self, filenames):
        """Upload sample files to the DocMgr system via API"""
        print(f"\n📤 Uploading {len(filenames)} sample files...")
        
        uploaded_count = 0
        for filename in filenames:
            try:
                file_path = Path("uploads") / filename
                
                if not file_path.exists():
                    print(f"  ❌ File not found: {filename}")
                    continue
                
                # Upload file via API
                with open(file_path, 'rb') as f:
                    files = {'file': (filename, f, 'text/plain')}
                    data = {'description': f'Sample {filename} for testing'}
                    
                    response = requests.post(
                        f"{self.base_url}/api/documents/upload",
                        files=files,
                        data=data
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    doc_id = result.get('id')
                    print(f"  ✅ Uploaded {filename} (ID: {doc_id})")
                    uploaded_count += 1
                else:
                    print(f"  ❌ Failed to upload {filename}: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Error uploading {filename}: {str(e)}")
        
        print(f"\n📊 Upload Summary: {uploaded_count}/{len(filenames)} files uploaded successfully")
        return uploaded_count
    
    def create_sample_database_entries(self):
        """Create sample database entries for testing"""
        print("\n🗄️ Creating sample database entries...")
        
        try:
            # Initialize database
            self.db_manager.init_db()
            
            # Create sample documents table if it doesn't exist
            self.db_manager.create_tables()
            
            print("  ✅ Database initialized successfully")
            
        except Exception as e:
            print(f"  ❌ Database initialization failed: {str(e)}")
            return False
        
        return True
    
    def test_vector_pipeline(self):
        """Test the vector pipeline with sample data"""
        print("\n🧠 Testing vector pipeline...")
        
        try:
            # Test vector pipeline initialization
            self.vector_pipeline.initialize_collection()
            print("  ✅ Vector pipeline initialized")
            
            # Get vector stats
            stats = self.vector_pipeline.get_collection_stats()
            print(f"  📊 Vector collection stats: {stats}")
            
        except Exception as e:
            print(f"  ❌ Vector pipeline test failed: {str(e)}")
            return False
        
        return True
    
    def run_health_checks(self):
        """Run health checks on the DocMgr system"""
        print("\n🏥 Running health checks...")
        
        try:
            # Check API health
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("  ✅ API is responding")
            else:
                print(f"  ❌ API health check failed: {response.status_code}")
                return False
            
            # Check documents endpoint
            response = requests.get(f"{self.base_url}/api/documents")
            if response.status_code == 200:
                docs = response.json()
                print(f"  📚 Found {len(docs)} documents in system")
            else:
                print(f"  ❌ Documents endpoint failed: {response.status_code}")
                return False
            
            # Check vector stats
            response = requests.get(f"{self.base_url}/api/vector/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"  🧠 Vector stats: {stats}")
            else:
                print(f"  ❌ Vector stats endpoint failed: {response.status_code}")
                return False
            
        except Exception as e:
            print(f"  ❌ Health check failed: {str(e)}")
            return False
        
        return True
    
    def setup(self):
        """Run the complete setup process"""
        print("🚀 Starting DocMgr Sample Data Setup...")
        print("=" * 50)
        
        # Check if DocMgr is running
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code != 200:
                print(f"❌ DocMgr is not running at {self.base_url}")
                print("Please start DocMgr first: uvicorn app:app --reload --host 0.0.0.0 --port 8000")
                return False
        except requests.exceptions.RequestException:
            print(f"❌ Cannot connect to DocMgr at {self.base_url}")
            print("Please start DocMgr first: uvicorn app:app --reload --host 0.0.0.0 --port 8000")
            return False
        
        # Run setup steps
        success = True
        
        # Create sample files
        filenames = self.create_sample_text_files()
        
        # Initialize database
        if not self.create_sample_database_entries():
            success = False
        
        # Test vector pipeline
        if not self.test_vector_pipeline():
            success = False
        
        # Upload files
        uploaded_count = self.upload_sample_files(filenames)
        
        # Run health checks
        if not self.run_health_checks():
            success = False
        
        # Summary
        print("\n" + "=" * 50)
        if success:
            print("🎉 Setup completed successfully!")
            print(f"📁 {len(filenames)} sample files created")
            print(f"📤 {uploaded_count} files uploaded to DocMgr")
            print("\nYou can now:")
            print("1. Test the API endpoints")
            print("2. Try semantic search queries")
            print("3. Use the chatbot interface")
            print("4. Explore document chunks and embeddings")
        else:
            print("⚠️ Setup completed with some issues")
            print("Please check the error messages above")
        
        return success

def main():
    """Main entry point"""
    setup = SampleDataSetup()
    
    try:
        success = setup.setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
