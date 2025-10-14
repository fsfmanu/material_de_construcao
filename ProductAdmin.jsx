import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Textarea } from '@/components/ui/textarea.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx';
import { Plus, Edit, Trash2, Download, Upload, Save, X } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

function ProductAdmin() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newProduct, setNewProduct] = useState({
    name: '',
    brand: '',
    category: 'Tinta Acrílica',
    type: 'Residencial',
    description: '',
    coverage: '',
    drying_time: '',
    dilution: '',
    application_tools: [],
    use_case: [],
    features: [],
    colors: [],
    packages: [{ size: '', price: 0, stock: 0 }]
  });

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/products`);
      if (response.ok) {
        const data = await response.json();
        setProducts(data.products || []);
      }
    } catch (error) {
      console.error('Erro ao carregar produtos:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddProduct = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/products`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newProduct),
      });

      if (response.ok) {
        await loadProducts();
        setShowAddDialog(false);
        setNewProduct({
          name: '',
          brand: '',
          category: 'Tinta Acrílica',
          type: 'Residencial',
          description: '',
          coverage: '',
          drying_time: '',
          dilution: '',
          application_tools: [],
          use_case: [],
          features: [],
          colors: [],
          packages: [{ size: '', price: 0, stock: 0 }]
        });
        alert('Produto adicionado com sucesso!');
      } else {
        alert('Erro ao adicionar produto');
      }
    } catch (error) {
      console.error('Erro ao adicionar produto:', error);
      alert('Erro ao adicionar produto');
    }
  };

  const handleUpdateProduct = async (productId, updates) => {
    try {
      const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (response.ok) {
        await loadProducts();
        setEditingProduct(null);
        alert('Produto atualizado com sucesso!');
      } else {
        alert('Erro ao atualizar produto');
      }
    } catch (error) {
      console.error('Erro ao atualizar produto:', error);
      alert('Erro ao atualizar produto');
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (confirm('Tem certeza que deseja remover este produto?')) {
      try {
        const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
          method: 'DELETE',
        });

        if (response.ok) {
          await loadProducts();
          alert('Produto removido com sucesso!');
        } else {
          alert('Erro ao remover produto');
        }
      } catch (error) {
        console.error('Erro ao remover produto:', error);
        alert('Erro ao remover produto');
      }
    }
  };

  const handleExportCatalog = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/catalog/export`);
      if (response.ok) {
        const catalog = await response.json();
        const blob = new Blob([JSON.stringify(catalog, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'catalogo_produtos.json';
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Erro ao exportar catálogo:', error);
      alert('Erro ao exportar catálogo');
    }
  };

  const handleImportCatalog = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        const text = await file.text();
        const catalog = JSON.parse(text);
        
        const response = await fetch(`${API_BASE_URL}/catalog/import`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(catalog),
        });

        if (response.ok) {
          await loadProducts();
          alert('Catálogo importado com sucesso!');
        } else {
          alert('Erro ao importar catálogo');
        }
      } catch (error) {
        console.error('Erro ao importar catálogo:', error);
        alert('Erro ao importar catálogo - verifique o formato do arquivo');
      }
    }
  };

  const addPackage = (productData, setProductData) => {
    const newPackages = [...productData.packages, { size: '', price: 0, stock: 0 }];
    setProductData({ ...productData, packages: newPackages });
  };

  const removePackage = (productData, setProductData, index) => {
    const newPackages = productData.packages.filter((_, i) => i !== index);
    setProductData({ ...productData, packages: newPackages });
  };

  const updatePackage = (productData, setProductData, index, field, value) => {
    const newPackages = [...productData.packages];
    newPackages[index] = { ...newPackages[index], [field]: value };
    setProductData({ ...productData, packages: newPackages });
  };

  const ProductForm = ({ product, setProduct, onSave, onCancel, title }) => (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Nome do Produto</label>
            <Input
              value={product.name}
              onChange={(e) => setProduct({ ...product, name: e.target.value })}
              placeholder="Ex: Coral Acrílica Premium"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Marca</label>
            <Input
              value={product.brand}
              onChange={(e) => setProduct({ ...product, brand: e.target.value })}
              placeholder="Ex: Coral"
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Categoria</label>
            <Select value={product.category} onValueChange={(value) => setProduct({ ...product, category: value })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Tinta Acrílica">Tinta Acrílica</SelectItem>
                <SelectItem value="Esmalte">Esmalte</SelectItem>
                <SelectItem value="Primer">Primer</SelectItem>
                <SelectItem value="Verniz">Verniz</SelectItem>
                <SelectItem value="Textura">Textura</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Tipo</label>
            <Select value={product.type} onValueChange={(value) => setProduct({ ...product, type: value })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Residencial">Residencial</SelectItem>
                <SelectItem value="Automotiva">Automotiva</SelectItem>
                <SelectItem value="Industrial">Industrial</SelectItem>
                <SelectItem value="Preparação">Preparação</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Rendimento</label>
            <Input
              value={product.coverage}
              onChange={(e) => setProduct({ ...product, coverage: e.target.value })}
              placeholder="Ex: 12 m²/L"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Descrição</label>
          <Textarea
            value={product.description}
            onChange={(e) => setProduct({ ...product, description: e.target.value })}
            placeholder="Descrição detalhada do produto"
            rows={3}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Tempo de Secagem</label>
            <Input
              value={product.drying_time}
              onChange={(e) => setProduct({ ...product, drying_time: e.target.value })}
              placeholder="Ex: 2 horas ao toque"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Diluição</label>
            <Input
              value={product.dilution}
              onChange={(e) => setProduct({ ...product, dilution: e.target.value })}
              placeholder="Ex: Até 20% com água"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Características (separadas por vírgula)</label>
          <Input
            value={Array.isArray(product.features) ? product.features.join(', ') : ''}
            onChange={(e) => setProduct({ ...product, features: e.target.value.split(', ').filter(f => f.trim()) })}
            placeholder="Ex: Lavável, Antimofo, Sem cheiro"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Casos de Uso (separados por vírgula)</label>
          <Input
            value={Array.isArray(product.use_case) ? product.use_case.join(', ') : ''}
            onChange={(e) => setProduct({ ...product, use_case: e.target.value.split(', ').filter(u => u.trim()) })}
            placeholder="Ex: Internas, Externas, Alvenaria"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Embalagens e Preços</label>
          {product.packages?.map((pkg, index) => (
            <div key={index} className="flex gap-2 mb-2 items-center">
              <Input
                placeholder="Tamanho (ex: 3.6L)"
                value={pkg.size}
                onChange={(e) => updatePackage(product, setProduct, index, 'size', e.target.value)}
                className="w-32"
              />
              <Input
                type="number"
                placeholder="Preço"
                value={pkg.price}
                onChange={(e) => updatePackage(product, setProduct, index, 'price', parseFloat(e.target.value) || 0)}
                className="w-32"
              />
              <Input
                type="number"
                placeholder="Estoque"
                value={pkg.stock}
                onChange={(e) => updatePackage(product, setProduct, index, 'stock', parseInt(e.target.value) || 0)}
                className="w-32"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => removePackage(product, setProduct, index)}
                disabled={product.packages.length === 1}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
          <Button
            variant="outline"
            size="sm"
            onClick={() => addPackage(product, setProduct)}
          >
            <Plus className="h-4 w-4 mr-2" />
            Adicionar Embalagem
          </Button>
        </div>

        <div className="flex gap-2 pt-4">
          <Button onClick={onSave}>
            <Save className="h-4 w-4 mr-2" />
            Salvar
          </Button>
          <Button variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  if (editingProduct) {
    return (
      <div className="p-6">
        <ProductForm
          product={editingProduct}
          setProduct={setEditingProduct}
          onSave={() => handleUpdateProduct(editingProduct.id, editingProduct)}
          onCancel={() => setEditingProduct(null)}
          title="Editar Produto"
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Gerenciamento de Produtos
            <div className="flex gap-2">
              <input
                type="file"
                accept=".json"
                onChange={handleImportCatalog}
                style={{ display: 'none' }}
                id="import-file"
              />
              <Button
                variant="outline"
                onClick={() => document.getElementById('import-file').click()}
              >
                <Upload className="h-4 w-4 mr-2" />
                Importar
              </Button>
              <Button variant="outline" onClick={handleExportCatalog}>
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
              <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Novo Produto
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Adicionar Novo Produto</DialogTitle>
                  </DialogHeader>
                  <ProductForm
                    product={newProduct}
                    setProduct={setNewProduct}
                    onSave={handleAddProduct}
                    onCancel={() => setShowAddDialog(false)}
                    title=""
                  />
                </DialogContent>
              </Dialog>
            </div>
          </CardTitle>
          <CardDescription>
            Gerencie seu catálogo de produtos, preços e características
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">Carregando produtos...</div>
          ) : (
            <div className="grid gap-4">
              {products.map((product) => (
                <Card key={product.id} className="p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-semibold text-lg">{product.name}</h3>
                        <Badge variant="secondary">{product.brand}</Badge>
                        <Badge variant="outline">{product.category}</Badge>
                      </div>
                      <p className="text-gray-600 mb-2">{product.description}</p>
                      <div className="flex flex-wrap gap-1 mb-2">
                        {product.features?.slice(0, 4).map((feature, idx) => (
                          <Badge key={idx} variant="secondary" className="text-xs">
                            {feature}
                          </Badge>
                        ))}
                      </div>
                      <div className="text-sm text-gray-500">
                        Rendimento: {product.coverage} | Embalagens: {product.packages?.length || 0}
                      </div>
                      <div className="flex gap-2 mt-2">
                        {product.packages?.map((pkg, idx) => (
                          <span key={idx} className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
                            {pkg.size}: R$ {pkg.price.toFixed(2)}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setEditingProduct(product)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteProduct(product.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default ProductAdmin;
