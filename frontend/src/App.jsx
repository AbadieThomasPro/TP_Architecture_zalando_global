import { useEffect, useState } from 'react'

const euro = new Intl.NumberFormat('fr-FR', {
  style: 'currency',
  currency: 'EUR',
})

const serviceLabels = {
  catalog: 'Catalogue',
  customer: 'Clients',
  order: 'Commandes',
}

async function fetchJson(url, options) {
  const response = await fetch(url, options)
  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json') ? await response.json() : null

  if (!response.ok) {
    throw new Error(data ? JSON.stringify(data) : 'Une erreur est survenue.')
  }

  return data
}

function formatApiError(message) {
  if (!message) {
    return 'Une erreur est survenue.'
  }

  try {
    const parsed = JSON.parse(message)
    if (typeof parsed === 'string') {
      return parsed
    }
    if (Array.isArray(parsed.items)) {
      return parsed.items.join(', ')
    }

    return Object.entries(parsed)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
      .join(' | ')
  } catch {
    return message
  }
}

function formatDate(value) {
  if (!value) {
    return 'Date indisponible'
  }

  return new Intl.DateTimeFormat('fr-FR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function serviceTone(status) {
  return status === 'online' ? 'online' : status === 'offline' ? 'offline' : 'loading'
}

export default function App() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [customers, setCustomers] = useState([])
  const [orders, setOrders] = useState([])
  const [customerAddresses, setCustomerAddresses] = useState([])
  const [selectedCustomer, setSelectedCustomer] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [quantities, setQuantities] = useState({})
  const [serviceStatus, setServiceStatus] = useState({
    catalog: 'loading',
    customer: 'loading',
    order: 'loading',
  })
  const [loading, setLoading] = useState(true)
  const [addressLoading, setAddressLoading] = useState(false)
  const [orderDetailLoading, setOrderDetailLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [activeOrder, setActiveOrder] = useState(null)

  useEffect(() => {
    async function loadStore() {
      setLoading(true)
      setError('')

      const [catalogResult, customerResult, orderResult] = await Promise.allSettled([
        Promise.all([
          fetchJson('/catalog-api/products/'),
          fetchJson('/catalog-api/categories/'),
        ]),
        fetchJson('/customer-api/customers/'),
        fetchJson('/order-api/orders/'),
      ])

      const nextServiceStatus = {
        catalog: catalogResult.status === 'fulfilled' ? 'online' : 'offline',
        customer: customerResult.status === 'fulfilled' ? 'online' : 'offline',
        order: orderResult.status === 'fulfilled' ? 'online' : 'offline',
      }

      setServiceStatus(nextServiceStatus)

      if (catalogResult.status === 'fulfilled') {
        const [productsData, categoriesData] = catalogResult.value
        setProducts(productsData)
        setCategories(categoriesData)
      } else {
        setProducts([])
        setCategories([])
      }

      if (customerResult.status === 'fulfilled') {
        setCustomers(customerResult.value)
      } else {
        setCustomers([])
      }

      if (orderResult.status === 'fulfilled') {
        setOrders(
          [...orderResult.value].sort(
            (left, right) => new Date(right.created_at) - new Date(left.created_at)
          )
        )
      } else {
        setOrders([])
      }

      const failures = Object.entries(nextServiceStatus)
        .filter(([, status]) => status === 'offline')
        .map(([key]) => serviceLabels[key])

      if (failures.length) {
        setError(`Services indisponibles: ${failures.join(', ')}`)
      }

      setLoading(false)
    }

    loadStore()
  }, [])

  useEffect(() => {
    if (!selectedCustomer) {
      setCustomerAddresses([])
      return
    }

    async function loadAddresses() {
      setAddressLoading(true)
      try {
        const data = await fetchJson(`/customer-api/customers/${selectedCustomer}/addresses/`)
        setCustomerAddresses(data)
      } catch {
        setCustomerAddresses([])
      } finally {
        setAddressLoading(false)
      }
    }

    loadAddresses()
  }, [selectedCustomer])

  function updateQuantity(productId, value) {
    const normalized = Math.max(0, Number(value) || 0)
    setQuantities((current) => ({
      ...current,
      [productId]: normalized,
    }))
  }

  async function handleSelectOrder(orderId) {
    setOrderDetailLoading(true)
    setError('')

    try {
      const data = await fetchJson(`/order-api/orders/${orderId}/`)
      setActiveOrder(data)
    } catch (err) {
      setError(formatApiError(err.message))
    } finally {
      setOrderDetailLoading(false)
    }
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    if (!selectedCustomer) {
      setError('Choisis un client avant de valider la commande.')
      return
    }

    if (!selectedItems.length) {
      setError('Ajoute au moins un produit au panier.')
      return
    }

    setSubmitting(true)

    try {
      const createdOrder = await fetchJson('/order-api/orders/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customer_id: Number(selectedCustomer),
          items: selectedItems.map((item) => ({
            product_id: item.id,
            quantity: item.quantity,
          })),
        }),
      })

      setOrders((current) =>
        [createdOrder, ...current.filter((order) => order.id !== createdOrder.id)].sort(
          (left, right) => new Date(right.created_at) - new Date(left.created_at)
        )
      )
      setActiveOrder(createdOrder)
      setQuantities({})
    } catch (err) {
      setError(formatApiError(err.message))
    } finally {
      setSubmitting(false)
    }
  }

  const filteredProducts = products.filter((product) => {
    const query = searchTerm.trim().toLowerCase()
    const matchesCategory = selectedCategory
      ? product.category?.slug === selectedCategory
      : true
    const matchesSearch = query
      ? `${product.name} ${product.description} ${product.category?.name || ''}`
          .toLowerCase()
          .includes(query)
      : true

    return matchesCategory && matchesSearch
  })

  const selectedItems = products
    .map((product) => ({
      ...product,
      quantity: Number(quantities[product.id] || 0),
    }))
    .filter((product) => product.quantity > 0)

  const estimatedTotal = selectedItems.reduce(
    (sum, item) => sum + Number(item.price) * item.quantity,
    0
  )

  const totalUnits = selectedItems.reduce((sum, item) => sum + item.quantity, 0)
  const selectedCustomerDetails = customers.find(
    (customer) => String(customer.id) === selectedCustomer
  )
  const orderCustomer =
    activeOrder && customers.find((customer) => customer.id === activeOrder.customer_id)
  const canSubmit = !submitting && !loading && serviceStatus.order === 'online'

  return (
    <div className="shop-page">
      <header className="site-header">
        <div className="brand">
          <div className="brand-logo">Z</div>
          <div>
            <p className="brand-title">Zalando</p>
            <p className="brand-subtitle">Women, Men, Sneakers & More</p>
          </div>
        </div>

        <div className="header-search">
          <input
            type="search"
            placeholder="Rechercher un produit"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
        </div>

        <div className="header-actions">
          <div className="header-pill">{totalUnits} article(s)</div>
          <div className="header-pill">{euro.format(estimatedTotal)}</div>
        </div>
      </header>

      <section className="shop-toolbar">
        <div className="shop-toolbar-copy">
          <p className="section-label">Boutique</p>
          <h1>Tous les produits</h1>
        </div>

        <div className="shop-toolbar-stats">
          <div className="toolbar-stat">
            <span>Produits</span>
            <strong>{products.length}</strong>
          </div>
          <div className="toolbar-stat">
            <span>Catégories</span>
            <strong>{categories.length}</strong>
          </div>
          <div className="toolbar-stat">
            <span>Panier</span>
            <strong>{totalUnits}</strong>
          </div>
        </div>
      </section>

      <section className="category-bar">
        <button
          type="button"
          className={`category-button ${selectedCategory === '' ? 'active' : ''}`}
          onClick={() => setSelectedCategory('')}
        >
          Tout
        </button>
        {categories.map((category) => (
          <button
            type="button"
            key={category.id}
            className={`category-button ${
              selectedCategory === category.slug ? 'active' : ''
            }`}
            onClick={() => setSelectedCategory(category.slug)}
          >
            {category.name}
          </button>
        ))}
      </section>

      <section className="status-row">
        {Object.entries(serviceStatus).map(([key, status]) => (
          <div key={key} className={`status-chip ${serviceTone(status)}`}>
            <span className="status-dot" />
            {serviceLabels[key]}
          </div>
        ))}
      </section>

      {loading ? <div className="notice info">Chargement de la boutique...</div> : null}
      {error ? <div className="notice error">{error}</div> : null}

      <main className="shop-layout">
        <section className="catalog-section" id="catalogue">
          <div className="section-head">
            <div>
              <p className="section-label">Catalogue</p>
              <h2>{filteredProducts.length} produit(s)</h2>
            </div>
          </div>

          <div className="product-grid">
            {filteredProducts.map((product) => (
              <article key={product.id} className="product-card">
                <div className="product-visual">
                  <span className="product-category">{product.category?.name || 'Produit'}</span>
                  <span className="stock">{product.stock} en stock</span>
                </div>

                <div className="product-body">
                  <h3>{product.name}</h3>
                  <p>{product.description}</p>
                </div>

                <div className="product-footer">
                  <div>
                    <strong>{euro.format(Number(product.price))}</strong>
                    <small>{product.is_active ? 'Disponible' : 'Indisponible'}</small>
                  </div>

                  <label className="qty-box">
                    <span>Qté</span>
                    <input
                      type="number"
                      min="0"
                      value={quantities[product.id] || 0}
                      onChange={(event) => updateQuantity(product.id, event.target.value)}
                    />
                  </label>
                </div>
              </article>
            ))}
          </div>
        </section>

        <aside className="sidebar">
          <section className="panel">
            <div className="section-head compact">
              <div>
                <p className="section-label">Client</p>
                <h2>Compte</h2>
              </div>
            </div>

            <select
              value={selectedCustomer}
              onChange={(event) => setSelectedCustomer(event.target.value)}
              className="customer-select"
            >
              <option value="">Choisir un client</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.first_name} {customer.last_name}
                </option>
              ))}
            </select>

            {selectedCustomerDetails ? (
              <div className="customer-card">
                <strong>
                  {selectedCustomerDetails.first_name} {selectedCustomerDetails.last_name}
                </strong>
                <p>{selectedCustomerDetails.email}</p>
                <span>{selectedCustomerDetails.phone || 'Téléphone non renseigné'}</span>
              </div>
            ) : (
              <p className="empty-text">Aucun client sélectionné.</p>
            )}

            <div className="address-list-wrapper">
              <div className="mini-head">
                <strong>Adresses</strong>
                <span>{addressLoading ? '...' : customerAddresses.length}</span>
              </div>

              {customerAddresses.length ? (
                <ul className="address-list">
                  {customerAddresses.map((address) => (
                    <li key={address.id}>
                      <strong>{address.city}</strong>
                      <span>{address.street}</span>
                      <span>
                        {address.postal_code} • {address.country}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty-text">Aucune adresse chargée.</p>
              )}
            </div>
          </section>

          <section className="panel">
            <div className="section-head compact">
              <div>
                <p className="section-label">Panier</p>
                <h2>Shopping bag</h2>
              </div>
              <span>{totalUnits} article(s)</span>
            </div>

            <form onSubmit={handleSubmit}>
              {selectedItems.length ? (
                <ul className="cart-list">
                  {selectedItems.map((item) => (
                    <li key={item.id}>
                      <div>
                        <strong>{item.name}</strong>
                        <span>
                          {item.quantity} x {euro.format(Number(item.price))}
                        </span>
                      </div>
                      <em>{euro.format(Number(item.price) * item.quantity)}</em>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="empty-text">Ton panier est vide.</p>
              )}

              <div className="cart-total">
                <span>Total</span>
                <strong>{euro.format(estimatedTotal)}</strong>
              </div>

              <button type="submit" className="checkout-button" disabled={!canSubmit}>
                {submitting ? 'Validation...' : 'Commander'}
              </button>
            </form>
          </section>

          <section className="panel">
            <div className="section-head compact">
              <div>
                <p className="section-label">Commandes</p>
                <h2>Suivi</h2>
              </div>
            </div>

            {orders.length ? (
              <div className="orders-list">
                {orders.slice(0, 5).map((order) => (
                  <button
                    type="button"
                    key={order.id}
                    className={`order-item ${activeOrder?.id === order.id ? 'active' : ''}`}
                    onClick={() => handleSelectOrder(order.id)}
                  >
                    <div>
                      <strong>#{order.id}</strong>
                      <span>{formatDate(order.created_at)}</span>
                    </div>
                    <em>{euro.format(Number(order.total_amount))}</em>
                  </button>
                ))}
              </div>
            ) : (
              <p className="empty-text">Aucune commande.</p>
            )}

            <div className="order-preview">
              {orderDetailLoading ? (
                <p className="empty-text">Chargement...</p>
              ) : activeOrder ? (
                <>
                  <div className="preview-head">
                    <strong>Commande #{activeOrder.id}</strong>
                    <span>{activeOrder.status}</span>
                  </div>
                  <p className="preview-customer">
                    {orderCustomer
                      ? `${orderCustomer.first_name} ${orderCustomer.last_name}`
                      : `Client #${activeOrder.customer_id}`}
                  </p>
                  <ul className="preview-lines">
                    {activeOrder.items?.map((item) => (
                      <li key={`${activeOrder.id}-${item.product_id}`}>
                        <span>
                          {item.product_name} x {item.quantity}
                        </span>
                        <strong>{euro.format(Number(item.line_total))}</strong>
                      </li>
                    ))}
                  </ul>
                  <div className="preview-total">
                    <span>Total</span>
                    <strong>{euro.format(Number(activeOrder.total_amount))}</strong>
                  </div>
                </>
              ) : (
                <p className="empty-text">Sélectionne une commande pour voir le détail.</p>
              )}
            </div>
          </section>
        </aside>
      </main>
    </div>
  )
}
