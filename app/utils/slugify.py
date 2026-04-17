import re
from sqlalchemy.orm import Session
from app.models.organization_model import Organization

def slugify(text: str) -> str:
    """
    Converts text to a slug.
    Example: 'Acme Corporation' -> 'acme-corporation'
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text

def generate_unique_slug(db: Session, name: str) -> str:
    """
    Generates a unique slug for an organization.
    If 'acme' exists, it tries 'acme-1', 'acme-2', etc.
    """
    base_slug = slugify(name)
    slug = base_slug
    counter = 1
    
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
        
    return slug
