"""
Utilitaires de validation et normalisation des données
"""
import re
from typing import Optional
from email_validator import validate_email, EmailNotValidError


def is_valid_email(email: str) -> bool:
    """
    Valide un email selon RFC 5322
    
    Args:
        email: Adresse email à valider
        
    Returns:
        True si valide, False sinon
    """
    try:
        validate_email(email, check_deliverability=False)
        return True
    except (EmailNotValidError, AttributeError, TypeError):
        return False


def normalize_phone(phone: str) -> str:
    """
    Normalise un numéro de téléphone au format international
    
    Args:
        phone: Numéro de téléphone à normaliser
        
    Returns:
        Numéro normalisé avec le préfixe +
    """
    if not phone:
        return ""
    
    # Supprimer tous les espaces, tirets, points, parenthèses
    cleaned = re.sub(r'[\s\-\.\(\)]', '', phone)
    
    # Ajouter + si absent
    if not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    
    return cleaned


def is_valid_phone(phone: str, min_digits: int = 6, max_digits: int = 20) -> bool:
    """
    Valide un numéro de téléphone
    
    Args:
        phone: Numéro à valider
        min_digits: Nombre minimum de chiffres (défaut: 6)
        max_digits: Nombre maximum de chiffres (défaut: 20)
        
    Returns:
        True si valide, False sinon
    """
    if not phone:
        return False
    
    # Extraire seulement les chiffres
    digits = re.sub(r'\D', '', phone)
    
    # Vérifier la longueur
    return min_digits <= len(digits) <= max_digits


def sanitize_name(name: Optional[str]) -> str:
    """
    Nettoie et sécurise un nom
    
    Args:
        name: Nom à nettoyer
        
    Returns:
        Nom nettoyé ou chaîne vide
    """
    if not name:
        return ""
    
    # Supprimer les espaces multiples et trim
    cleaned = re.sub(r'\s+', ' ', name.strip())
    
    # Limiter à 100 caractères
    if len(cleaned) > 100:
        cleaned = cleaned[:100]
    
    return cleaned


def extract_email_username(email: str) -> str:
    """
    Extrait le nom d'utilisateur d'une adresse email
    
    Args:
        email: Adresse email
        
    Returns:
        Partie avant le @ ou email complet si pas de @
    """
    if '@' in email:
        return email.split('@')[0]
    return email


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Tronque un texte à une longueur maximale
    
    Args:
        text: Texte à tronquer
        max_length: Longueur maximale
        suffix: Suffixe à ajouter si tronqué (défaut: "...")
        
    Returns:
        Texte tronqué si nécessaire
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
