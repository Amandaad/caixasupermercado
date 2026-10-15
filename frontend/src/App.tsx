import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api, getToken } from './api'
import type { Product } from './api'

type Me = { id: number; username: string; role: string }
const money = (value: string | number) => Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

export default function App() {
  const [token, setToken] = useState(getToken())
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('')
  const [me, setMe] = useState<Me | null>(null)
  const [products, setProducts] = useState<Product[]>([])
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  const [form, setForm] = useState({ barcode: '', name: '', unit: 'UN', cost_price: '0.00', sale_price: '', stock_qty: '0', min_stock: '0' })

  const loadProducts = useCallback(async () => {
    if (!token) return
    try {
      const data = await api<Product[]>(`/products?search=${encodeURIComponent(search)}`)
      setProducts(data)
    } catch (e) { setError(e instanceof Error ? e.message : 'Falha ao carregar produtos') }
  }, [token, search])

  useEffect(() => {
    if (!token) return
    api<Me>('/auth/me').then(setMe).catch(() => {
      sessionStorage.removeItem('superas_token'); setToken(null); setMe(null)
    })
  }, [token])

  useEffect(() => { void loadProducts() }, [loadProducts])

  async function login(event: FormEvent) {
    event.preventDefault(); setError(''); setBusy(true)
    try {
      const result = await api<{ access_token: string }>('/auth/login', {
        method: 'POST', body: JSON.stringify({ username, password }),
      })
      sessionStorage.setItem('superas_token', result.access_token)
      setToken(result.access_token); setPassword('')
    } catch (e) { setError(e instanceof Error ? e.message : 'Não foi possível entrar') }
    finally { setBusy(false) }
  }

  async function createProduct(event: FormEvent) {
    event.preventDefault(); setError(''); setNotice(''); setBusy(true)
    try {
      await api<Product>('/products', { method: 'POST', body: JSON.stringify(form) })
      setForm({ barcode: '', name: '', unit: 'UN', cost_price: '0.00', sale_price: '', stock_qty: '0', min_stock: '0' })
      setNotice('Produto cadastrado com sucesso.')
      await loadProducts()
    } catch (e) { setError(e instanceof Error ? e.message : 'Não foi possível cadastrar') }
    finally { setBusy(false) }
  }

  function logout() {
    sessionStorage.removeItem('superas_token'); setToken(null); setMe(null); setProducts([])
  }

  if (!token) return <main className="login-wrap">
    <form className="login-card" onSubmit={login}>
      <div className="brand-mark">AS</div>
      <p className="eyebrow">GESTÃO DE SUPERMERCADO</p>
      <h1>Super AS</h1>
      <p className="muted">Entre para administrar produtos e estoque.</p>
      {error && <div className="alert error">{error}</div>}
      <label>Usuário<input value={username} onChange={e => setUsername(e.target.value)} autoComplete="username" required /></label>
      <label>Senha<input type="password" value={password} onChange={e => setPassword(e.target.value)} autoComplete="current-password" required /></label>
      <button className="primary full" disabled={busy}>{busy ? 'Entrando…' : 'Entrar'}</button>
      <p className="tiny">Credenciais iniciais: use os valores definidos no seu arquivo .env.</p>
    </form>
  </main>

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand-row"><div className="brand-mark small">AS</div><div><strong>Super AS</strong><span>Gestão de supermercado</span></div></div>
      <div className="nav-label">PRINCIPAL</div>
      <div className="nav-item selected">▦ <span>Produtos e estoque</span></div>
      <div className="nav-item disabled">▣ <span>Frente de caixa</span><small>Em breve</small></div>
      <div className="nav-item disabled">▤ <span>Compras</span><small>Em breve</small></div>
      <div className="nav-item disabled">◷ <span>Relatórios</span><small>Em breve</small></div>
      <div className="sidebar-bottom"><span className="status-dot"/> API conectada quando autenticada <button className="logout" onClick={logout}>Sair</button></div>
    </aside>
    <main className="content">
      <header className="topbar"><div><p className="eyebrow">PAINEL ADMINISTRATIVO</p><h1>Produtos e estoque</h1></div><div className="user-pill">● {me?.username ?? username}</div></header>
      {error && <div className="alert error">{error}<button onClick={() => setError('')}>Fechar</button></div>}
      {notice && <div className="alert success">{notice}<button onClick={() => setNotice('')}>Fechar</button></div>}
      <section className="stats">
        <div className="stat-card"><span>Produtos nesta lista</span><strong>{products.length}</strong><small>Máximo de 100 por consulta</small></div>
        <div className="stat-card"><span>Estoque baixo</span><strong>{products.filter(p => Number(p.stock_qty) <= Number(p.min_stock)).length}</strong><small>Comparação com estoque mínimo</small></div>
        <div className="stat-card"><span>Valor de venda em estoque</span><strong>{money(products.reduce((sum, p) => sum + Number(p.stock_qty) * Number(p.sale_price), 0))}</strong><small>Somente produtos listados</small></div>
      </section>
      <section className="panel">
        <div className="panel-heading"><div><h2>Cadastrar produto</h2><p>Preencha os dados básicos da mercadoria.</p></div></div>
        <form className="product-form" onSubmit={createProduct}>
          <label>Código de barras<input value={form.barcode} onChange={e => setForm({ ...form, barcode: e.target.value })} maxLength={64} required /></label>
          <label>Nome do produto<input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} maxLength={180} required /></label>
          <label>Unidade<select value={form.unit} onChange={e => setForm({ ...form, unit: e.target.value })}><option>UN</option><option>KG</option><option>G</option><option>L</option><option>ML</option><option>PC</option><option>CX</option></select></label>
          <label>Custo (R$)<input type="number" min="0" step="0.01" value={form.cost_price} onChange={e => setForm({ ...form, cost_price: e.target.value })} required /></label>
          <label>Preço de venda (R$)<input type="number" min="0" step="0.01" value={form.sale_price} onChange={e => setForm({ ...form, sale_price: e.target.value })} required /></label>
          <label>Estoque inicial<input type="number" min="0" step="0.001" value={form.stock_qty} onChange={e => setForm({ ...form, stock_qty: e.target.value })} required /></label>
          <label>Estoque mínimo<input type="number" min="0" step="0.001" value={form.min_stock} onChange={e => setForm({ ...form, min_stock: e.target.value })} required /></label>
          <div className="form-action"><button className="primary" disabled={busy}>{busy ? 'Salvando…' : '＋ Cadastrar produto'}</button></div>
        </form>
      </section>
      <section className="panel">
        <div className="panel-heading list-heading"><div><h2>Catálogo de produtos</h2><p>Pesquise por nome ou código de barras.</p></div><input className="search" placeholder="Buscar produto…" value={search} onChange={e => setSearch(e.target.value)} /></div>
        <div className="table-scroll"><table><thead><tr><th>Produto</th><th>Código</th><th>Un.</th><th>Custo</th><th>Venda</th><th>Estoque</th><th>Status</th></tr></thead>
          <tbody>{products.map(p => <tr key={p.id}><td><strong>{p.name}</strong></td><td>{p.barcode}</td><td>{p.unit}</td><td>{money(p.cost_price)}</td><td>{money(p.sale_price)}</td><td>{p.stock_qty}</td><td><span className={`tag ${Number(p.stock_qty) <= Number(p.min_stock) ? 'warning' : 'ok'}`}>{Number(p.stock_qty) <= Number(p.min_stock) ? 'Estoque baixo' : p.active ? 'Ativo' : 'Inativo'}</span></td></tr>)}
          {products.length === 0 && <tr><td colSpan={7} className="empty">Nenhum produto encontrado. Cadastre o primeiro acima.</td></tr>}</tbody>
        </table></div>
      </section>
      <footer>Super AS · MVP 0.1.0 · Integração fiscal ainda não configurada</footer>
    </main>
  </div>
}
