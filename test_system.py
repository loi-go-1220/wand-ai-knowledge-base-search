#!/usr/bin/env python3
"""
Quick system test to validate everything works
This is the kind of script a dev writes to test their system
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if the server is running"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server healthy, OpenAI configured: {data['openai_configured']}")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Can't connect to server: {e}")
        print("   Make sure to run: python main.py")
        return False

def upload_test_documents():
    """Upload test documents"""
    print("\n📤 Uploading test documents...")
    
    test_files = ["test_data/ai_basics.txt", "test_data/cloud_computing.txt"]
    uploaded = []
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"   ⚠️  File not found: {file_path}")
            continue
            
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'text/plain')}
                response = requests.post(f"{BASE_URL}/upload", files=files)
                
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Uploaded {data['filename']} - {data['chunks_created']} chunks")
                uploaded.append(data['filename'])
            else:
                print(f"   ❌ Upload failed for {file_path}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error uploading {file_path}: {e}")
    
    return uploaded

def test_search():
    """Test semantic search"""
    print("\n🔍 Testing semantic search...")
    
    test_queries = [
        "What is machine learning?",
        "Cloud computing benefits",
        "Deep learning applications",
        "IaaS vs PaaS vs SaaS"
    ]
    
    for query in test_queries:
        try:
            payload = {"query": query, "limit": 2}
            response = requests.post(f"{BASE_URL}/search", json=payload)
            
            if response.status_code == 200:
                results = response.json()
                print(f"   ✅ Query: '{query}' - Found {len(results)} results")
                if results:
                    best_result = results[0]
                    print(f"      Best match (score: {best_result['score']:.3f}): {best_result['chunk']['chunk_text'][:100]}...")
            else:
                print(f"   ❌ Search failed for '{query}': {response.text}")
                
        except Exception as e:
            print(f"   ❌ Search error for '{query}': {e}")

def test_qa():
    """Test Q&A functionality"""
    print("\n🤔 Testing Q&A system...")
    
    test_questions = [
        "What are the three types of machine learning?",
        "What are the benefits of cloud computing?",
        "How is deep learning different from traditional machine learning?",
        "What is the difference between IaaS and SaaS?"
    ]
    
    for question in test_questions:
        try:
            payload = {"question": question, "context_limit": 3}
            response = requests.post(f"{BASE_URL}/ask", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Q: {question}")
                print(f"      A: {data['answer'][:200]}...")
                print(f"      Confidence: {data['confidence']:.3f}, Sources: {len(data['sources'])}")
            else:
                print(f"   ❌ Q&A failed for '{question}': {response.text}")
                
        except Exception as e:
            print(f"   ❌ Q&A error for '{question}': {e}")

def main():
    """Run all tests"""
    print("🧪 Testing AI Knowledge Base System")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server not running. Start with: python main.py")
        return
    
    # Test 2: Upload documents
    uploaded = upload_test_documents()
    if not uploaded:
        print("\n❌ No documents uploaded. Can't test search/Q&A.")
        return
    
    # Give the system a moment to process
    print("\n⏳ Waiting for processing to complete...")
    time.sleep(2)
    
    # Test 3: Search
    test_search()
    
    # Test 4: Q&A
    test_qa()
    
    print("\n" + "=" * 50)
    print("✨ System test complete!")
    print(f"📊 Documents uploaded: {len(uploaded)}")
    print("🌐 Try the interactive docs at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
