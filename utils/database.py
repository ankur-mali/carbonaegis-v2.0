"""
Database module for Carbon Emission Calculator application.
"""
import os
import json
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create SQLAlchemy base class
Base = declarative_base()

# Define database models
class EmissionData(Base):
    """
    Model for storing emission calculation data.
    """
    __tablename__ = 'emission_data'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=True)  # If we add user authentication later
    organization_name = Column(String, nullable=True)
    report_year = Column(Integer, nullable=True)
    time_period = Column(String, nullable=False)
    calculation_method = Column(String, nullable=False)
    input_data = Column(JSON, nullable=False)  # Store all input data as JSON
    scope1_emissions = Column(Float, nullable=True)
    scope2_emissions = Column(Float, nullable=True)
    scope3_emissions = Column(Float, nullable=True)
    total_emissions = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Helper method to convert to dict
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'organization_name': self.organization_name,
            'report_year': self.report_year,
            'time_period': self.time_period,
            'calculation_method': self.calculation_method,
            'input_data': self.input_data,
            'scope1_emissions': self.scope1_emissions,
            'scope2_emissions': self.scope2_emissions,
            'scope3_emissions': self.scope3_emissions,
            'total_emissions': self.total_emissions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Report(Base):
    """
    Model for storing generated reports.
    """
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    emission_data_id = Column(Integer, nullable=False)
    report_name = Column(String, nullable=False)
    report_type = Column(String, nullable=False)  # 'pdf' or 'excel'
    organization_name = Column(String, nullable=True)
    report_year = Column(Integer, nullable=True)
    prepared_by = Column(String, nullable=True)
    report_date = Column(DateTime, nullable=False)
    report_content = Column(Text, nullable=True)  # For report metadata or comments
    created_at = Column(DateTime, default=datetime.utcnow)


# Create database connection
def get_db_engine():
    """
    Create SQLAlchemy engine from the DATABASE_URL environment variable.
    """
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Handle the 'postgres://' vs 'postgresql://' issue
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    return create_engine(database_url)


def get_db_session():
    """
    Create a new database session.
    """
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """
    Initialize the database by creating all tables.
    """
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    return engine


def save_emission_data(input_data, organization_name=None, report_year=None):
    """
    Save emission calculation data to the database.
    
    Args:
        input_data (dict): Dictionary containing all input data and calculation results
        organization_name (str, optional): Organization name
        report_year (int, optional): Report year
    
    Returns:
        int: ID of the newly created record
    """
    session = get_db_session()
    
    # Extract required data from input_data
    time_period = input_data.get('time_period', 'Monthly')
    calculation_method = input_data.get('calculation_method', 'Standard')
    
    # Extract emission results
    scope1_emissions = input_data.get('scope1_total', 0.0)
    scope2_emissions = input_data.get('scope2_total', 0.0)
    scope3_emissions = input_data.get('scope3_total', 0.0)
    total_emissions = input_data.get('total_emissions', 0.0)
    
    # Create new record
    emission_data = EmissionData(
        organization_name=organization_name,
        report_year=report_year,
        time_period=time_period,
        calculation_method=calculation_method,
        input_data=input_data,
        scope1_emissions=scope1_emissions,
        scope2_emissions=scope2_emissions,
        scope3_emissions=scope3_emissions,
        total_emissions=total_emissions
    )
    
    try:
        session.add(emission_data)
        session.commit()
        record_id = emission_data.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    
    return record_id


def get_emission_data(record_id):
    """
    Retrieve emission data from the database by ID.
    
    Args:
        record_id (int): ID of the record to retrieve
    
    Returns:
        dict: Dictionary containing the emission data
    """
    session = get_db_session()
    
    try:
        emission_data = session.query(EmissionData).filter_by(id=record_id).first()
        if emission_data:
            return emission_data.to_dict()
        return None
    finally:
        session.close()


def get_all_emission_data():
    """
    Retrieve all emission data records from the database.
    
    Returns:
        list: List of dictionaries containing the emission data
    """
    session = get_db_session()
    
    try:
        emission_data_list = session.query(EmissionData).order_by(EmissionData.created_at.desc()).all()
        return [data.to_dict() for data in emission_data_list]
    finally:
        session.close()


def save_report(emission_data_id, report_name, report_type, organization_name=None, 
                report_year=None, prepared_by=None, report_date=None, report_content=None):
    """
    Save report metadata to the database.
    
    Args:
        emission_data_id (int): ID of the associated emission data
        report_name (str): Name of the report
        report_type (str): Type of report ('pdf' or 'excel')
        organization_name (str, optional): Organization name
        report_year (int, optional): Report year
        prepared_by (str, optional): Name of the person who prepared the report
        report_date (datetime, optional): Date of the report
        report_content (str, optional): Report metadata or comments
    
    Returns:
        int: ID of the newly created report record
    """
    session = get_db_session()
    
    # Convert report_date to datetime if it's a date object
    if report_date and not isinstance(report_date, datetime):
        try:
            report_date = datetime.combine(report_date, datetime.min.time())
        except:
            # If there's an error converting, use current datetime
            report_date = datetime.utcnow()
    
    # Default to current time if no date provided
    if not report_date:
        report_date = datetime.utcnow()
    
    # Convert report_year to int if needed
    if report_year and not isinstance(report_year, int):
        try:
            report_year = int(report_year)
        except:
            report_year = datetime.utcnow().year
    
    # Create new report record
    report = Report(
        emission_data_id=emission_data_id,
        report_name=report_name,
        report_type=report_type,
        organization_name=organization_name,
        report_year=report_year,
        prepared_by=prepared_by,
        report_date=report_date,
        report_content=report_content
    )
    
    try:
        session.add(report)
        session.commit()
        report_id = report.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    
    return report_id


def df_to_sql(dataframe, table_name, if_exists='replace', index=False):
    """
    Save a pandas DataFrame to the database.
    
    Args:
        dataframe (pd.DataFrame): DataFrame to save
        table_name (str): Name of the table
        if_exists (str, optional): How to behave if the table exists. 
                                  Options: 'fail', 'replace', 'append'.
        index (bool, optional): Write DataFrame index as a column
    """
    engine = get_db_engine()
    dataframe.to_sql(table_name, engine, if_exists=if_exists, index=index)