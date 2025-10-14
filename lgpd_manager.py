
import datetime
from supabase_client import supabase_manager
import hashlib

def anonymize_user_data(user_id: str) -> bool:
    """Anonimiza os dados de um usuário no sistema."""
    if not supabase_manager.is_connected():
        print("Não conectado ao Supabase. Não é possível anonimizar dados.")
        return False

    try:
        # Exemplo: Anonimizar conversas e mensagens associadas ao user_id
        # Em um cenário real, isso seria mais complexo e envolveria todas as tabelas com PII.
        
        # Buscar conversas do usuário
        conversations_response = supabase_manager.client.from_("conversations").select("id").eq("user_id", user_id).execute()
        conversation_ids = [c["id"] for c in conversations_response.data]

        if conversation_ids:
            # Anonimizar mensagens
            supabase_manager.client.from_("messages").update({"content": "[DADOS ANONIMIZADOS]", "metadata": {}}).in_("conversation_id", conversation_ids).execute()
            # Anonimizar conversas
            supabase_manager.client.from_("conversations").update({"phone_number": "[ANONIMIZADO]", "user_id": "[ANONIMIZADO]"}).in_("id", conversation_ids).execute()
        
        # Registrar evento de anonimização
        supabase_manager.log_activity(
            "lgpd_anonymization",
            "user",
            user_id,
            {"action": "anonymized_data"}
        )
        print(f"Dados do usuário {user_id} anonimizados com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao anonimizar dados do usuário {user_id}: {e}")
        return False

def delete_user_data(user_id: str) -> bool:
    """Exclui permanentemente os dados de um usuário do sistema."""
    if not supabase_manager.is_connected():
        print("Não conectado ao Supabase. Não é possível excluir dados.")
        return False

    try:
        # Buscar conversas do usuário
        conversations_response = supabase_manager.client.from_("conversations").select("id").eq("user_id", user_id).execute()
        conversation_ids = [c["id"] for c in conversations_response.data]

        if conversation_ids:
            # Excluir mensagens
            supabase_manager.client.from_("messages").delete().in_("conversation_id", conversation_ids).execute()
            # Excluir orçamentos
            supabase_manager.client.from_("quotes").delete().in_("conversation_id", conversation_ids).execute()
            # Excluir feedback
            supabase_manager.client.from_("feedback").delete().in_("conversation_id", conversation_ids).execute()
            # Excluir conversas
            supabase_manager.client.from_("conversations").delete().in_("id", conversation_ids).execute()
        
        # Excluir registros de consentimento
        supabase_manager.client.from_("user_consent").delete().eq("user_id", user_id).execute()

        # Registrar evento de exclusão
        supabase_manager.log_activity(
            "lgpd_data_deletion",
            "user",
            user_id,
            {"action": "deleted_data"}
        )
        print(f"Dados do usuário {user_id} excluídos com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao excluir dados do usuário {user_id}: {e}")
        return False

def record_consent(user_id: str, consent_type: str, granted: bool, metadata: dict = None) -> bool:
    """Registra ou atualiza o consentimento de um usuário."""
    if not supabase_manager.is_connected():
        print("Não conectado ao Supabase. Não é possível registrar consentimento.")
        return False

    try:
        data = {
            "user_id": user_id,
            "consent_type": consent_type,
            "granted": granted,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "metadata": metadata
        }
        response = supabase_manager.client.from_("user_consent").upsert(data, on_conflict="user_id,consent_type").execute()
        
        if response.data:
            supabase_manager.log_activity(
                "lgpd_consent_record",
                "user",
                user_id,
                {"consent_type": consent_type, "granted": granted}
            )
            print(f"Consentimento para {consent_type} de {user_id} registrado: {granted}.")
            return True
        else:
            print(f"Erro ao registrar consentimento para {user_id}: {response.error}")
            return False
    except Exception as e:
        print(f"Exceção ao registrar consentimento para {user_id}: {e}")
        return False

def get_consent_status(user_id: str, consent_type: str) -> bool:
    """Verifica o status de consentimento de um usuário para um tipo específico."""
    if not supabase_manager.is_connected():
        print("Não conectado ao Supabase. Não é possível verificar consentimento.")
        return False

    try:
        response = supabase_manager.client.from_("user_consent").select("granted").eq("user_id", user_id).eq("consent_type", consent_type).single().execute()
        if response.data:
            return response.data["granted"]
        return False
    except Exception as e:
        print(f"Erro ao buscar status de consentimento para {user_id} e {consent_type}: {e}")
        return False

