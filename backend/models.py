from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


# -----------------------------
# USER MODEL
# -----------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)  # technician, physician, patient


# -----------------------------
# PATIENT MODEL
# -----------------------------
class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    time_since_onset = Column(String)
    chief_complaint = Column(String)

    # Vitals
    systolic_bp = Column(Integer)
    diastolic_bp = Column(Integer)
    heart_rate = Column(Integer)
    oxygen_saturation = Column(Integer)
    temperature = Column(Float)
    glucose = Column(Float)
    platelet_count = Column(Integer)
    inr = Column(Float)

    # Unique patient code for linking
    code = Column(String, unique=True)

    # Link to User account
    linked_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationship to scans
    scans = relationship("StrokeScan", back_populates="patient")


# -----------------------------
# STROKE SCAN
# -----------------------------
class StrokeScan(Base):
    __tablename__ = "strokescans"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))

    image_path = Column(String)
    prediction = Column(String)
    timestamp = Column(DateTime)

    doctor_comment = Column(String)  # physician written comment
    eligibility_result = Column(String)  # detailed explanation for tPA eligibility
    eligible = Column(Boolean)  # True or False for tPA eligibility

    technician_notes = Column(String)
    status = Column(String, default="pending")  
    # pending → technician submitted
    # ready_for_review → physician needs to check
    # reviewed → physician finished
    reviewed_at = Column(DateTime)

    patient = relationship("Patient", back_populates="scans")

    # Relationship to treatment plan
    treatment_plan = relationship("TreatmentPlan", back_populates="scan", uselist=False)


# -----------------------------
# NIHSS ASSESSMENT
# -----------------------------
class NIHSSAssessment(Base):
    __tablename__ = "nihssassessments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))

    consciousness = Column(Integer)
    gaze = Column(Integer)
    visual = Column(Integer)
    facial = Column(Integer)
    motor_arm_left = Column(Integer)
    motor_arm_right = Column(Integer)
    motor_leg_left = Column(Integer)
    motor_leg_right = Column(Integer)
    ataxia = Column(Integer)
    sensory = Column(Integer)
    language = Column(Integer)
    dysarthria = Column(Integer)
    extinction = Column(Integer)

    total_score = Column(Integer)
    timestamp = Column(DateTime)

    patient = relationship("Patient")


# -----------------------------
# TREATMENT PLAN (NEW UPDATED)
# -----------------------------
class TreatmentPlan(Base):
    __tablename__ = "treatmentplans"
    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(Integer, ForeignKey("patients.id"))
    scan_id = Column(Integer, ForeignKey("strokescans.id"))

    # NEW FIELDS FOR ICD STORAGE
    icd_code = Column(String)             # e.g. "I63.9"
    icd_description = Column(String)      # e.g. "Cerebral infarction, unspecified"

    plan_type = Column(String)            # "tpa_eligible", "not_eligible", "alternative"
    ai_generated_plan = Column(String)    # entire AI-generated text
    physician_notes = Column(String)      # handwritten changes or comments

    status = Column(String, default="draft")  
    # draft → physician still editing
    # approved → finalized & shown to tech/patient
    # implemented → treatment started

    created_by = Column(String)           # physician username
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Relationships
    patient = relationship("Patient")
    scan = relationship("StrokeScan", back_populates="treatment_plan")
