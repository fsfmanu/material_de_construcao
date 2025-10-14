import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../MetricsDashboard.css';

const MetricsDashboard = () => {
    const [aggregatedMetrics, setAggregatedMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchAggregatedMetrics = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:5000/api/aggregated_metrics');
                setAggregatedMetrics(response.data);
                setLoading(false);
            } catch (err) {
                setError('Erro ao carregar as métricas agregadas.');
                setLoading(false);
            }
        };

        fetchAggregatedMetrics();
    }, []);

    if (loading) {
        return <div className="metrics-dashboard">Carregando dashboard de métricas...</div>;
    }

    if (error) {
        return <div className="metrics-dashboard error-message">Erro: {error}</div>;
    }

    if (!aggregatedMetrics) {
        return <div className="metrics-dashboard">Nenhuma métrica agregada disponível.</div>;
    }

    return (
        <div className="metrics-dashboard">
            <h2>Dashboard de Métricas Avançadas</h2>

            <div className="metric-card-container">
                <div className="metric-card">
                    <h3>Total de Eventos</h3>
                    <p>{aggregatedMetrics.total_events}</p>
                </div>
                <div className="metric-card">
                    <h3>Usuários Únicos</h3>
                    <p>{aggregatedMetrics.unique_users}</p>
                </div>
                {aggregatedMetrics.reviewer_approval_rate && (
                    <div className="metric-card">
                        <h3>Aprovações do Revisor</h3>
                        <p>{aggregatedMetrics.reviewer_approval_rate.approved || 0} aprovados</p>
                        <p>{aggregatedMetrics.reviewer_approval_rate.rejected || 0} rejeitados</p>
                    </div>
                )}
            </div>

            <h3>Eventos por Tipo</h3>
            {Object.keys(aggregatedMetrics.events_by_type).length > 0 ? (
                <ul>
                    {Object.entries(aggregatedMetrics.events_by_type).map(([type, count]) => (
                        <li key={type}><strong>{type}:</strong> {count}</li>
                    ))}
                </ul>
            ) : (
                <p>Nenhum evento por tipo registrado.</p>
            )}

            <h3>Eventos por Dia</h3>
            {Object.keys(aggregatedMetrics.events_by_day).length > 0 ? (
                <ul>
                    {Object.entries(aggregatedMetrics.events_by_day).map(([day, count]) => (
                        <li key={day}><strong>{day}:</strong> {count}</li>
                    ))}
                </ul>
            ) : (
                <p>Nenhum evento por dia registrado.</p>
            )}

            <h3>Top 5 Pesquisas</h3>
            {Object.keys(aggregatedMetrics.top_search_queries).length > 0 ? (
                <ol>
                    {Object.entries(aggregatedMetrics.top_search_queries).map(([query, count]) => (
                        <li key={query}>{query} ({count})</li>
                    ))}
                </ol>
            ) : (
                <p>Nenhuma pesquisa registrada.</p>
            )}

            <h3>Top 5 Produtos Visualizados</h3>
            {Object.keys(aggregatedMetrics.top_products_viewed).length > 0 ? (
                <ol>
                    {Object.entries(aggregatedMetrics.top_products_viewed).map(([product, count]) => (
                        <li key={product}>{product} ({count})</li>
                    ))}
                </ol>
            ) : (
                <p>Nenhum produto visualizado.</p>
            )}

            <h3>Top 5 Requisições de Recomendação</h3>
            {Object.keys(aggregatedMetrics.top_recommendation_requests).length > 0 ? (
                <ol>
                    {Object.entries(aggregatedMetrics.top_recommendation_requests).map(([req, count]) => (
                        <li key={req}>{req} ({count})</li>
                    ))}
                </ol>
            ) : (
                <p>Nenhuma requisição de recomendação registrada.</p>
            )}

        </div>
    );
};

export default MetricsDashboard;

