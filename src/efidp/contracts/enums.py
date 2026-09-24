"""Standardized enumerations for EFIDP data contracts and source schemas."""

from enum import StrEnum


class SourceClassification(StrEnum):
    """Classification of data origin ensuring synthetic data is never confused with real data."""

    REAL_PUBLIC = "real_public"
    SYNTHETIC = "synthetic"
    DERIVED = "derived"


class Frequency(StrEnum):
    """Observation frequency for macroeconomic indicators and time-series data."""

    ANNUAL = "ANNUAL"
    SEMI_ANNUAL = "SEMI_ANNUAL"
    QUARTERLY = "QUARTERLY"
    MONTHLY = "MONTHLY"
    DAILY = "DAILY"


class ChannelType(StrEnum):
    """Financial transaction channels in the Egyptian retail banking and payments ecosystem."""

    INSTAPAY = "InstaPay"
    POS = "POS"
    MOBILE_WALLET = "Mobile_Wallet"
    ATM = "ATM"
    WEB = "Web"


class TransactionStatus(StrEnum):
    """Status lifecycle of a financial transaction event."""

    COMPLETED = "COMPLETED"
    DECLINED = "DECLINED"
    REVERSED = "REVERSED"


class TransactionCategory(StrEnum):
    """Merchant and transaction category classifications."""

    RETAIL = "Retail"
    GROCERIES = "Groceries"
    UTILITIES = "Utilities"
    HEALTHCARE = "Healthcare"
    GOVERNMENT_FEES = "Government_Fees"
    ENTERTAINMENT = "Entertainment"
    EDUCATION = "Education"
    TRANSPORT = "Transport"


class Governorate(StrEnum):
    """The 27 official administrative governorates of the Arab Republic of Egypt."""

    CAIRO = "Cairo"
    GIZA = "Giza"
    ALEXANDRIA = "Alexandria"
    DAKAHLIA = "Dakahlia"
    RED_SEA = "Red Sea"
    BEHEIRA = "Beheira"
    FAYOUM = "Fayoum"
    GHARBIA = "Gharbia"
    ISMAILIA = "Ismailia"
    MENOFIA = "Menofia"
    MINYA = "Minya"
    QALIOUBIA = "Qalioubia"
    NEW_VALLEY = "New Valley"
    SUEZ = "Suez"
    ASWAN = "Aswan"
    ASSIUT = "Assiut"
    BENI_SUEF = "Beni Suef"
    PORT_SAID = "Port Said"
    DAMIETTA = "Damietta"
    SHARQIA = "Sharqia"
    SOUTH_SINAI = "South Sinai"
    NORTH_SINAI = "North Sinai"
    SOHAG = "Sohag"
    QENA = "Qena"
    LUXOR = "Luxor"
    MATROUH = "Matrouh"
    KAFR_EL_SHEIKH = "Kafr El-Sheikh"


class ConnectorType(StrEnum):
    """Underlying protocol or connection type for data sources."""

    API = "api"
    FILE = "file"
    STREAMING = "streaming"
    MOCK = "mock"
