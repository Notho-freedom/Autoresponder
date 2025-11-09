"""
Configuration du logging centralisé
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


# Configuration du format de log
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Configure et retourne un logger
    
    Args:
        name: Nom du logger (généralement __name__ du module)
        level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    
    # Éviter la duplication des handlers
    if logger.handlers:
        return logger
    
    # Définir le niveau
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Handler pour la console (avec couleurs)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Formatter avec couleurs pour la console
    console_formatter = ColoredFormatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(console_handler)
    
    return logger


class ColoredFormatter(logging.Formatter):
    """Formatter avec support des couleurs pour la console"""
    
    # Codes ANSI pour les couleurs
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Vert
        'WARNING': '\033[33m',   # Jaune
        'ERROR': '\033[31m',     # Rouge
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Ajouter la couleur selon le niveau
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        
        return super().format(record)


# Logger global pour l'application
app_logger = setup_logger("autoresponder")
