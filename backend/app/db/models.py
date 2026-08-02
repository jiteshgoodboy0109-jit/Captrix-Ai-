import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="Analyst")  # Analyst, CFO, Admin
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    uploads = relationship("Upload", back_populates="user", cascade="all, delete-orphan")
    history = relationship("History", back_populates="user", cascade="all, delete-orphan")

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, default="General")
    currency = Column(String, default="USD")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    uploads = relationship("Upload", back_populates="company", cascade="all, delete-orphan")

class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, default=0)
    sheet_names = Column(JSON, default=list)
    status = Column(String, default="COMPLETED") # PROCESSING, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="uploads")
    company = relationship("Company", back_populates="uploads")
    financial_data = relationship("FinancialData", back_populates="upload", cascade="all, delete-orphan")
    statement = relationship("Statement", back_populates="upload", uselist=False, cascade="all, delete-orphan")
    ratio = relationship("Ratio", back_populates="upload", uselist=False, cascade="all, delete-orphan")
    corporate_finance = relationship("CorporateFinance", back_populates="upload", uselist=False, cascade="all, delete-orphan")
    ai_report = relationship("AIReport", back_populates="upload", uselist=False, cascade="all, delete-orphan")
    chat_histories = relationship("ChatHistory", back_populates="upload", cascade="all, delete-orphan")

class FinancialData(Base):
    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    account_code = Column(String, nullable=True)
    account_name = Column(String, nullable=False)
    account_type = Column(String, nullable=False) # Asset, Liability, Equity, Revenue, Expense, Cash, etc.
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    net_amount = Column(Float, default=0.0)
    metadata_json = Column(JSON, default=dict)

    upload = relationship("Upload", back_populates="financial_data")

class Statement(Base):
    __tablename__ = "statements"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    balance_sheet = Column(JSON, nullable=False)
    income_statement = Column(JSON, nullable=False)
    cash_flow = Column(JSON, nullable=False)
    trial_balance = Column(JSON, nullable=False)
    ledger_summary = Column(JSON, nullable=False)

    upload = relationship("Upload", back_populates="statement")

class Ratio(Base):
    __tablename__ = "ratios"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    profitability = Column(JSON, nullable=False)
    liquidity = Column(JSON, nullable=False)
    solvency = Column(JSON, nullable=False)
    efficiency = Column(JSON, nullable=False)

    upload = relationship("Upload", back_populates="ratio")

class CorporateFinance(Base):
    __tablename__ = "corporate_finance"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    capital_budgeting = Column(JSON, nullable=False)
    capital_structure = Column(JSON, nullable=False)
    working_capital_cycle = Column(JSON, nullable=False)

    upload = relationship("Upload", back_populates="corporate_finance")

class AIReport(Base):
    __tablename__ = "ai_reports"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    health_score = Column(Float, default=0.0)
    executive_summary = Column(Text, nullable=False)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)

    upload = relationship("Upload", back_populates="ai_report")

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    company_name = Column(String, nullable=False)
    health_score = Column(Float, default=0.0)
    status = Column(String, default="COMPLETED")
    report_name = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="history")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    upload = relationship("Upload", back_populates="chat_histories")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
