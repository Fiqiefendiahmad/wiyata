import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class ToolCategoryResponse(BaseModel):
    id: str | uuid.UUID
    slug: str
    name_en: str
    name_id: str
    description_en: str | None = None
    description_id: str | None = None
    tool_count: int = 0

    model_config = {"from_attributes": True}


class FeatureItem(BaseModel):
    name_en: str
    name_id: str
    description_en: str
    description_id: str
    edition_scope: str = "all"  # "community", "enterprise", "all"
    verification_status: str = "verified"  # "verified", "partially_verified", "deprecated"


class CompatibilityTarget(BaseModel):
    target_type: str  # "database_engine", "operating_system", "cloud_platform"
    target_name: str
    version_scope: str
    support_level: str  # "native", "jdbc_driver", "via_extension", "deprecated"
    notes_en: str
    notes_id: str
    verification_status: str = "verified"


class SecurityConsiderations(BaseModel):
    credential_storage: str
    network_and_ports: str
    tls_ssl_support: str
    privilege_model: str
    audit_logging: str


class GettingStartedStep(BaseModel):
    step_number: int
    title_en: str
    title_id: str
    command: str | None = None
    instruction_en: str
    instruction_id: str
    checkpoint_en: str | None = None
    checkpoint_id: str | None = None


class GettingStartedWorkflow(BaseModel):
    prerequisites_en: list[str] = Field(default_factory=list)
    prerequisites_id: list[str] = Field(default_factory=list)
    steps: list[GettingStartedStep] = Field(default_factory=list)
    safe_first_test_en: str
    safe_first_test_id: str
    troubleshooting_tips_en: list[str] = Field(default_factory=list)
    troubleshooting_tips_id: list[str] = Field(default_factory=list)


class ProfessionalScenario(BaseModel):
    scenario_id: str
    title_en: str
    title_id: str
    role: str
    goal_en: str
    goal_id: str
    environment: str
    steps_en: list[str] = Field(default_factory=list)
    steps_id: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    validation_en: str
    validation_id: str
    expected_result_en: str
    expected_result_id: str
    rollback_en: str | None = None
    rollback_id: str | None = None


class CareerConnection(BaseModel):
    role_id: str
    role_name_en: str
    role_name_id: str
    competency_id: str
    competency_name_en: str
    competency_name_id: str
    proficiency_level: str  # "foundational", "intermediate", "advanced", "expert"
    relevance_why_en: str
    relevance_why_id: str


class KnowledgeConnection(BaseModel):
    article_slug: str
    title_en: str
    title_id: str
    relationship_type: str  # "operational_guide", "troubleshooting", "architecture"


class ExerciseConnection(BaseModel):
    exercise_slug: str
    title_en: str
    title_id: str
    lab_type: str


class ToolAlternative(BaseModel):
    slug: str
    name: str
    product_type: str
    license_model: str
    tradeoff_en: str
    tradeoff_id: str


class VerifiedSourceCitation(BaseModel):
    claim_topic: str
    source_url: str
    source_title: str
    verified_at: str
    status: str = "verified"  # "verified", "partially_verified", "deprecated"


class ToolSummary(BaseModel):
    id: str | uuid.UUID
    slug: str
    name: str
    vendor: str | None = None
    category_slug: str | None = None
    category_name: str | None = None
    category_name_id: str | None = None
    product_type: str = "Standalone Utility"
    summary: str | None = None
    summary_id: str | None = None
    official_url: str | None = None
    documentation_url: str | None = None
    license_model: str | None = None
    supported_platforms: list[str] = Field(default_factory=list)
    supported_engines: list[str] = Field(default_factory=list)
    verification_status: str = "verified"
    publication_status: str = "published"
    lifecycle_status: str = "active"
    last_verified_at: datetime | None = None

    model_config = {"from_attributes": True}


class ToolDetail(ToolSummary):
    repository_url: str | None = None
    download_url: str | None = None
    overview_en: str | None = None
    overview_id: str | None = None
    primary_use_cases_en: list[str] = Field(default_factory=list)
    primary_use_cases_id: list[str] = Field(default_factory=list)
    explicit_boundaries_en: list[str] = Field(default_factory=list)
    explicit_boundaries_id: list[str] = Field(default_factory=list)
    features: list[FeatureItem] = Field(default_factory=list)
    compatibility_matrix: list[CompatibilityTarget] = Field(default_factory=list)
    security_considerations: SecurityConsiderations | None = None
    getting_started: GettingStartedWorkflow | None = None
    practical_scenarios: list[ProfessionalScenario] = Field(default_factory=list)
    career_connections: list[CareerConnection] = Field(default_factory=list)
    knowledge_connections: list[KnowledgeConnection] = Field(default_factory=list)
    exercise_connections: list[ExerciseConnection] = Field(default_factory=list)
    alternatives: list[ToolAlternative] = Field(default_factory=list)
    verified_sources: list[VerifiedSourceCitation] = Field(default_factory=list)
    content_reviewed_at: str | None = None

    model_config = {"from_attributes": True}


class ToolListResponse(BaseModel):
    items: list[ToolSummary]
    total: int
    page: int
    limit: int
    categories: list[ToolCategoryResponse] = Field(default_factory=list)


class ToolFiltersResponse(BaseModel):
    categories: list[dict[str, str]]
    engines: list[str]
    platforms: list[str]
    licenses: list[str]
    verification_statuses: list[str]
