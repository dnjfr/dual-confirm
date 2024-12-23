import os
import time
import jwt
from datetime import datetime, timedelta
import secrets
import threading
import logging
from dotenv import load_dotenv
from functools import wraps
from flask import redirect, current_app, request, session, url_for
from src.db_management.db_configurations import get_redis_users_sessions_connection


load_dotenv(override=True)

redis_users_sessions = get_redis_users_sessions_connection()
session_audit_tablename = os.getenv("POSTGRES_DB_AUDIT_TABLENAME_SESSIONS_AUDIT")

# Gestionnaire de rotation des clés
class KeyRotationManager:
    def __init__(self, initial_secret, rotation_interval_hours=24):
        """
        Gestionnaire de rotation des clés secrètes JWT
        
        Args:
            initial_secret (str): Clé secrète initiale
            rotation_interval_hours (int): Intervalle de rotation des clés
        """
        self.current_secret = initial_secret
        self.previous_secret = None
        self.rotation_interval = rotation_interval_hours
        self.last_rotation = datetime.now()
        
        # Démarre le thread de rotation périodique
        self.rotation_thread = threading.Thread(target=self._periodic_rotation, daemon=True)
        self.rotation_thread.start()
    
    # Thread pour la rotation périodique des clés
    def _periodic_rotation(self):
        """
        Thread pour la rotation périodique des clés
        """
        while True:
            # Attend l'intervalle de rotation
            time.sleep(self.rotation_interval * 3600)
            
            # Rotation des clés
            self.rotate_secret()
    
    # Fonction de rotation des clés
    def rotate_secret(self):
        """
        Effectue la rotation des clés secrètes
        """
        logging.info("Rotation des clés secrètes JWT")
        
        # Conserve l'ancienne clé comme clé précédente
        self.previous_secret = self.current_secret
        
        # Générer une nouvelle clé secrète
        self.current_secret = secrets.token_hex(32)
        self.last_rotation = datetime.now()

# Gestionnaire des OTP et tokens JWT
class OTPManager:
    def __init__(self, redis_connection, key_rotation_manager, audit_db_connection, users_db_connection):
        """
        Gestionnaire des OTP et tokens JWT
        
        Args:
            redis_connection (redis.Redis): Connexion Redis
            key_rotation_manager (KeyRotationManager): Gestionnaire de rotation des clés
            audit_db_connection (psycopg2.connection): Connexion à la base d'audit
        """
        self.redis = redis_connection
        self.key_rotation_manager = key_rotation_manager
        self.audit_db_connection = audit_db_connection
        self.users_db_connection = users_db_connection
        
        # Configuration du nettoyage périodique des OTP expirés
        self.cleanup_thread = threading.Thread(target=self._periodic_otp_cleanup, daemon=True)
        self.cleanup_thread.start()
    
    # Fonction de récupération de l'advisor_id associé à un user_id
    def _get_advisor_id(self, user_id):
        """
        Récupère l'advisor_id associé à un user_id
        
        Args:
            user_id (str): Identifiant de l'utilisateur
        
        Returns:
            str or None: L'identifiant du conseiller associé
        """
        try:
            with self.users_db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT advisor_id 
                    FROM users_advisors 
                    WHERE user_id = %s
                """, (user_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'advisor_id : {e}")
            return None
    
    # Fonction de génération d'OTP
    def generate_otp(self, user_id=None, advisor_id=None, expiration_minutes=15):
        """
        Génère un OTP et le stocke en cache avec JWT
        
        Stockage :
        - Clé Redis : "otp:{user_id}"
        - user_id (str, optional): ID de l'utilisateur client
        - advisor_id (str, optional): ID du conseiller
        - Expiration : Basée sur la durée de validité de l'OTP
        """
        
        if not user_id and not advisor_id:
            raise ValueError("Vous devez fournir soit un user_id, soit un advisor_id")
        
        if user_id and not advisor_id:
            advisor_id = self._get_advisor_id(user_id)
        
        if not advisor_id:
            raise ValueError("Impossible de déterminer un advisor_id associé.")
        
        redis_key = f"otp:{user_id or advisor_id}"
        
        # Détermine quel ID utiliser et récupére l'advisor_id si nécessaire
        if user_id:
            advisor_id = self._get_advisor_id(user_id)
        
        # Vérifie l'existence d'un OTP valide
        existing_token = self.redis.get(redis_key)
        if existing_token:
            try:
                # Tente de décoder avec la clé courante ou précédente
                payload = self._decode_token(existing_token)
                if payload:
                    return payload
            except jwt.InvalidTokenError:
                # Token invalide, on continue la génération
                pass
        
        # Générer un nouvel OTP
        otp = secrets.token_urlsafe(16)
        now = datetime.now()
        expiration = now + timedelta(minutes=expiration_minutes)
        
        payload = {
            'user_id': user_id,
            'advisor_id': advisor_id,
            'otp': otp,
            'exp': expiration,
            'iat': now.timestamp()
        }
        logging.debug(f"Payload généré: {payload}")
        # Encode avec la clé courante
        jwt_token = jwt.encode(
            payload, 
            self.key_rotation_manager.current_secret, 
            algorithm='HS256'
        )
        
        # Stockage dans Redis
        self.redis.setex(
            redis_key, 
            int(expiration_minutes * 60), 
            jwt_token
        )
        
        # Audit de la génération
        self._audit_otp_generation(user_id, advisor_id)
        
        # Audit de la déconnexion
        self._audit_logout(user_id, advisor_id)
        
        return jwt_token
    
    # Decode un token
    def _decode_token(self, token):
        """
        Décode un token JWT en essayant différentes clés
        
        Stratégie :
        1. Essayer avec la clé courante
        2. Si échec, essayer avec la clé précédente
        
        Returns:
            dict: Payload décodé ou None
        """
        try:
            # Essaye avec la clé courante
            payload = jwt.decode(
                token, 
                self.key_rotation_manager.current_secret, 
                algorithms=['HS256']
            )
            logging.debug(f"Token décodé avec succès : {payload}")
            return payload
        except jwt.ExpiredSignatureError:
            logging.error("Le token a expiré")
            return None
        except jwt.InvalidTokenError as e:
            # Essayer avec la clé précédente si disponible
            if self.key_rotation_manager.previous_secret:
                try:
                    payload = jwt.decode(
                        token, 
                        self.key_rotation_manager.previous_secret, 
                        algorithms=['HS256']
                    )
                    logging.debug(f"Token décodé avec la clé précédente : {payload}")
                    return payload
                except Exception as e:
                    logging.error(f"Erreur avec la clé précédente : {e}")
                    return None
            return None
    
    # Vérification de l'OTP
    def validate_otp(self, token, user_id=None, advisor_id=None):
        payload = self._decode_token(token)
        
        if not payload:
            return False
        
        now = datetime.now()
        exp = payload.get('exp')
        iat = payload.get('iat')

        # Vérification de l'expiration
        if not exp or now > datetime.fromtimestamp(exp):
            logging.error(f"Token expiré : exp={exp}, now={now}")
            return False

        # Vérification du timestamp initial
        if not iat or now < datetime.fromtimestamp(iat):
            logging.error(f"Horodatage du token invalide : iat={iat}, now={now}")
            return False
        
        # Cas du conseiller : 
        # - Doit avoir un advisor_id
        # - Ne doit PAS avoir de user_id
        if advisor_id is not None:
            return (
                payload.get('advisor_id') == advisor_id and 
                payload.get('user_id') is None
            )
        
        # Cas du client :
        # - Doit avoir un user_id 
        # - Doit avoir un advisor_id
        if user_id is not None:
            return (
                payload.get('user_id') == user_id and 
                payload.get('advisor_id') is not None
            )

        # Si aucun ID n'est spécifié, on considère le token comme valide
        return False
    
    # Nettoyage périodique des OTP expirés
    def _periodic_otp_cleanup(self):
        """
        Nettoie périodiquement les OTP expirés dans Redis
        
        Stratégie :
        - Parcourt toutes les clés OTP
        - Supprime celles qui ont expiré
        - S'exécute toutes les heures
        """
        while True:
            try:
                # Attente d'une heure entre chaque nettoyage
                time.sleep(3600)
                
                # Parcoure et supprime les OTP expirés
                otp_keys = self.redis.keys("otp:*")
                for key in otp_keys:
                    token = self.redis.get(key)
                    if token:
                        try:
                            # Tente de décoder le token
                            payload = self._decode_token(token)
                            if not payload:
                                # Token expiré ou invalide, supprimer
                                self.redis.delete(key)
                        except Exception as e:
                            logging.error(f"Erreur lors du nettoyage de {key}: {e}")
            except Exception as e:
                logging.error(f"Erreur dans le nettoyage périodique des OTP: {e}")
    
    # Fonction d'audit de la génération d'OTP
    def _audit_otp_generation(self, user_id, advisor_id, status='success'):
        try:
            role = 'advisor' if not user_id else 'client'
            with self.audit_db_connection.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {session_audit_tablename} (
                        user_id, 
                        advisor_id, 
                        role, 
                        login_timestamp, 
                        ip_address, 
                        user_agent, 
                        status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id, 
                    advisor_id, 
                    role, 
                    datetime.now(), 
                    request.remote_addr, 
                    request.user_agent.string, 
                    status
                ))
                self.audit_db_connection.commit()
        except Exception as e:
            logging.error(f"Erreur d'audit OTP : {e}")
    
    
    # Fonction d'audit de la déconnexion
    def _audit_logout(self, user_id, advisor_id):
        try:
            with self.audit_db_connection.cursor() as cursor:
                # Récupère le dernier enregistrement de connexion pour cet utilisateur
                cursor.execute(f"""
                    SELECT login_timestamp 
                    FROM {session_audit_tablename} 
                    WHERE (user_id = %s OR advisor_id = %s) 
                    ORDER BY login_timestamp DESC 
                    LIMIT 1
                """, (user_id, advisor_id))
                
                login_record = cursor.fetchone()
                
                if login_record:
                    login_timestamp = login_record[0]
                    logout_timestamp = datetime.now()
                    session_duration = logout_timestamp - login_timestamp
                    
                    # Met à jour l'enregistrement de la session avec la déconnexion et la durée
                    cursor.execute(f"""
                        UPDATE {session_audit_tablename} 
                        SET logout_timestamp = %s, 
                            session_duration = %s 
                        WHERE login_timestamp = %s 
                        AND (user_id = %s OR advisor_id = %s)
                    """, (
                        logout_timestamp, 
                        session_duration, 
                        login_timestamp,
                        user_id, 
                        advisor_id
                    ))
                    
                    self.audit_db_connection.commit()
            
        except Exception as e:
            logging.error(f"Erreur lors de l'audit de la déconnexion : {e}")


# Décorateur pour la connexion
def jwt_required(otp_manager):
    """
    Décorateur pour sécuriser les routes avec JWT
    
    Args:
        otp_manager (OTPManager): Instance du gestionnaire OTP
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_app.logger.debug("Entrée dans jwt_required")
            
            token = session.get('jwt_token')
            user_id = session.get('user_id')
            advisor_id = session.get('advisor_id')
            role = session.get('role')
            
            if not token:
                current_app.logger.error("Aucun token trouvé")
                session.clear()
                return redirect(url_for('login'))
            
            # Vérifier l'existence du token dans Redis
            redis_key = f"otp:{user_id or advisor_id}"
            stored_token = redis_users_sessions.get(redis_key)
            
            if not stored_token:
                current_app.logger.error("Token inexistant dans Redis")
                session.clear()
                return redirect(url_for('login'))
            
            # Validation adaptée selon le rôle
            if role == 'advisor':
                validation_result = otp_manager.validate_otp(token=token, advisor_id=advisor_id)
            elif role == 'client':
                validation_result = otp_manager.validate_otp(token=token, user_id=user_id)
            else:
                current_app.logger.error("Rôle invalide")
                session.clear()
                return redirect(url_for('login'))
            
            if not validation_result:
                current_app.logger.error(f"Token invalide pour le rôle {role}")
                session.clear()
                return redirect(url_for('login'))
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Initialisation du gestionnaire OTP
def init_otp_management(redis_connection, audit_db_connection, users_db_connection):
    """
    Initialise le gestionnaire OTP avec rotation de clés
    """
    # Génère une clé secrète initiale
    initial_secret = os.getenv('JWT_SECRET')
    
    # Crée le gestionnaire de rotation de clés
    key_rotation_manager = KeyRotationManager(initial_secret)
    
    # Crée le gestionnaire OTP
    otp_manager = OTPManager(
        redis_connection,
        key_rotation_manager,
        audit_db_connection,
        users_db_connection
    )
    
    return otp_manager