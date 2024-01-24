from ...base import helpers as base_repo_helpers, enums as base_repo_enums


def generate_chat_id():
    return base_repo_helpers.generate_model_id(base_repo_enums.ModelPrefixEnum.CHAT)


def generate_message_id():
    return base_repo_helpers.generate_model_id(base_repo_enums.ModelPrefixEnum.MESSAGE)


def generate_receipt_id():
    return base_repo_helpers.generate_model_id(base_repo_enums.ModelPrefixEnum.RECEIPT)
