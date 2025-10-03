"""
Q&A Service using retrieved context and OpenAI
This is where we turn search results into actual answers
"""

from typing import List
from openai import OpenAI

from .models import QARequest, QAResponse, SearchResult
from .config import settings
from .storage import storage
from .document_processor import DocumentProcessor

class QAService:
    """Handles question answering using retrieved context"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.processor = DocumentProcessor()
    
    def answer_question(self, question: str, context_limit: int = 3) -> QAResponse:
        """
        Answer a question using retrieved context
        1. Search for relevant chunks
        2. Build context from top results  
        3. Generate answer using GPT-4
        """
        try:
            # Step 1: Get relevant context through search
            print(f"🤔 Answering question: {question}")
            
            # Generate embedding for the question
            question_embeddings = self.processor.generate_embeddings([question])
            
            if not question_embeddings or not question_embeddings[0]:
                return QAResponse(
                    answer="Sorry, I couldn't process your question. Please try again.",
                    sources=[],
                    confidence=0.0
                )
            
            # Search for relevant chunks
            search_results = storage.search_similar_chunks(
                question_embeddings[0], 
                limit=context_limit
            )
            
            if not search_results:
                return QAResponse(
                    answer="I don't have any relevant information to answer your question. Please upload some documents first.",
                    sources=[],
                    confidence=0.0
                )
            
            # Step 2: Build context from search results
            context_parts = []
            for i, result in enumerate(search_results):
                context_parts.append(f"[Source {i+1} from {result.document_filename}]:\n{result.chunk.chunk_text}")
            
            context = "\n\n".join(context_parts)
            
            # Step 3: Generate answer using GPT-4
            print(f"   Using {len(search_results)} context chunks")
            answer = self._generate_answer(question, context)
            
            # Calculate confidence based on search scores
            avg_score = sum(r.score for r in search_results) / len(search_results)
            confidence = min(avg_score, 1.0)  # Cap at 1.0
            
            print(f"✅ Answer generated (confidence: {confidence:.2f})")
            
            return QAResponse(
                answer=answer,
                sources=search_results,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"❌ Q&A failed: {e}")
            return QAResponse(
                answer=f"Sorry, I encountered an error while processing your question: {str(e)}",
                sources=[],
                confidence=0.0
            )
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using GPT-4 with retrieved context"""
        
        # Build the prompt
        prompt = f"""You are a helpful AI assistant that answers questions based on provided context.

Context:
{context}

Question: {question}

Instructions:
- Answer the question based ONLY on the provided context
- If the context doesn't contain enough information, say so
- Be concise but comprehensive
- Cite which sources you're using when relevant
- If you're not sure, express uncertainty

Answer:"""

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1  # Low temperature for more consistent answers
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"I encountered an error generating the answer: {str(e)}"
