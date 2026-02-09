"""
LOCAL AI CINEMATIC VIDEO EDITOR (PRO VERSION)
Main Flask Application
"""

import os
import uuid
import json
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

# Import phase handlers
from phases.prompt_refiner import PromptRefiner
from phases.intelligent_questioning import IntelligentQuestioning
from phases.narrative_reasoning import NarrativeReasoning
from phases.scene_planning import ScenePlanning

# Import utilities
from utils.webhook import WebhookNotifier
from utils.validators import validate_json_schema
from models.schemas import (
    PromptRefinementOutput, 
    QuestioningOutput, 
    ScenePlanningOutput,
    WebhookConfig
)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 2GB max file size

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS
CORS(app)

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize phase handlers
prompt_refiner = PromptRefiner()
intelligent_questioning = IntelligentQuestioning()
narrative_reasoning = NarrativeReasoning()
scene_planning = ScenePlanning()

# Initialize webhook notifier
webhook_notifier = WebhookNotifier()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Session storage (in production, use Redis or database)
sessions = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_session(session_id):
    if session_id not in sessions:
        sessions[session_id] = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'video_path': None,
            'transcription': None,
            'visual_analysis': None,
            'phase': None,
            'webhook_config': None,
            'data': {}
        }
    return sessions[session_id]

@app.route('/')
def index():
    """Render the main web interface"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# ==================== FILE UPLOAD ENDPOINTS ====================

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """
    Handle video file upload
    Triggers webhook: VIDEO_UPLOAD_STARTED, VIDEO_UPLOAD_COMPLETED
    """
    session_id = request.form.get('session_id') or str(uuid.uuid4())
    session = get_session(session_id)
    
    # Webhook: Upload started
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'VIDEO_UPLOAD_STARTED',
            session_id,
            'Video upload initiated',
            {'filename': request.files.get('file', {}).filename if request.files.get('file') else None}
        ))
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part', 'session_id': session_id}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file', 'session_id': session_id}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{session_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            file.save(filepath)
            session['video_path'] = filepath
            session['phase'] = 'upload_complete'
            
            logger.info(f"Video uploaded successfully: {filepath}")
            
            # Webhook: Upload completed
            if session.get('webhook_config'):
                asyncio.run(webhook_notifier.notify(
                    session['webhook_config'],
                    'VIDEO_UPLOAD_COMPLETED',
                    session_id,
                    'Video upload completed successfully',
                    {'filepath': filepath, 'size': os.path.getsize(filepath)}
                ))
            
            # Notify via WebSocket
            socketio.emit('upload_complete', {
                'session_id': session_id,
                'filename': filename,
                'path': filepath
            }, room=session_id)
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'filename': filename,
                'path': filepath,
                'message': 'Video uploaded successfully'
            }), 200
            
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            
            # Webhook: Error
            if session.get('webhook_config'):
                asyncio.run(webhook_notifier.notify(
                    session['webhook_config'],
                    'ERROR',
                    session_id,
                    f'Upload failed: {str(e)}',
                    {'error': str(e)}
                ))
            
            return jsonify({
                'error': str(e),
                'session_id': session_id
            }), 500
    
    return jsonify({
        'error': 'Invalid file type',
        'session_id': session_id,
        'allowed_types': list(ALLOWED_EXTENSIONS)
    }), 400

# ==================== WEBHOOK CONFIGURATION ====================

@app.route('/api/webhook/config', methods=['POST'])
def configure_webhook():
    """Configure Discord webhook settings"""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    session = get_session(session_id)
    
    try:
        webhook_config = WebhookConfig(**data.get('webhook_config', {}))
        session['webhook_config'] = webhook_config.dict()
        
        # Test webhook if URL provided
        if webhook_config.webhook_url:
            asyncio.run(webhook_notifier.notify(
                session['webhook_config'],
                'WEBHOOK_TEST',
                session_id,
                'Webhook configured successfully',
                {}
            ))
        
        return jsonify({
            'success': True,
            'message': 'Webhook configuration saved',
            'config': session['webhook_config']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== PHASE 1: PROMPT REFINEMENT ====================

@app.route('/api/phase1/refine', methods=['POST'])
def phase1_refine_prompt():
    """
    Phase 1: Refine user prompt without changing intent
    Triggers webhook: PROMPT_REFINEMENT_STARTED, PROMPT_REFINEMENT_IMPROVED
    """
    data = request.json
    session_id = data.get('session_id', str(uuid.uuid4()))
    original_prompt = data.get('original_prompt', '')
    
    session = get_session(session_id)
    session['phase'] = 'phase1_prompt_refinement'
    
    # Webhook: Phase started
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'PROMPT_REFINEMENT_STARTED',
            session_id,
            'Phase 1: Prompt refinement started',
            {'original_prompt': original_prompt[:100] + '...' if len(original_prompt) > 100 else original_prompt}
        ))
    
    try:
        # Process prompt refinement
        result = prompt_refiner.refine(original_prompt)
        
        # Validate output schema
        validated = validate_json_schema(result, PromptRefinementOutput)
        
        session['data']['phase1'] = validated
        session['data']['improved_prompt'] = validated.get('improved_prompt')
        
        # Webhook: Refinement improved
        if session.get('webhook_config'):
            asyncio.run(webhook_notifier.notify(
                session['webhook_config'],
                'PROMPT_REFINEMENT_IMPROVED',
                session_id,
                'Prompt refined and awaiting user approval',
                {
                    'issues_detected': validated.get('issues_detected', []),
                    'improvements_made': validated.get('improvements_made', [])
                }
            ))
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'result': validated,
            'user_action_required': validated.get('user_action_required', 'accept')
        }), 200
        
    except Exception as e:
        logger.error(f"Phase 1 error: {str(e)}")
        
        if session.get('webhook_config'):
            asyncio.run(webhook_notifier.notify(
                session['webhook_config'],
                'ERROR',
                session_id,
                f'Prompt refinement failed: {str(e)}',
                {'error': str(e)}
            ))
        
        return jsonify({
            'error': str(e),
            'session_id': session_id
        }), 500

@app.route('/api/phase1/approve', methods=['POST'])
def phase1_approve():
    """
    User approves or rejects improved prompt
    Triggers webhook: PROMPT_REFINEMENT_APPROVED or revision cycle
    """
    data = request.json
    session_id = data.get('session_id')
    approved = data.get('approved', False)
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    session = sessions[session_id]
    
    if approved:
        session['data']['prompt_approved'] = True
        session['data']['final_prompt'] = session['data'].get('improved_prompt')
        
        if session.get('webhook_config'):
            asyncio.run(webhook_notifier.notify(
                session['webhook_config'],
                'PROMPT_REFINEMENT_APPROVED',
                session_id,
                'User approved improved prompt',
                {'final_prompt': session['data']['final_prompt'][:100] + '...'}
            ))
        
        return jsonify({
            'success': True,
            'message': 'Prompt approved. Proceeding to Phase 2.',
            'session_id': session_id,
            'next_phase': 'phase2_intelligent_questioning'
        }), 200
    else:
        # Revision requested
        feedback = data.get('feedback', '')
        new_attempt = prompt_refiner.refine_with_feedback(
            session['data'].get('original_prompt'),
            session['data'].get('improved_prompt'),
            feedback
        )
        
        if session.get('webhook_config'):
            asyncio.run(webhook_notifier.notify(
                session['webhook_config'],
                'PROMPT_REFINEMENT_REVISION',
                session_id,
                'User requested revision',
                {'feedback': feedback}
            ))
        
        return jsonify({
            'success': True,
            'message': 'Revision generated',
            'session_id': session_id,
            'result': new_attempt
        }), 200

# ==================== PHASE 2: INTELLIGENT QUESTIONING ====================

@app.route('/api/phase2/questions', methods=['POST'])
def phase2_generate_questions():
    """
    Phase 2: Generate intelligent questions based on approved prompt
    Triggers webhook: INTELLIGENT_QUESTIONING_STARTED, INTELLIGENT_QUESTIONING_COMPLETED
    """
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    session = sessions[session_id]
    session['phase'] = 'phase2_intelligent_questioning'
    
    if not session['data'].get('prompt_approved'):
        return jsonify({'error': 'Prompt not yet approved. Complete Phase 1 first.'}), 400
    
    # Webhook: Phase started
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'INTELLIGENT_QUESTIONING_STARTED',
            session_id,
            'Phase 2: Intelligent questioning started',
            {}
        ))
    
    try:
        final_prompt = session['data'].get('final_prompt')
        existing_answers = session['data'].get('phase2_answers', {})
        
        # Generate questions
        questions = intelligent_questioning.generate_questions(final_prompt, existing_answers)
        
        # Convert Question objects to dictionaries for JSON serialization
        questions_dict = [q.dict() for q in questions]
        
        session['data']['phase2_questions'] = questions_dict
        
        # Webhook: Phase completed
        if session.get('webhook_config'):
            asyncio.run(webhook_notifier.notify(
                session['webhook_config'],
                'INTELLIGENT_QUESTIONING_COMPLETED',
                session_id,
                f'Generated {len(questions)} questions',
                {'question_count': len(questions)}
            ))
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'questions': questions_dict,
            'total_questions': len(questions),
            'answered': len(existing_answers)
        }), 200

        
    except Exception as e:
        logger.error(f"Phase 2 error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/phase2/answer', methods=['POST'])
def phase2_submit_answer():
    """Submit answer to a specific question"""
    data = request.json
    session_id = data.get('session_id')
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    session = sessions[session_id]
    
    if 'phase2_answers' not in session['data']:
        session['data']['phase2_answers'] = {}
    
    session['data']['phase2_answers'][question_id] = answer
    
    # Check if all required questions answered
    all_answered = intelligent_questioning.check_completeness(
        session['data'].get('phase2_questions', []),
        session['data']['phase2_answers']
    )
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'question_id': question_id,
        'all_answered': all_answered,
        'can_proceed': all_answered
    }), 200

# ==================== PHASE 3: NARRATIVE REASONING ====================

@app.route('/api/phase3/analyze', methods=['POST'])
def phase3_narrative_analysis():
    """
    Phase 3: Deep narrative reasoning (hidden processing)
    Triggers webhook: NARRATIVE_REASONING_STARTED, NARRATIVE_REASONING_COMPLETED
    """
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    session = sessions[session_id]
    session['phase'] = 'phase3_narrative_reasoning'
    
    # Check prerequisites
    if not session['data'].get('phase2_answers'):
        return jsonify({'error': 'Phase 2 not completed. Answer questions first.'}), 400
    
    # Webhook: Phase started
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'NARRATIVE_REASONING_STARTED',
            session_id,
            'Phase 3: Deep narrative reasoning started (hidden)',
            {}
        ))
    
    try:
        final_prompt = session['data'].get('final_prompt')
        answers = session['data'].get('phase2_answers', {})
        transcription = session.get('transcription', {})
        visual_analysis = session.get('visual_analysis', {})
        
        # Perform hidden narrative analysis
        narrative_result = narrative_reasoning.analyze(
            final_prompt,
            answers,
            transcription,
            visual_analysis
        )
        
        # Store but don't expose detailed reasoning
        session['data']['phase3_narrative'] = narrative_result
        
        # Webhook: Phase completed
        if session.get('webhook_config'):
            asyncio.run(webhook_notifier.notify(
                session['webhook_config'],
                'NARRATIVE_REASONING_COMPLETED',
                session_id,
                'Narrative analysis completed',
                {
                    'narrative_arc': narrative_result.get('narrative_arc'),
                    'emotional_progression': narrative_result.get('emotional_progression')
                }
            ))
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Narrative analysis complete',
            'next_phase': 'phase4_scene_planning',
            'narrative_summary': {
                'arc': narrative_result.get('narrative_arc'),
                'tone': narrative_result.get('dominant_tone')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Phase 3 error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== PHASE 4: SCENE PLANNING ====================

@app.route('/api/phase4/plan', methods=['POST'])
def phase4_scene_planning():
    """
    Phase 4: Cinematic scene planning with Director LLM
    Triggers webhook: SCENE_PLANNING_STARTED, SCENE_PLANNING_COMPLETED
    """
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    session = sessions[session_id]
    session['phase'] = 'phase4_scene_planning'
    
    # Check prerequisites
    if not session['data'].get('phase3_narrative'):
        return jsonify({'error': 'Phase 3 not completed. Run narrative analysis first.'}), 400
    
    # Webhook: Phase started
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'SCENE_PLANNING_STARTED',
            session_id,
            'Phase 4: Cinematic scene planning started',
            {}
        ))
    
    try:
        # Gather all inputs for Director LLM
        inputs = {
            'solicitud': session['data'].get('final_prompt'),
            'transcripcion': session.get('transcription', {}),
            'visuales': session.get('visual_analysis', {}),
            'narrative': session['data'].get('phase3_narrative', {}),
            'answers': session['data'].get('phase2_answers', {})
        }
        
        # Generate scene plan
        scene_plan = scene_planning.generate_plan(inputs)
        
        # Validate strict JSON output
        validated = validate_json_schema(scene_plan, ScenePlanningOutput)
        
        session['data']['phase4_scene_plan'] = validated
        
        # Webhook: Phase completed
        if session.get('webhook_config'):
            scene_count = len(validated.get('scenes', []))
            asyncio.run(webhook_notifier.notify(
                session['webhook_config'],
                'SCENE_PLANNING_COMPLETED',
                session_id,
                f'Scene planning completed with {scene_count} scenes',
                {
                    'title': validated.get('title'),
                    'theme': validated.get('theme'),
                    'scene_count': scene_count
                }
            ))
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'scene_plan': validated,
            'message': 'Scene planning complete. Ready for execution.'
        }), 200
        
    except Exception as e:
        logger.error(f"Phase 4 error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== VIDEO PROCESSING ENDPOINTS ====================

@app.route('/api/transcription', methods=['POST'])
def start_transcription():
    """
    Start audio transcription
    Triggers webhook: AUDIO_TRANSCRIPTION_STARTED, AUDIO_TRANSCRIPTION_COMPLETED
    """
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    session = sessions[session_id]
    
    if not session.get('video_path'):
        return jsonify({'error': 'No video uploaded'}), 400
    
    # Webhook: Transcription started
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'AUDIO_TRANSCRIPTION_STARTED',
            session_id,
            'Audio transcription started',
            {'video': session['video_path']}
        ))
    
    # TODO: Implement actual transcription logic
    # For now, return mock data
    session['transcription'] = {
        'segments': [],
        'full_text': '',
        'language': 'es'
    }
    
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'AUDIO_TRANSCRIPTION_COMPLETED',
            session_id,
            'Audio transcription completed',
            {}
        ))
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Transcription complete'
    }), 200

@app.route('/api/visual-analysis', methods=['POST'])
def start_visual_analysis():
    """
    Start visual analysis
    Triggers webhook: VISUAL_ANALYSIS_STARTED, VISUAL_ANALYSIS_COMPLETED
    """
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    session = sessions[session_id]
    
    # Webhook: Visual analysis started
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'VISUAL_ANALYSIS_STARTED',
            session_id,
            'Visual analysis started',
            {}
        ))
    
    # TODO: Implement actual visual analysis
    session['visual_analysis'] = {
        'scenes': [],
        'key_frames': [],
        'visual_quality': {}
    }
    
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'VISUAL_ANALYSIS_COMPLETED',
            session_id,
            'Visual analysis completed',
            {}
        ))
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Visual analysis complete'
    }), 200

# ==================== EXECUTION ENDPOINTS ====================

@app.route('/api/execute/cut', methods=['POST'])
def execute_video_cut():
    """
    Execute a single video cut
    Triggers webhook: VIDEO_CUT_CREATION
    """
    data = request.json
    session_id = data.get('session_id')
    scene_id = data.get('scene_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    session = sessions[session_id]
    
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'VIDEO_CUT_CREATION',
            session_id,
            f'Creating video cut for scene {scene_id}',
            {'scene_id': scene_id}
        ))
    
    # TODO: Implement video cutting logic
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'scene_id': scene_id,
        'message': 'Video cut created'
    }), 200

@app.route('/api/execute/voiceover', methods=['POST'])
def generate_voiceover():
    """
    Generate voice-over audio
    Triggers webhook: VOICE_OVER_GENERATION
    """
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    session = sessions[session_id]
    
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'VOICE_OVER_GENERATION',
            session_id,
            'Generating voice-over',
            {}
        ))
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Voice-over generated'
    }), 200

@app.route('/api/execute/subtitles', methods=['POST'])
def generate_subtitles():
    """
    Generate subtitles
    Triggers webhook: SUBTITLE_GENERATION
    """
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    session = sessions[session_id]
    
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'SUBTITLE_GENERATION',
            session_id,
            'Generating subtitles',
            {}
        ))
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Subtitles generated'
    }), 200

@app.route('/api/execute/render', methods=['POST'])
def final_render():
    """
    Final video render
    Triggers webhook: FINAL_RENDER_STARTED, FINAL_RENDER_COMPLETED
    """
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    session = sessions[session_id]
    
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'FINAL_RENDER_STARTED',
            session_id,
            'Final render started',
            {}
        ))
    
    # TODO: Implement final render logic
    
    if session.get('webhook_config'):
        asyncio.run(webhook_notifier.notify(
            session['webhook_config'],
            'FINAL_RENDER_COMPLETED',
            session_id,
            'Final render completed',
            {'output_path': 'path/to/final/video.mp4'}
        ))
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Final render complete',
        'output_url': '/download/final.mp4'
    }), 200

# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

@socketio.on('join_session')
def handle_join_session(data):
    """Join a specific session room"""
    session_id = data.get('session_id')
    if session_id:
        # Join room for session-specific updates
        pass

# ==================== ERROR HANDLING ====================

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large',
        'max_size': '2GB',
        'message': 'Please upload a smaller video file'
    }), 413

@app.errorhandler(500)
def server_error(e):
    """Handle internal server error"""
    logger.error(f'Server error: {str(e)}')
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong. Please try again.'
    }), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("LOCAL AI CINEMATIC VIDEO EDITOR (PRO VERSION)")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
