const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'
export type Product = {
  id: number
  barcode: string
  name: string
  category_id: number | null
  unit: string
  cost_price: string
  sale_price: string
  stock_qty: string
  min_stock: string
  active: boolean
}
export function getToken() { return sessionStorage.getItem('superas_token') }
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? `Erro HTTP ${response.status}`)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}
