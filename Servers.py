from flask import Flask, request, jsonify
import json
from datetime import datetime
import logging

app = Flask(__name__)

# Configuration du logging pour voir toutes les requêtes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Stockage simple en mémoire (sera perdu au redémarrage)
users = {}
sessions = {}

# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================

def log_request():
    """Log toutes les infos de la requête"""
    logger.info(f"\n{'='*60}")
    logger.info(f"METHOD: {request.method}")
    logger.info(f"PATH: {request.path}")
    logger.info(f"HEADERS: {dict(request.headers)}")
    
    if request.data:
        try:
            data = request.get_json()
            logger.info(f"BODY (JSON): {json.dumps(data, indent=2)}")
        except:
            logger.info(f"BODY (RAW): {request.data}")
    
    logger.info(f"QUERY PARAMS: {dict(request.args)}")
    logger.info(f"{'='*60}\n")

def create_response(success=True, data=None, message=""):
    """Crée une réponse standardisée"""
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "message": message
    }
    if data:
        response["data"] = data
    return jsonify(response)

# ==========================================
# ROUTES DE BASE
# ==========================================

@app.route('/', methods=['GET', 'POST'])
def home():
    """Route racine - probablement un health check"""
    log_request()
    return create_response(
        success=True,
        message="Wibble Wobble Private Server - Running"
    )

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    log_request()
    return create_response(success=True, message="Server is running")

# ==========================================
# ROUTES D'AUTHENTIFICATION (À ADAPTER)
# ==========================================

@app.route('/api/login', methods=['POST'])
@app.route('/api/auth/login', methods=['POST'])
@app.route('/login', methods=['POST'])
def login():
    """Endpoint de login - à adapter selon ce que le jeu envoie"""
    log_request()
    
    data = request.get_json() if request.is_json else {}
    
    # Récupération des identifiants (à adapter)
    device_id = data.get('device_id', 'unknown')
    user_id = data.get('user_id', device_id)
    
    # Création d'une session simple
    session_token = f"session_{user_id}_{datetime.now().timestamp()}"
    sessions[session_token] = {
        "user_id": user_id,
        "device_id": device_id,
        "created_at": datetime.now().isoformat()
    }
    
    # Création ou récupération de l'utilisateur
    if user_id not in users:
        users[user_id] = {
            "user_id": user_id,
            "device_id": device_id,
            "created_at": datetime.now().isoformat(),
            "level": 1,
            "coins": 1000,
            "yokai": []
        }
    
    return create_response(
        success=True,
        data={
            "session_token": session_token,
            "user": users[user_id]
        },
        message="Login successful"
    )

@app.route('/api/session', methods=['POST', 'GET'])
@app.route('/session', methods=['POST', 'GET'])
def session():
    """Vérification de session"""
    log_request()
    
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if session_token in sessions:
        session_data = sessions[session_token]
        user_data = users.get(session_data['user_id'], {})
        
        return create_response(
            success=True,
            data={
                "session": session_data,
                "user": user_data
            }
        )
    
    return create_response(
        success=False,
        message="Invalid session"
    ), 401

# ==========================================
# ROUTES DE JEU (À COMPLÉTER)
# ==========================================

@app.route('/api/game/start', methods=['POST'])
@app.route('/game/start', methods=['POST'])
def game_start():
    """Démarrage d'une partie"""
    log_request()
    
    return create_response(
        success=True,
        data={
            "stage_id": 1,
            "difficulty": "normal"
        }
    )

@app.route('/api/user/profile', methods=['GET'])
@app.route('/user/profile', methods=['GET'])
def user_profile():
    """Profil utilisateur"""
    log_request()
    
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if session_token in sessions:
        user_id = sessions[session_token]['user_id']
        user_data = users.get(user_id, {})
        
        return create_response(
            success=True,
            data=user_data
        )
    
    return create_response(success=False, message="Unauthorized"), 401

# ==========================================
# CATCH-ALL ROUTE
# ==========================================

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def catch_all(path):
    """Capture toutes les autres routes pour les logger"""
    log_request()
    
    logger.warning(f"Unknown endpoint called: /{path}")
    
    # Réponse générique pour ne pas bloquer le jeu
    return create_response(
        success=True,
        data={},
        message=f"Endpoint /{path} - under development"
    )

# ==========================================
# DÉMARRAGE DU SERVEUR
# ==========================================

if __name__ == '__main__':
    logger.info("🚀 Wibble Wobble Private Server Starting...")
    logger.info("📝 All requests will be logged for analysis")
    logger.info("="*60)
    
    # Pour Replit ou hébergement cloud
    app.run(host='0.0.0.0', port=8080, debug=True)
