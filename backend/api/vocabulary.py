"""
Vocabulary API Routes - ULTIMATE COMPLETE VERSION
API cho quản lý từ vựng - Đầy đủ và hoàn chỉnh nhất

Features:
- ✅ Query vocabulary by video_id (not language)
- ✅ Full CRUD operations
- ✅ User personal vocabulary management
- ✅ Statistics and analytics
- ✅ Search and filter
- ✅ Proper error handling
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.models import Vocabulary, UserVocabulary, Video
from database.db_config import db
from middleware.auth_middleware import get_current_user
from utils.response_handler import success_response, error_response, paginated_response
from utils.constants import SUCCESS_VOCABULARY_SAVED

logger = logging.getLogger(__name__)

# Tạo Blueprint
vocabulary_bp = Blueprint('vocabulary', __name__)


@vocabulary_bp.route('/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video_vocabulary(video_id):
    """
    ✅ FIXED: Lấy vocabulary CỤ THỂ của video này
    
    Path params:
        video_id: ID của video
    
    Returns:
        200: Danh sách từ vựng của video
        404: Video không tồn tại
        
    Query by video_id (NOT language) để đảm bảo mỗi video có vocabulary riêng
    """
    try:
        user = get_current_user()
        
        # Kiểm tra video tồn tại và thuộc về user
        video = Video.query.filter_by(video_id=video_id, user_id=user.user_id).first()
        
        if not video:
            return jsonify(error_response(
                message='Không tìm thấy video',
                status_code=404
            )), 404
        
        # ✅ CRITICAL FIX: Query by video_id thay vì language
        vocabularies = Vocabulary.query.filter_by(video_id=video_id).all()
        
        # ❌ OLD WRONG WAY:
        # vocabularies = Vocabulary.query.filter_by(language=video.language_detected).limit(50).all()
        # → Lấy TẤT CẢ vocabulary cùng ngôn ngữ (WRONG!)
        
        vocabularies_data = [vocab.to_dict() for vocab in vocabularies]
        
        logger.info(f"✅ Found {len(vocabularies_data)} vocabularies for video {video_id}")
        
        return jsonify(success_response(
            message='Lấy từ vựng thành công',
            data={'vocabularies': vocabularies_data}
        )), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_video_vocabulary: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy từ vựng',
            status_code=500,
            error=str(e)
        )), 500


@vocabulary_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_vocabulary():
    """
    API lấy tất cả từ vựng trong hệ thống
    
    Query params:
        - page: Trang (default: 1)
        - per_page: Số từ mỗi trang (default: 20)
        - language: Lọc theo ngôn ngữ (optional)
        - search: Tìm kiếm từ (optional)
        - video_id: Lọc theo video (optional)
    
    Returns:
        200: Danh sách từ vựng với pagination
    """
    try:
        user = get_current_user()
        
        # Lấy params
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        language = request.args.get('language', None)
        search = request.args.get('search', None)
        video_id = request.args.get('video_id', None, type=int)
        
        # Query - Join với Video để chỉ lấy vocabulary của user
        query = db.session.query(Vocabulary).join(
            Video, Vocabulary.video_id == Video.video_id
        ).filter(Video.user_id == user.user_id)
        
        # Filters
        if language:
            query = query.filter(Vocabulary.language == language)
        
        if video_id:
            query = query.filter(Vocabulary.video_id == video_id)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                db.or_(
                    Vocabulary.word.like(search_pattern),
                    Vocabulary.translation.like(search_pattern)
                )
            )
        
        # Order by vocab_id desc
        query = query.order_by(Vocabulary.vocab_id.desc())
        
        # Pagination
        total_items = query.count()
        vocabularies = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Convert to dict
        vocabularies_data = [vocab.to_dict() for vocab in vocabularies]
        
        return jsonify(paginated_response(
            items=vocabularies_data,
            page=page,
            per_page=per_page,
            total_items=total_items,
            message='Lấy danh sách từ vựng thành công'
        )), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_all_vocabulary: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy danh sách từ vựng',
            status_code=500,
            error=str(e)
        )), 500


@vocabulary_bp.route('/save', methods=['POST'])
@jwt_required()
def save_vocabulary():
    """
    API lưu từ vựng vào danh sách cá nhân
    
    Request body:
    {
        "vocab_id": int,
        "video_id": int (optional)
    }
    
    Returns:
        201: Lưu thành công
        400: Từ vựng đã lưu hoặc thiếu thông tin
        404: Từ vựng không tồn tại
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data or 'vocab_id' not in data:
            return jsonify(error_response(
                message='Thiếu vocab_id',
                status_code=400
            )), 400
        
        vocab_id = data['vocab_id']
        video_id = data.get('video_id')
        
        # Kiểm tra vocab tồn tại
        vocab = Vocabulary.query.get(vocab_id)
        
        if not vocab:
            return jsonify(error_response(
                message='Không tìm thấy từ vựng',
                status_code=404
            )), 404
        
        # Kiểm tra đã lưu chưa
        existing = UserVocabulary.query.filter_by(
            user_id=user.user_id,
            vocab_id=vocab_id
        ).first()
        
        if existing:
            return jsonify(error_response(
                message='Từ vựng đã được lưu trước đó',
                status_code=400
            )), 400
        
        # Lưu từ vựng
        user_vocab = UserVocabulary(
            user_id=user.user_id,
            vocab_id=vocab_id,
            video_id=video_id or vocab.video_id,  # Use vocab's video_id if not provided
            learned_status='learning'
        )
        
        db.session.add(user_vocab)
        db.session.commit()
        
        logger.info(f"✅ User {user.user_id} saved vocabulary {vocab_id}")
        
        return jsonify(success_response(
            message=SUCCESS_VOCABULARY_SAVED,
            data={'user_vocabulary': user_vocab.to_dict()}
        )), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error in save_vocabulary: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lưu từ vựng',
            status_code=500,
            error=str(e)
        )), 500


@vocabulary_bp.route('/saved', methods=['GET'])
@jwt_required()
def get_saved_vocabulary():
    """
    API lấy danh sách từ vựng đã lưu của user
    
    Query params:
        - page: Trang (default: 1)
        - per_page: Số từ vựng mỗi trang (default: 20)
        - learned_status: Lọc theo trạng thái (optional: learning/learned/mastered)
        - language: Lọc theo ngôn ngữ (optional)
        - video_id: Lọc theo video (optional)
    
    Returns:
        200: Danh sách từ vựng đã lưu với pagination
    """
    try:
        user = get_current_user()
        
        # Lấy params
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        learned_status = request.args.get('learned_status', None)
        language = request.args.get('language', None)
        video_id = request.args.get('video_id', None, type=int)
        
        # Query
        query = UserVocabulary.query.filter_by(user_id=user.user_id)
        
        if learned_status:
            query = query.filter_by(learned_status=learned_status)
        
        if video_id:
            query = query.filter_by(video_id=video_id)
        
        # Order by saved_date desc
        query = query.order_by(UserVocabulary.saved_date.desc())
        
        # Pagination
        total_items = query.count()
        user_vocabs = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Convert to dict và join với Vocabulary
        vocabularies_data = []
        for user_vocab in user_vocabs:
            vocab = Vocabulary.query.get(user_vocab.vocab_id)
            if vocab:
                # Filter by language if specified
                if language and vocab.language != language:
                    continue
                
                vocab_data = vocab.to_dict()
                vocab_data['user_vocab_id'] = user_vocab.id
                vocab_data['learned_status'] = user_vocab.learned_status
                vocab_data['saved_date'] = user_vocab.saved_date.isoformat() if user_vocab.saved_date else None
                vocab_data['last_reviewed'] = user_vocab.last_reviewed.isoformat() if user_vocab.last_reviewed else None
                vocab_data['review_count'] = user_vocab.review_count
                vocabularies_data.append(vocab_data)
        
        return jsonify(paginated_response(
            items=vocabularies_data,
            page=page,
            per_page=per_page,
            total_items=len(vocabularies_data),  # Use filtered count
            message='Lấy danh sách từ vựng thành công'
        )), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_saved_vocabulary: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy từ vựng đã lưu',
            status_code=500,
            error=str(e)
        )), 500


@vocabulary_bp.route('/<int:user_vocab_id>', methods=['DELETE'])
@jwt_required()
def delete_vocabulary(user_vocab_id):
    """
    API xóa từ vựng khỏi danh sách cá nhân
    
    Path params:
        user_vocab_id: ID của user_vocabulary
    
    Returns:
        200: Xóa thành công
        404: Không tìm thấy từ vựng
    """
    try:
        user = get_current_user()
        
        # Tìm user vocabulary
        user_vocab = UserVocabulary.query.filter_by(
            id=user_vocab_id,
            user_id=user.user_id
        ).first()
        
        if not user_vocab:
            return jsonify(error_response(
                message='Không tìm thấy từ vựng',
                status_code=404
            )), 404
        
        # Xóa
        db.session.delete(user_vocab)
        db.session.commit()
        
        logger.info(f"✅ User {user.user_id} deleted vocabulary {user_vocab_id}")
        
        return jsonify(success_response(
            message='Xóa từ vựng thành công'
        )), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error in delete_vocabulary: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi xóa từ vựng',
            status_code=500,
            error=str(e)
        )), 500


@vocabulary_bp.route('/<int:user_vocab_id>/status', methods=['PUT'])
@jwt_required()
def update_vocabulary_status(user_vocab_id):
    """
    API cập nhật trạng thái học từ vựng
    
    Path params:
        user_vocab_id: ID của user_vocabulary
    
    Request body:
    {
        "learned_status": "learning" | "learned" | "mastered"
    }
    
    Returns:
        200: Cập nhật thành công
        400: Status không hợp lệ
        404: Không tìm thấy từ vựng
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data or 'learned_status' not in data:
            return jsonify(error_response(
                message='Thiếu learned_status',
                status_code=400
            )), 400
        
        learned_status = data['learned_status']
        
        # Validate status
        valid_statuses = ['learning', 'learned', 'mastered']
        if learned_status not in valid_statuses:
            return jsonify(error_response(
                message=f'Trạng thái không hợp lệ. Chỉ chấp nhận: {", ".join(valid_statuses)}',
                status_code=400
            )), 400
        
        # Tìm user vocabulary
        user_vocab = UserVocabulary.query.filter_by(
            id=user_vocab_id,
            user_id=user.user_id
        ).first()
        
        if not user_vocab:
            return jsonify(error_response(
                message='Không tìm thấy từ vựng',
                status_code=404
            )), 404
        
        # Cập nhật
        user_vocab.learned_status = learned_status
        user_vocab.review_count += 1
        
        from datetime import datetime
        user_vocab.last_reviewed = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"✅ User {user.user_id} updated vocabulary {user_vocab_id} to {learned_status}")
        
        return jsonify(success_response(
            message='Cập nhật trạng thái thành công',
            data={'user_vocabulary': user_vocab.to_dict()}
        )), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error in update_vocabulary_status: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi cập nhật trạng thái',
            status_code=500,
            error=str(e)
        )), 500


@vocabulary_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_vocabulary_stats():
    """
    API lấy thống kê từ vựng của user
    
    Returns:
        200: Thống kê từ vựng
        {
            "total": int,
            "learning": int,
            "learned": int,
            "mastered": int,
            "by_language": {
                "en": int,
                "ko": int,
                ...
            },
            "by_video": {
                "video_id": int,
                ...
            }
        }
    """
    try:
        user = get_current_user()
        
        # Tổng số từ đã lưu
        total = UserVocabulary.query.filter_by(user_id=user.user_id).count()
        
        # Theo trạng thái
        learning = UserVocabulary.query.filter_by(user_id=user.user_id, learned_status='learning').count()
        learned = UserVocabulary.query.filter_by(user_id=user.user_id, learned_status='learned').count()
        mastered = UserVocabulary.query.filter_by(user_id=user.user_id, learned_status='mastered').count()
        
        # Theo ngôn ngữ
        user_vocabs = UserVocabulary.query.filter_by(user_id=user.user_id).all()
        by_language = {}
        by_video = {}
        
        for user_vocab in user_vocabs:
            vocab = Vocabulary.query.get(user_vocab.vocab_id)
            if vocab:
                # By language
                lang = vocab.language
                by_language[lang] = by_language.get(lang, 0) + 1
                
                # By video
                if vocab.video_id:
                    by_video[vocab.video_id] = by_video.get(vocab.video_id, 0) + 1
        
        stats = {
            'total': total,
            'learning': learning,
            'learned': learned,
            'mastered': mastered,
            'by_language': by_language,
            'by_video': by_video
        }
        
        return jsonify(success_response(
            message='Lấy thống kê thành công',
            data=stats
        )), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_vocabulary_stats: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy thống kê',
            status_code=500,
            error=str(e)
        )), 500


@vocabulary_bp.route('/detail/<int:vocab_id>', methods=['GET'])
@jwt_required()
def get_vocabulary_detail(vocab_id):
    """
    API lấy chi tiết một từ vựng
    
    Path params:
        vocab_id: ID của vocabulary
    
    Returns:
        200: Chi tiết từ vựng
        404: Không tìm thấy
    """
    try:
        user = get_current_user()
        
        # Lấy vocabulary
        vocab = Vocabulary.query.get(vocab_id)
        
        if not vocab:
            return jsonify(error_response(
                message='Không tìm thấy từ vựng',
                status_code=404
            )), 404
        
        vocab_data = vocab.to_dict()
        
        # Kiểm tra user đã lưu chưa
        user_vocab = UserVocabulary.query.filter_by(
            user_id=user.user_id,
            vocab_id=vocab_id
        ).first()
        
        if user_vocab:
            vocab_data['is_saved'] = True
            vocab_data['learned_status'] = user_vocab.learned_status
            vocab_data['review_count'] = user_vocab.review_count
            vocab_data['saved_date'] = user_vocab.saved_date.isoformat() if user_vocab.saved_date else None
        else:
            vocab_data['is_saved'] = False
        
        # Thêm thông tin video
        if vocab.video_id:
            video = Video.query.get(vocab.video_id)
            if video:
                vocab_data['video_title'] = video.title
        
        return jsonify(success_response(
            message='Lấy thông tin từ vựng thành công',
            data={'vocabulary': vocab_data}
        )), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_vocabulary_detail: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy thông tin từ vựng',
            status_code=500,
            error=str(e)
        )), 500