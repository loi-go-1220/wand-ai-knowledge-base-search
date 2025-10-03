"""
Completeness checker - analyze knowledge gaps in the database
This addresses the "completeness check" requirement from the challenge
"""

from typing import List, Dict, Any
from collections import Counter
import re

from .storage import storage
from .models import SearchResult

class CompletenessChecker:
    """Analyzes the knowledge base for gaps and coverage"""
    
    def __init__(self):
        self.common_question_patterns = [
            "what is", "how to", "why does", "when should", "where can",
            "who is", "which one", "how much", "how many", "what are"
        ]
    
    def analyze_coverage(self) -> Dict[str, Any]:
        """
        Analyze the current knowledge base coverage
        """
        stats = storage.get_stats()
        documents = storage.list_documents()
        
        if not documents:
            return {
                "status": "empty",
                "message": "No documents in knowledge base",
                "suggestions": ["Upload documents to begin analysis"]
            }
        
        # Analyze document types and topics
        file_types = Counter()
        total_content_length = 0
        topics_mentioned = []
        
        for doc in documents:
            # File type analysis
            ext = doc.filename.split('.')[-1].lower() if '.' in doc.filename else 'unknown'
            file_types[ext] += 1
            
            # Content analysis
            total_content_length += len(doc.content)
            
            # Simple topic extraction (look for common technical terms)
            content_lower = doc.content.lower()
            tech_terms = [
                'ai', 'artificial intelligence', 'machine learning', 'deep learning',
                'cloud', 'computing', 'database', 'api', 'software', 'system',
                'algorithm', 'data', 'model', 'training', 'neural network'
            ]
            
            for term in tech_terms:
                if term in content_lower:
                    topics_mentioned.append(term)
        
        topic_coverage = Counter(topics_mentioned)
        
        # Generate suggestions
        suggestions = []
        
        if stats['total_documents'] < 5:
            suggestions.append("Consider adding more documents for better coverage")
        
        if len(topic_coverage) < 3:
            suggestions.append("Knowledge base seems narrow - consider adding diverse topics")
        
        if total_content_length < 5000:
            suggestions.append("Content volume is low - add more detailed documents")
        
        # Check for common gaps
        common_gaps = self._identify_common_gaps(documents)
        suggestions.extend(common_gaps)
        
        return {
            "status": "analyzed",
            "statistics": {
                "total_documents": stats['total_documents'],
                "total_chunks": stats['total_chunks'],
                "total_content_length": total_content_length,
                "avg_content_per_doc": total_content_length // max(stats['total_documents'], 1)
            },
            "file_types": dict(file_types),
            "topic_coverage": dict(topic_coverage.most_common(10)),
            "suggestions": suggestions,
            "completeness_score": self._calculate_completeness_score(stats, topic_coverage, total_content_length)
        }
    
    def _identify_common_gaps(self, documents: List) -> List[str]:
        """Identify common knowledge gaps"""
        gaps = []
        
        # Check for missing fundamental topics
        all_content = " ".join([doc.content.lower() for doc in documents])
        
        fundamental_topics = {
            "definitions": ["definition", "what is", "meaning"],
            "procedures": ["how to", "steps", "process", "procedure"],
            "examples": ["example", "instance", "case study", "sample"],
            "troubleshooting": ["error", "problem", "issue", "fix", "solve"]
        }
        
        for topic_type, keywords in fundamental_topics.items():
            if not any(keyword in all_content for keyword in keywords):
                gaps.append(f"Missing {topic_type} - consider adding content with {', '.join(keywords[:2])}")
        
        return gaps[:3]  # Limit to top 3 gaps
    
    def _calculate_completeness_score(self, stats: Dict, topic_coverage: Counter, content_length: int) -> float:
        """Calculate a simple completeness score (0-1)"""
        score = 0.0
        
        # Document count factor (up to 0.3)
        doc_factor = min(stats['total_documents'] / 10, 0.3)
        score += doc_factor
        
        # Content length factor (up to 0.3)
        content_factor = min(content_length / 20000, 0.3)
        score += content_factor
        
        # Topic diversity factor (up to 0.4)
        topic_factor = min(len(topic_coverage) / 10, 0.4)
        score += topic_factor
        
        return round(score, 2)
    
    def suggest_questions(self, limit: int = 5) -> List[str]:
        """
        Suggest questions that might reveal knowledge gaps
        """
        documents = storage.list_documents()
        
        if not documents:
            return ["What topics should be covered in this knowledge base?"]
        
        # Generate questions based on existing content
        suggestions = []
        
        # Generic questions
        suggestions.extend([
            "What are the main concepts covered in the knowledge base?",
            "How do the different topics relate to each other?",
            "What are some practical applications of these concepts?",
            "What are common challenges or problems in this domain?",
            "What are the latest developments or trends?"
        ])
        
        return suggestions[:limit]
