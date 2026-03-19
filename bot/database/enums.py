from enum import Enum


class LeadStatus(str, Enum):

    NEW = "new"

    PROCESSED = "processed"

    SENT_TO_CRM = "sent_to_crm"

    REJECTED = "rejected"
