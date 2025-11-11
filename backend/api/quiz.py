"""
Quiz API Routes - FIXED
Sửa lỗi: shuffle options và trả correct_answer index
"""
import logging
import random
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.models import Quiz, UserQuizResult, Video
from database.db_config import db
from middleware.auth_middleware import get_current_user
from utils.response_handler import success_response, error_response
from utils.constants import SUCCESS_QUIZ_SUBMITTED

logger = logging.getLogger(__name__)

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route('/<int:video_id>', methods=['GET'])
@jwt_required()
def get_quizzes(video_id):
    """
    API lấy danh sách quiz của video - FIXED
    """
    try:
        user = get_current_user()
        
        video = Video.query.filter_by(video_id=video_id, user_id=user.user_id).first()
        
        if not video:
            return jsonify(error_response(
                message='Không tìm thấy video',
                status_code=404
            )), 404
        
        quizzes = Quiz.query.filter_by(video_id=video_id).all()
        
        quizzes_data = []
        for quiz in quizzes:
            # ✅ FIX: Tạo options và shuffle
            options = [
                quiz.correct_answer,
                quiz.wrong_answer_1,
                quiz.wrong_answer_2,
                quiz.wrong_answer_3
            ]
            
            # Shuffle và lưu index của correct answer
            correct_answer_text = quiz.correct_answer
            random.shuffle(options)
            correct_index = options.index(correct_answer_text)
            
            quiz_dict = {
                'quiz_id': quiz.quiz_id,
                'video_id': quiz.video_id,
                'question': quiz.question,
                'options': options,
                'correct_answer': correct_index,  # ✅ Index của đáp án đúng
                'difficulty_level': quiz.difficulty_level,
                'explanation': quiz.explanation
            }
            
            quizzes_data.append(quiz_dict)
        
        return jsonify(success_response(
            message='Lấy danh sách quiz thành công',
            data={'quizzes': quizzes_data}
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API get_quizzes: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy quiz',
            status_code=500,
            error=str(e)
        )), 500


@quiz_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_quiz():
    """
    API nộp bài quiz
    
    Request body:
    {
        "quiz_id": int,
        "selected_answer": "string",
        "time_taken": int (seconds, optional)
    }
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data or 'quiz_id' not in data or 'selected_answer' not in data:
            return jsonify(error_response(
                message='Thiếu thông tin bắt buộc',
                status_code=400
            )), 400
        
        quiz_id = data['quiz_id']
        selected_answer = data['selected_answer']
        time_taken = data.get('time_taken')
        
        quiz = Quiz.query.get(quiz_id)
        
        if not quiz:
            return jsonify(error_response(
                message='Không tìm thấy quiz',
                status_code=404
            )), 404
        
        video = Video.query.filter_by(video_id=quiz.video_id, user_id=user.user_id).first()
        
        if not video:
            return jsonify(error_response(
                message='Không có quyền truy cập',
                status_code=403
            )), 403
        
        is_correct = (selected_answer == quiz.correct_answer)
        
        result = UserQuizResult(
            user_id=user.user_id,
            quiz_id=quiz_id,
            selected_answer=selected_answer,
            is_correct=is_correct,
            time_taken=time_taken
        )
        
        db.session.add(result)
        db.session.commit()
        
        return jsonify(success_response(
            message=SUCCESS_QUIZ_SUBMITTED,
            data={
                'result_id': result.result_id,
                'is_correct': is_correct,
                'correct_answer': quiz.correct_answer if not is_correct else None,
                'explanation': quiz.explanation
            }
        )), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Lỗi API submit_quiz: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi nộp bài quiz',
            status_code=500,
            error=str(e)
        )), 500


@quiz_bp.route('/results/<int:user_id>', methods=['GET'])
@jwt_required()
def get_quiz_results(user_id):
    """
    API lấy kết quả quiz của user
    """
    try:
        current_user = get_current_user()
        
        if current_user.user_id != user_id:
            return jsonify(error_response(
                message='Không có quyền truy cập',
                status_code=403
            )), 403
        
        video_id = request.args.get('video_id', None, type=int)
        
        query = UserQuizResult.query.filter_by(user_id=user_id)
        
        if video_id:
            query = query.join(Quiz).filter(Quiz.video_id == video_id)
        
        results = query.all()
        results_data = [result.to_dict() for result in results]
        
        total_questions = len(results_data)
        correct_answers = sum(1 for r in results_data if r['is_correct'])
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        return jsonify(success_response(
            message='Lấy kết quả quiz thành công',
            data={
                'results': results_data,
                'statistics': {
                    'total_questions': total_questions,
                    'correct_answers': correct_answers,
                    'accuracy': round(accuracy, 2)
                }
            }
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API get_quiz_results: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy kết quả quiz',
            status_code=500,
            error=str(e)
        )), 500