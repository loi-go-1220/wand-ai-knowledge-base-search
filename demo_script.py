#!/usr/bin/env python3
"""
Demo script for AI Knowledge Base System
Perfect for recording a demo video or live presentation
"""

import requests
import json
import time
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(title):
    """Print a nice header for demo sections"""
    print("\n" + "="*60)
    print(f"🎬 {title}")
    print("="*60)

def print_step(step, description):
    """Print demo step"""
    print(f"\n📍 Step {step}: {description}")
    print("-" * 40)

def demo_health_check():
    """Demo: System health and capabilities"""
    print_header("DEMO: System Health & Capabilities")
    
    print_step(1, "Check System Health")
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    
    print("✅ System Status:")
    print(f"   • Status: {data['status']}")
    print(f"   • OpenAI Configured: {data['openai_configured']}")
    print(f"   • Documents: {data['storage_stats']['total_documents']}")
    print(f"   • Chunks: {data['storage_stats']['total_chunks']}")
    print(f"   • Available Endpoints: {len(data['endpoints'])}")

def demo_document_upload():
    """Demo: Document upload and processing"""
    print_header("DEMO: Document Upload & Processing")
    
    # Upload AI basics document
    print_step(1, "Upload AI Fundamentals Document")
    with open('test_data/ai_basics.txt', 'rb') as f:
        files = {'file': ('ai_basics.txt', f, 'text/plain')}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Upload Successful:")
        print(f"   • Filename: {data['filename']}")
        print(f"   • Document ID: {data['document_id'][:8]}...")
        print(f"   • Chunks Created: {data['chunks_created']}")
        print(f"   • Content Length: {data['content_length']:,} characters")
    
    # Upload cloud computing document
    print_step(2, "Upload Cloud Computing Document")
    with open('test_data/cloud_computing.txt', 'rb') as f:
        files = {'file': ('cloud_computing.txt', f, 'text/plain')}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Upload Successful:")
        print(f"   • Filename: {data['filename']}")
        print(f"   • Chunks Created: {data['chunks_created']}")
    
    # List all documents
    print_step(3, "View All Documents")
    response = requests.get(f"{BASE_URL}/documents")
    data = response.json()
    
    print(f"📚 Total Documents: {data['total']}")
    for doc in data['documents']:
        print(f"   • {doc['filename']} - {doc['chunks']} chunks")

def demo_semantic_search():
    """Demo: Semantic search capabilities"""
    print_header("DEMO: Semantic Search")
    
    search_queries = [
        ("What is machine learning?", "Basic ML concepts"),
        ("cloud computing benefits", "Cloud advantages"),
        ("neural networks deep learning", "Advanced AI topics"),
        ("scalability and flexibility", "System characteristics")
    ]
    
    for i, (query, description) in enumerate(search_queries, 1):
        print_step(i, f"Search: {description}")
        print(f"🔍 Query: '{query}'")
        
        payload = {"query": query, "limit": 2}
        response = requests.post(f"{BASE_URL}/search", json=payload)
        
        if response.status_code == 200:
            results = response.json()
            print(f"📊 Found {len(results)} results:")
            
            for j, result in enumerate(results, 1):
                score = result['score']
                source = result['document_filename']
                text_preview = result['chunk']['chunk_text'][:100] + "..."
                
                print(f"   {j}. Score: {score:.3f} | Source: {source}")
                print(f"      Preview: {text_preview}")
        
        time.sleep(1)  # Pause for demo effect

def demo_qa_system():
    """Demo: Question & Answer system"""
    print_header("DEMO: Question & Answer System")
    
    questions = [
        ("What are the three types of machine learning?", "ML fundamentals"),
        ("What are the main benefits of cloud computing?", "Cloud advantages"),
        ("How is deep learning different from traditional ML?", "AI comparison"),
        ("What are some applications of AI in healthcare?", "AI applications")
    ]
    
    for i, (question, description) in enumerate(questions, 1):
        print_step(i, f"Q&A: {description}")
        print(f"❓ Question: {question}")
        
        payload = {"question": question, "context_limit": 3}
        response = requests.post(f"{BASE_URL}/ask", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            answer = data['answer']
            confidence = data['confidence']
            sources = len(data['sources'])
            
            print(f"🤖 Answer (Confidence: {confidence:.3f}):")
            print(f"   {answer[:200]}...")
            print(f"📚 Based on {sources} source chunks")
        
        time.sleep(2)  # Pause for demo effect

def demo_completeness_check():
    """Demo: Knowledge base completeness analysis"""
    print_header("DEMO: Knowledge Base Analysis")
    
    print_step(1, "Analyze Knowledge Base Completeness")
    response = requests.get(f"{BASE_URL}/completeness")
    
    if response.status_code == 200:
        data = response.json()
        analysis = data['analysis']
        suggestions = data['suggested_questions']
        
        print("📊 Knowledge Base Analysis:")
        print(f"   • Status: {analysis['status']}")
        print(f"   • Total Documents: {analysis['statistics']['total_documents']}")
        print(f"   • Total Chunks: {analysis['statistics']['total_chunks']}")
        print(f"   • Completeness Score: {analysis['completeness_score']}/1.0")
        
        print("\n🎯 Top Topics Covered:")
        for topic, count in list(analysis['topic_coverage'].items())[:5]:
            print(f"   • {topic}: {count} mentions")
        
        print("\n💡 Improvement Suggestions:")
        for suggestion in analysis['suggestions'][:3]:
            print(f"   • {suggestion}")
        
        print("\n❓ Suggested Questions to Test:")
        for question in suggestions[:3]:
            print(f"   • {question}")

def demo_architecture_overview():
    """Demo: System architecture explanation"""
    print_header("DEMO: System Architecture")
    
    print("🏗️  AI Knowledge Base Architecture:")
    print("""
    ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
    │   FastAPI App   │────│ Document         │────│   OpenAI API    │
    │   (REST API)    │    │ Processor        │    │  (Embeddings)   │
    └─────────────────┘    └──────────────────┘    └─────────────────┘
             │                       │                       │
             │              ┌──────────────────┐             │
             └──────────────│  In-Memory       │─────────────┘
                            │  Vector Storage  │
                            └──────────────────┘
                                     │
                            ┌──────────────────┐
                            │   Q&A Service    │
                            │   (GPT-4)        │
                            └──────────────────┘
    """)
    
    print("🔧 Key Components:")
    print("   • Document Processor: Intelligent chunking (paragraphs vs lines)")
    print("   • Vector Storage: In-memory cosine similarity search")
    print("   • Q&A Service: Context retrieval + GPT-4 generation")
    print("   • Completeness Checker: Knowledge gap analysis")
    
    print("\n⚡ Performance Features:")
    print("   • Batch embedding generation")
    print("   • Automatic content type detection")
    print("   • Comprehensive error handling")
    print("   • FastAPI async support")

def main():
    """Run the complete demo"""
    print("🎬 AI KNOWLEDGE BASE SYSTEM - LIVE DEMO")
    print("=" * 60)
    print("Built for Wand AI Backend Engineer Technical Assessment")
    print(f"Demo Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            raise Exception("Server not healthy")
    except:
        print("\n❌ ERROR: Server not running!")
        print("Please start the server with: python main.py")
        return
    
    # Run demo sections
    demo_health_check()
    demo_document_upload()
    demo_semantic_search()
    demo_qa_system()
    demo_completeness_check()
    demo_architecture_overview()
    
    print_header("DEMO COMPLETE")
    print("🎉 All features demonstrated successfully!")
    print("\n🌐 Try the interactive API docs: http://localhost:8000/docs")
    print("📚 Full documentation: README.md")
    print("🔗 GitHub repository: [Your GitHub URL]")
    
    print("\n" + "="*60)
    print("Thank you for watching the AI Knowledge Base demo!")
    print("Questions? Contact: [Your Email]")
    print("="*60)

if __name__ == "__main__":
    main()
