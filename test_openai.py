import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("✅ OpenAI client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize OpenAI client: {e}")
    print("This might be a dependency version issue. Try upgrading openai and httpx.")
    exit(1)

def test_embedding():
    """Test basic embedding generation"""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="This is a test document for embedding generation."
        )
        
        embedding = response.data[0].embedding
        print(f"✅ Embedding generated successfully!")
        print(f"   Dimensions: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        
        return embedding
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return None

def test_chat():
    """Test basic chat completion"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Say hello in a professional way for a technical demo."}
            ],
            max_tokens=50
        )
        
        answer = response.choices[0].message.content
        print(f"✅ Chat completion successful!")
        print(f"   Response: {answer}")
        
        return answer
    except Exception as e:
        print(f"❌ Chat completion failed: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Testing OpenAI API connection...")
    print("=" * 50)
    
    print("\n1. Testing Embeddings:")
    test_embedding()
    
    print("\n2. Testing Chat Completion:")
    test_chat()
    
    print("\n" + "=" * 50)
    print("✨ API exploration complete!")
