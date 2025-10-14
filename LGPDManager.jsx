
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card.jsx';
import { Button } from '@/components/ui/button.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Label } from '@/components/ui/label.jsx';
import { Switch } from '@/components/ui/switch.jsx';
import { toast } from 'sonner';

const API_BASE_URL = 'http://localhost:5000/api';

const LGPDManager = () => {
    const [userId, setUserId] = useState('');
    const [consentType, setConsentType] = useState('data_processing');
    const [granted, setGranted] = useState(false);
    const [currentConsentStatus, setCurrentConsentStatus] = useState(null);

    const handleRecordConsent = async () => {
        if (!userId || !consentType) {
            toast.error('Por favor, preencha o ID do Usuário e o Tipo de Consentimento.');
            return;
        }
        try {
            const response = await axios.post(`${API_BASE_URL}/lgpd/consent`, {
                user_id: userId,
                consent_type: consentType,
                granted: granted,
                metadata: { source: 'frontend_manager' }
            });
            toast.success(response.data.message);
            checkConsentStatus();
        } catch (error) {
            toast.error('Erro ao registrar consentimento: ' + (error.response?.data?.error || error.message));
        }
    };

    const checkConsentStatus = async () => {
        if (!userId || !consentType) {
            setCurrentConsentStatus(null);
            return;
        }
        try {
            const response = await axios.get(`${API_BASE_URL}/lgpd/consent/${userId}/${consentType}`);
            setCurrentConsentStatus(response.data.granted ? 'Concedido' : 'Negado');
        } catch (error) {
            setCurrentConsentStatus('Não encontrado ou erro');
            toast.error('Erro ao verificar consentimento: ' + (error.response?.data?.error || error.message));
        }
    };

    const handleAnonymizeData = async () => {
        if (!userId) {
            toast.error('Por favor, preencha o ID do Usuário para anonimizar.');
            return;
        }
        if (!window.confirm(`Tem certeza que deseja anonimizar os dados do usuário ${userId}? Esta ação é irreversível.`)) {
            return;
        }
        try {
            const response = await axios.post(`${API_BASE_URL}/lgpd/anonymize/${userId}`);
            toast.success(response.data.message);
        } catch (error) {
            toast.error('Erro ao anonimizar dados: ' + (error.response?.data?.error || error.message));
        }
    };

    const handleDeleteData = async () => {
        if (!userId) {
            toast.error('Por favor, preencha o ID do Usuário para excluir.');
            return;
        }
        if (!window.confirm(`Tem certeza que deseja EXCLUIR permanentemente os dados do usuário ${userId}? Esta ação é irreversível.`)) {
            return;
        }
        try {
            const response = await axios.delete(`${API_BASE_URL}/lgpd/delete/${userId}`);
            toast.success(response.data.message);
        } catch (error) {
            toast.error('Erro ao excluir dados: ' + (error.response?.data?.error || error.message));
        }
    };

    useEffect(() => {
        if (userId && consentType) {
            checkConsentStatus();
        }
    }, [userId, consentType]);

    return (
        <div className="lgpd-manager space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Gerenciamento de Consentimento LGPD</CardTitle>
                    <CardDescription>Registre e verifique o consentimento dos usuários para processamento de dados.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="lgpd-user-id">ID do Usuário</Label>
                            <Input
                                id="lgpd-user-id"
                                value={userId}
                                onChange={(e) => setUserId(e.target.value)}
                                placeholder="Ex: user_123"
                            />
                        </div>
                        <div>
                            <Label htmlFor="consent-type">Tipo de Consentimento</Label>
                            <Input
                                id="consent-type"
                                value={consentType}
                                onChange={(e) => setConsentType(e.target.value)}
                                placeholder="Ex: data_processing, marketing_emails"
                            />
                        </div>
                    </div>
                    <div className="flex items-center space-x-2">
                        <Switch
                            id="consent-granted"
                            checked={granted}
                            onCheckedChange={setGranted}
                        />
                        <Label htmlFor="consent-granted">Consentimento Concedido</Label>
                    </div>
                    <Button onClick={handleRecordConsent}>Registrar/Atualizar Consentimento</Button>
                    {currentConsentStatus && (
                        <p className="text-sm text-gray-600">Status atual do consentimento para {consentType}: <strong>{currentConsentStatus}</strong></p>
                    )}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Operações de Dados LGPD</CardTitle>
                    <CardDescription>Anonimize ou exclua dados de usuários conforme solicitações de privacidade.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-sm text-red-600">Atenção: Estas ações são irreversíveis e devem ser usadas com cautela.</p>
                    <Button variant="destructive" onClick={handleAnonymizeData}>Anonimizar Dados do Usuário</Button>
                    <Button variant="destructive" onClick={handleDeleteData}>Excluir Dados do Usuário</Button>
                </CardContent>
            </Card>
        </div>
    );
};

export default LGPDManager;

