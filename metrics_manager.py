import datetime
from supabase_client import supabase_manager
from collections import defaultdict

def track_event(event_name: str, user_id: str = None, product_id: str = None, metadata: dict = None):
    """Registra um evento no sistema de métricas."""
    data = {
        "event_name": event_name,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "user_id": user_id,
        "product_id": product_id,
        "metadata": metadata
    }
    try:
        response = supabase_manager.client.from_("metrics").insert([data]).execute()
        if response.data:
            print(f"Evento \'{event_name}\' registrado com sucesso.")
            return True
        else:
            print(f"Erro ao registrar evento \'{event_name}\'")
            return False
    except Exception as e:
        print(f"Exceção ao registrar evento \'{event_name}\'": {e}")
        return False

def get_metrics(start_date: str = None, end_date: str = None, event_name: str = None):
    """Recupera métricas do banco de dados."""
    query = supabase_manager.client.from_("metrics").select("*")
    if event_name:
        query = query.eq("event_name", event_name)
    if start_date:
        query = query.gte("timestamp", start_date)
    if end_date:
        query = query.lte("timestamp", end_date)
    
    try:
        response = query.execute()
        if response.data:
            return response.data
        else:
            print(f"Erro ao buscar métricas: {response.error}")
            return []
    except Exception as e:
        print(f"Exceção ao buscar métricas: {e}")
        return []

def get_aggregated_metrics(start_date: str = None, end_date: str = None):
    """Recupera métricas agregadas para o dashboard.

    Returns:
        Dicionário com métricas agregadas.
    """
    all_metrics = get_metrics(start_date, end_date)

    total_events = len(all_metrics)
    events_by_type = defaultdict(int)
    events_by_day = defaultdict(int)
    user_interactions = defaultdict(int)
    product_views = defaultdict(int)
    search_queries = defaultdict(int)
    recommendation_requests = defaultdict(int)
    reviewer_approvals = defaultdict(int)

    for metric in all_metrics:
        event_name = metric["event_name"]
        timestamp_str = metric["timestamp"]
        user_id = metric["user_id"]
        product_id = metric["product_id"]
        metadata = metric["metadata"]

        # Agregação por tipo de evento
        events_by_type[event_name] += 1

        # Agregação por dia
        event_date = datetime.datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")).date()
        events_by_day[str(event_date)] += 1

        # Interações por usuário
        if user_id:
            user_interactions[user_id] += 1

        # Métricas específicas
        if event_name == "product_view" and product_id:
            product_views[product_id] += 1
        elif event_name == "semantic_search" and metadata and "query" in metadata:
            search_queries[metadata["query"]] += 1
        elif event_name == "product_recommendation" and metadata and "requirements" in metadata:
            recommendation_requests[str(metadata["requirements"])] += 1
        elif event_name == "chat_interaction" and metadata and "reviewer_approved" in metadata:
            if metadata["reviewer_approved"]:
                reviewer_approvals["approved"] += 1
            else:
                reviewer_approvals["rejected"] += 1

    return {
        "total_events": total_events,
        "events_by_type": dict(events_by_type),
        "events_by_day": dict(events_by_day),
        "unique_users": len(user_interactions),
        "top_products_viewed": dict(sorted(product_views.items(), key=lambda item: item[1], reverse=True)[:5]),
        "top_search_queries": dict(sorted(search_queries.items(), key=lambda item: item[1], reverse=True)[:5]),
        "top_recommendation_requests": dict(sorted(recommendation_requests.items(), key=lambda item: item[1], reverse=True)[:5]),
        "reviewer_approval_rate": reviewer_approvals
    }

# Exemplo de uso (para testes)
if __name__ == "__main__":
    # Certifique-se de que o Supabase está configurado e acessível para testar
    # track_event("page_view", user_id="user123", metadata={"page": "home"})
    # track_event("semantic_search", user_id="user123", metadata={"query": "tinta lavável"})
    # track_event("product_view", user_id="user456", product_id="prod001", metadata={"product_name": "Tinta Acrílica"})
    # track_event("chat_interaction", user_id="user123", metadata={"reviewer_approved": True})

    # metrics = get_metrics(start_date="2023-01-01T00:00:00Z")
    # print("\n--- Métricas Brutas ---")
    # for m in metrics:
    #     print(m)

    aggregated = get_aggregated_metrics()
    print("\n--- Métricas Agregadas ---")
    print(json.dumps(aggregated, indent=4))

