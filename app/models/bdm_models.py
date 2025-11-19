"""
Modelos SQLAlchemy basados en el BDM de Bonita.
Representan las tablas en PostgreSQL.
"""
from datetime import date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Double, BigInteger, Date,
    ForeignKey, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base, get_schema


class PerfilContratista(Base):
    """
    Perfil del contratista asociado a Bonita.
    """
    __tablename__ = "perfil_contratista"
    __table_args__ = {"schema": get_schema()}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    nombre_completo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    documento_identidad: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    id_usuario_bonita: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    estado: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Relaciones
    contratos: Mapped[List["Contrato"]] = relationship(
        "Contrato",
        back_populates="perfil_contratista",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<PerfilContratista(id={self.id}, nombre={self.nombre_completo})>"


class ContratoInterAdministrativo(Base):
    """
    Contratos marco base (padre de contratos específicos).
    """
    __tablename__ = "contrato_inter_administrativo"
    __table_args__ = {"schema": get_schema()}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    numero_contrato: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    supervisor: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    contratista: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Relaciones
    componentes: Mapped[List["Componente"]] = relationship(
        "Componente",
        back_populates="contrato_marco",
        cascade="all, delete-orphan"
    )
    contratos: Mapped[List["Contrato"]] = relationship(
        "Contrato",
        back_populates="padre",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ContratoInterAdministrativo(id={self.id}, numero={self.numero_contrato})>"


class Componente(Base):
    """
    Componentes y subcomponentes de un contrato marco.
    """
    __tablename__ = "componente"
    __table_args__ = {"schema": get_schema()}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    indice: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Foreign keys
    contrato_marco_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{get_schema()}.contrato_inter_administrativo.id", ondelete="CASCADE"),
        nullable=True
    )
    componente_padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{get_schema()}.componente.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relaciones
    contrato_marco: Mapped[Optional["ContratoInterAdministrativo"]] = relationship(
        "ContratoInterAdministrativo",
        back_populates="componentes"
    )
    componente_padre: Mapped[Optional["Componente"]] = relationship(
        "Componente",
        remote_side="Componente.id",
        back_populates="componentes_hijos"
    )
    componentes_hijos: Mapped[List["Componente"]] = relationship(
        "Componente",
        back_populates="componente_padre",
        cascade="all, delete-orphan"
    )
    objetivos: Mapped[List["ObjetivoContrato"]] = relationship(
        "ObjetivoContrato",
        back_populates="componente",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Componente(id={self.id}, indice={self.indice})>"


class ObjetivoContrato(Base):
    """
    Objetivos asociados a un componente.
    """
    __tablename__ = "objetivo_contrato"
    __table_args__ = {"schema": get_schema()}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    indice: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    componente_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{get_schema()}.componente.id", ondelete="CASCADE"),
        nullable=True
    )

    # Relaciones
    componente: Mapped[Optional["Componente"]] = relationship(
        "Componente",
        back_populates="objetivos"
    )
    evidencias: Mapped[List["EvidenciaContrato"]] = relationship(
        "EvidenciaContrato",
        back_populates="objetivo_contrato",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ObjetivoContrato(id={self.id}, indice={self.indice})>"


class EvidenciaContrato(Base):
    """
    Evidencias asociadas a objetivos u obligaciones.
    """
    __tablename__ = "evidencia_contrato"
    __table_args__ = {"schema": get_schema()}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    indice: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    objetivo_contrato_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{get_schema()}.objetivo_contrato.id", ondelete="CASCADE"),
        nullable=True
    )
    obligacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{get_schema()}.obligacion.id", ondelete="CASCADE"),
        nullable=True
    )

    # Relaciones
    objetivo_contrato: Mapped[Optional["ObjetivoContrato"]] = relationship(
        "ObjetivoContrato",
        back_populates="evidencias"
    )
    obligacion: Mapped[Optional["Obligacion"]] = relationship(
        "Obligacion",
        back_populates="evidencia_asociada"
    )

    def __repr__(self):
        return f"<EvidenciaContrato(id={self.id}, indice={self.indice})>"


class Contrato(Base):
    """
    Contrato específico de un contratista.
    """
    __tablename__ = "contrato"
    __table_args__ = (
        Index("idx_contrato_perfil_estado", "perfil_contratista_id", "estado"),
        {"schema": get_schema()},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    numero_contrato: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    fecha_inicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    plazo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    objeto: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    valor_contrato: Mapped[Optional[Decimal]] = mapped_column(Double, nullable=True)
    supervisor: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    # Foreign keys
    perfil_contratista_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{get_schema()}.perfil_contratista.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    padre_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{get_schema()}.contrato_inter_administrativo.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Relaciones
    perfil_contratista: Mapped["PerfilContratista"] = relationship(
        "PerfilContratista",
        back_populates="contratos"
    )
    padre: Mapped["ContratoInterAdministrativo"] = relationship(
        "ContratoInterAdministrativo",
        back_populates="contratos"
    )
    informes: Mapped[List["Informe"]] = relationship(
        "Informe",
        back_populates="contrato",
        cascade="all, delete-orphan"
    )
    obligaciones: Mapped[List["Obligacion"]] = relationship(
        "Obligacion",
        back_populates="contrato",
        cascade="all, delete-orphan"
    )


    def __repr__(self):
        return f"<Contrato(id={self.id}, numero={self.numero_contrato})>"


class Obligacion(Base):
    """
    Obligaciones específicas del contrato de un contratista.
    """
    __tablename__ = "obligacion"
    __table_args__ = {"schema": get_schema()}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    indice: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    contrato_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{get_schema()}.contrato.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Relaciones
    contrato: Mapped[Optional["Contrato"]] = relationship(
        "Contrato",
        back_populates="obligaciones"
    )
    ejecuciones: Mapped[List["Ejecucion"]] = relationship(
        "Ejecucion",
        back_populates="obligacion",
        cascade="all, delete-orphan"
    )
    evidencia_asociada: Mapped[List["EvidenciaContrato"]] = relationship(
        "EvidenciaContrato",
        back_populates="obligacion",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Obligacion(id={self.id}, indice={self.indice})>"


class Informe(Base):
    """
    Informes de ejecución asociados a un contrato.
    """
    __tablename__ = "informe"
    __table_args__ = (
        Index("idx_informe_contrato_anio_mes", "contrato_id", "anio", "mes"),
        {"schema": get_schema()},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    valor_periodo: Mapped[Optional[Decimal]] = mapped_column(Double, nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    mes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    anio: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fecha_inicio_periodo: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin_periodo: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    contrato_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{get_schema()}.contrato.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Relaciones
    contrato: Mapped[Optional["Contrato"]] = relationship(
        "Contrato",
        back_populates="informes"
    )
    ejecuciones: Mapped[List["Ejecucion"]] = relationship(
        "Ejecucion",
        back_populates="informe",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Informe(id={self.id}, mes={self.mes}, anio={self.anio})>"


class Ejecucion(Base):
    """
    Registro de la ejecución de una obligación dentro de un informe.
    """
    __tablename__ = "ejecucion"
    __table_args__ = {"schema": get_schema()}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    evidencia_adjunta: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    obligacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{get_schema()}.obligacion.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    informe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{get_schema()}.informe.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relaciones
    obligacion: Mapped["Obligacion"] = relationship(
        "Obligacion",
        back_populates="ejecuciones"
    )
    informe: Mapped["Informe"] = relationship(
        "Informe",
        back_populates="ejecuciones"
    )
    descripciones: Mapped[List["DescripcionEjecucion"]] = relationship(
        "DescripcionEjecucion",
        back_populates="ejecucion",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Ejecucion(id={self.id})>"


class DescripcionEjecucion(Base):
    """
    Descripciones detalladas de una ejecución.
    """
    __tablename__ = "descripcion_ejecucion"
    __table_args__ = {"schema": get_schema()}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    indice: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    ejecucion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{get_schema()}.ejecucion.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relaciones
    ejecucion: Mapped["Ejecucion"] = relationship(
        "Ejecucion",
        back_populates="descripciones"
    )

    def __repr__(self):
        return f"<DescripcionEjecucion(id={self.id}, indice={self.indice})>"

