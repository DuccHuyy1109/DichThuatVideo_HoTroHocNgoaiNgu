"""
Quiz Generator
Tạo quiz tự động từ nội dung video
"""
import logging
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=Config.OPENAI_API_KEY)


def generate_quiz_from_transcript(transcript_segments, num_questions=10):
    """
    Tạo quiz từ transcript
    
    Args:
        transcript_segments: List các segments đã dịch
        num_questions: Số câu hỏi cần tạo
    
    Returns:
        tuple: (success: bool, quizzes: list, message: str)
    """
    try:
        if not transcript_segments:
            return False, None, "Không có transcript"
        
        # Tạo context từ segments
        context = create_context_from_segments(transcript_segments)
        
        # Tạo prompt
        prompt = create_quiz_prompt(context, num_questions)
        
        logger.info(f"Đang tạo {num_questions} câu quiz...")
        
        # Gọi GPT-4o
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là chuyên gia tạo câu hỏi trắc nghiệm cho học ngoại ngữ. Tạo các câu hỏi chất lượng cao, có độ khó phù hợp."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        # Parse kết quả
        quiz_text = response.choices[0].message.content.strip()
        quizzes = parse_quiz_response(quiz_text)
        
        logger.info(f"Đã tạo {len(quizzes)} câu quiz")
        
        return True, quizzes, "Tạo quiz thành công"
        
    except Exception as e:
        logger.error(f"Lỗi khi tạo quiz: {str(e)}")
        return False, None, f"Lỗi: {str(e)}"


def create_context_from_segments(segments, max_segments=50):
    """
    Tạo context từ segments để tạo quiz
    
    Args:
        segments: List segments
        max_segments: Số segments tối đa
    
    Returns:
        str: Context text
    """
    # Chọn segments quan trọng (có translation)
    important_segments = [
        seg for seg in segments 
        if 'translation' in seg and seg['translation']
    ][:max_segments]
    
    context_parts = []
    for seg in important_segments:
        text = seg.get('text', '')
        translation = seg.get('translation', '')
        if text and translation:
            context_parts.append(f"{text} ({translation})")
    
    return "\n".join(context_parts)


def create_quiz_prompt(context, num_questions):
    """
    Tạo prompt cho GPT để tạo quiz
    
    Args:
        context: Nội dung video
        num_questions: Số câu hỏi
    
    Returns:
        str: Prompt
    """
    prompt = f"""Dựa trên nội dung video sau, hãy tạo {num_questions} câu hỏi trắc nghiệm để kiểm tra hiểu biết của người học.

Nội dung video:
{context}

Yêu cầu:
1. Tạo {num_questions} câu hỏi chất lượng cao
2. Mỗi câu hỏi có 4 đáp án (A, B, C, D)
3. Câu hỏi phải liên quan đến từ vựng, ngữ pháp hoặc nội dung trong video
4. Độ khó: 40% dễ, 40% trung bình, 20% khó
5. Kèm giải thích ngắn gọn cho đáp án đúng

Format trả về (QUAN TRỌNG - phải đúng format này):
---
QUESTION: [Câu hỏi]
A: [Đáp án A]
B: [Đáp án B]
C: [Đáp án C]
D: [Đáp án D]
CORRECT: [A/B/C/D]
EXPLANATION: [Giải thích ngắn]
DIFFICULTY: [easy/medium/hard]
---

Chỉ trả về các câu hỏi theo format trên, không thêm text khác."""

    return prompt


def parse_quiz_response(quiz_text):
    """
    Parse response từ GPT thành list quizzes
    
    Args:
        quiz_text: Text response từ GPT
    
    Returns:
        list: Danh sách quiz dictionaries
    """
    quizzes = []
    
    # Split by separator
    quiz_blocks = quiz_text.split('---')
    
    for block in quiz_blocks:
        block = block.strip()
        if not block:
            continue
        
        quiz = parse_single_quiz(block)
        if quiz:
            quizzes.append(quiz)
    
    return quizzes


def parse_single_quiz(block):
    """
    Parse một quiz block
    
    Args:
        block: Text của một quiz
    
    Returns:
        dict: Quiz data
    """
    try:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        
        quiz = {
            'question': '',
            'options': {},
            'correct_answer': '',
            'explanation': '',
            'difficulty': 'medium'
        }
        
        for line in lines:
            if line.startswith('QUESTION:'):
                quiz['question'] = line.replace('QUESTION:', '').strip()
            elif line.startswith('A:'):
                quiz['options']['A'] = line.replace('A:', '').strip()
            elif line.startswith('B:'):
                quiz['options']['B'] = line.replace('B:', '').strip()
            elif line.startswith('C:'):
                quiz['options']['C'] = line.replace('C:', '').strip()
            elif line.startswith('D:'):
                quiz['options']['D'] = line.replace('D:', '').strip()
            elif line.startswith('CORRECT:'):
                quiz['correct_answer'] = line.replace('CORRECT:', '').strip()
            elif line.startswith('EXPLANATION:'):
                quiz['explanation'] = line.replace('EXPLANATION:', '').strip()
            elif line.startswith('DIFFICULTY:'):
                quiz['difficulty'] = line.replace('DIFFICULTY:', '').strip()
        
        # Validate
        if (quiz['question'] and 
            len(quiz['options']) == 4 and 
            quiz['correct_answer'] in quiz['options']):
            return quiz
        
        return None
        
    except Exception as e:
        logger.error(f"Lỗi parse quiz block: {str(e)}")
        return None


def save_quizzes_to_database(quizzes, video_id, db):
    """
    Lưu quizzes vào database
    
    Args:
        quizzes: List quiz dictionaries
        video_id: ID của video
        db: Database session
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        from database.models import Quiz
        
        for quiz_data in quizzes:
            quiz = Quiz(
                video_id=video_id,
                question=quiz_data['question'],
                correct_answer=quiz_data['options'][quiz_data['correct_answer']],
                wrong_answer_1=quiz_data['options'].get('A' if quiz_data['correct_answer'] != 'A' else 'B'),
                wrong_answer_2=quiz_data['options'].get('B' if quiz_data['correct_answer'] != 'B' else 'C'),
                wrong_answer_3=quiz_data['options'].get('C' if quiz_data['correct_answer'] != 'C' else 'D'),
                explanation=quiz_data.get('explanation', ''),
                difficulty_level=quiz_data.get('difficulty', 'medium')
            )
            
            db.session.add(quiz)
        
        db.session.commit()
        
        logger.info(f"Đã lưu {len(quizzes)} quiz vào database")
        
        return True, "Lưu quiz thành công"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Lỗi lưu quiz: {str(e)}")
        return False, f"Lỗi: {str(e)}"