from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, LargeBinary, text,  Boolean, func
from sqlalchemy.orm import relationship

from db.database import Base


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    created_by = Column(String)
    modified_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # default value
        onupdate=func.now()  # automatically updates on row update
    )
    modified_by = Column(String)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)  # hashed password
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    created_at = Column(DateTime, default=datetime.utcnow())
    created_by = Column(String)
    modified_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # default value
        onupdate=func.now()  # automatically updates on row update
    )
    modified_by = Column(String)

    organization = relationship("Organization", backref="users")


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    # address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow())
    created_by = Column(String)
    modified_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # default value
        onupdate=func.now()  # automatically updates on row update
    )
    modified_by = Column(String)
    is_active = Column(
        Boolean,  # SQLAlchemy Boolean type
        nullable=False,  # Cannot be NULL
        default=True  # Default True at the DB level
    )  # pages_per_valve = Column(Integer)

    organization = relationship("Organization", backref="customers")


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # country = Column(String)
    country_id = Column(Integer, ForeignKey('countries.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    created_by = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    modified_by = Column(String)
    modified_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", backref="projects")
    customer = relationship("Customer", backref="projects")


class ExtractionTemplate(Base):
    __tablename__ = "extraction_templates"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    ocr_boxes = Column(JSON)  # all OCR-extracted boxes with unique IDs
    box_mappings = Column(JSON)  # key-value box relationships by ID
    # created_at = Column(DateTime, default=datetime.utcnow())
    created_by = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    modified_by = Column(String)
    modified_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", backref="templates")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, server_default=text('1'))
    created_by = Column(Integer, ForeignKey('users.id'))
    format_id = Column(Integer, ForeignKey('formats.id'))
    fluid_state_id = Column(Integer, ForeignKey('fluid_states.id'))
    page_per_item = Column(Integer, nullable=False, server_default='1')
    filename = Column(String)
    raw_pdf = Column(LargeBinary)
    extracted_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow())
    modified_by = Column(String)
    modified_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # 🔽 Add this line to reference the template
    template_id = Column(Integer, ForeignKey('extraction_templates.id'), nullable=True)

    # Relationships
    customer = relationship("Customer", backref="documents")
    project = relationship("Project", backref="documents")
    format = relationship("Format", backref="documents")
    fluid_state = relationship("Fluid_state", backref="documents")
    uploaded_by = relationship("User")
    template = relationship("ExtractionTemplate", backref="documents")


class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_by = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    modified_by = Column(String)
    modified_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class Fluid_state(Base):
    __tablename__ = "fluid_states"
    id = Column(Integer, primary_key=True)
    fluid_state = Column(String)
    created_by = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    modified_by = Column(String)
    modified_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class Format(Base):
    __tablename__ = "formats"
    id = Column(Integer, primary_key=True)
    format = Column(String)
    created_by = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    modified_by = Column(String)
    modified_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class Sizingtool(Base):
    __tablename__ = "standard_parameters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fluid_state_id = Column(Integer)
    format_id = Column(Integer)
    parameters = Column(String, nullable=False)
    created_by = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    modified_by = Column(String)
    modified_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

