from sqlalchemy.orm import Session

from app.db.models import Company
from app.schemas.company import CompanyCreate
from tests.utils.utils import random_lower_string


def create_random_company(db: Session) -> Company:
    name = random_lower_string()
    company_in = CompanyCreate(name=name)
    company = Company(**company_in.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company
