import hashlib
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.report import ReportArtifact, ArtifactVersion


class ArtifactCRUD:
    """Artifact CRUD operations with versioning support"""

    @staticmethod
    async def create_artifact(
        db: AsyncSession,
        report_id: int,
        step_id: str,
        skill_id: str,
        logical_name: str,
        filename: str,
        artifact_type: str,
        content: str,
        source_type: str = "initial_generation",
        change_reason: str = None,
        created_by: str = "system",
        metadata: dict = None,
    ) -> ReportArtifact:
        """Create a new artifact with initial version"""
        artifact = ReportArtifact(
            report_id=report_id,
            step_id=step_id,
            skill_id=skill_id,
            logical_name=logical_name,
            filename=filename,
            artifact_type=artifact_type,
        )
        db.add(artifact)
        await db.flush()

        version = ArtifactVersion(
            artifact_id=artifact.id,
            version=1,
            content=content,
            content_hash=ArtifactCRUD._hash_content(content),
            change_reason=change_reason or "Initial creation",
            created_by=created_by,
            source_type=source_type,
            source_step_id=step_id,
            extra_metadata=metadata,
        )
        db.add(version)
        await db.flush()

        artifact.current_version_id = version.id
        await db.commit()
        await db.refresh(artifact)
        return artifact

    @staticmethod
    async def create_version(
        db: AsyncSession,
        artifact_id: int,
        content: str,
        source_type: str = "skill_rerun",
        change_reason: str = None,
        created_by: str = "system",
        source_step_id: str = None,
        metadata: dict = None,
    ) -> ArtifactVersion:
        """Create a new version for an existing artifact"""
        result = await db.execute(
            select(func.max(ArtifactVersion.version))
            .where(ArtifactVersion.artifact_id == artifact_id)
        )
        max_version = result.scalar() or 0

        version = ArtifactVersion(
            artifact_id=artifact_id,
            version=max_version + 1,
            content=content,
            content_hash=ArtifactCRUD._hash_content(content),
            change_reason=change_reason,
            created_by=created_by,
            source_type=source_type,
            source_step_id=source_step_id,
            extra_metadata=metadata,
        )
        db.add(version)
        await db.flush()

        result = await db.execute(
            select(ReportArtifact).where(ReportArtifact.id == artifact_id)
        )
        artifact = result.scalar_one_or_none()
        if artifact:
            artifact.current_version_id = version.id
            artifact.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(version)
        return version

    @staticmethod
    async def get_artifact(
        db: AsyncSession, artifact_id: int
    ) -> Optional[ReportArtifact]:
        """Get artifact with current version"""
        result = await db.execute(
            select(ReportArtifact)
            .where(ReportArtifact.id == artifact_id)
            .options(
                selectinload(ReportArtifact.current_version),
                selectinload(ReportArtifact.versions),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_artifact_by_step(
        db: AsyncSession, report_id: int, step_id: str
    ) -> Optional[ReportArtifact]:
        """Get artifact by report_id and step_id"""
        result = await db.execute(
            select(ReportArtifact)
            .where(ReportArtifact.report_id == report_id)
            .where(ReportArtifact.step_id == step_id)
            .options(
                selectinload(ReportArtifact.current_version),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_report_artifacts(
        db: AsyncSession, report_id: int
    ) -> List[ReportArtifact]:
        """Get all artifacts for a report"""
        result = await db.execute(
            select(ReportArtifact)
            .where(ReportArtifact.report_id == report_id)
            .options(
                selectinload(ReportArtifact.current_version),
            )
            .order_by(ReportArtifact.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def get_artifact_versions(
        db: AsyncSession, artifact_id: int
    ) -> List[ArtifactVersion]:
        """Get all versions of an artifact"""
        result = await db.execute(
            select(ArtifactVersion)
            .where(ArtifactVersion.artifact_id == artifact_id)
            .order_by(ArtifactVersion.version.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_version(
        db: AsyncSession, version_id: int
    ) -> Optional[ArtifactVersion]:
        """Get a specific version"""
        result = await db.execute(
            select(ArtifactVersion).where(ArtifactVersion.id == version_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def restore_version(
        db: AsyncSession,
        artifact_id: int,
        source_version_id: int,
        created_by: str = "user",
    ) -> ArtifactVersion:
        """Restore an old version as a new version"""
        source_version = await ArtifactCRUD.get_version(db, source_version_id)
        if not source_version:
            raise ValueError(f"Source version {source_version_id} not found")

        return await ArtifactCRUD.create_version(
            db=db,
            artifact_id=artifact_id,
            content=source_version.content,
            source_type="user_edit",
            change_reason=f"Restored from version {source_version.version}",
            created_by=created_by,
            metadata={"restored_from_version": source_version.version},
        )

    @staticmethod
    def _hash_content(content: str) -> str:
        """Generate SHA256 hash of content"""
        if not content:
            return ""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
