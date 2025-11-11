# 🚀 Hướng Dẫn Tối Ưu Performance Toàn Diện

## 📋 Mục Lục
1. [Frontend Optimization](#frontend-optimization)
2. [API & Backend Optimization](#api-backend-optimization)
3. [Progress Tracking cho Operations Lớn](#progress-tracking)
4. [Database Optimization](#database-optimization)
5. [Caching Strategy](#caching-strategy)
6. [Monitoring & Analytics](#monitoring-analytics)

---

## 🎨 Frontend Optimization

### 1. Code Splitting & Lazy Loading
```typescript
// Lazy load heavy components
const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  loading: () => <LoadingSkeleton />,
  ssr: false
});
```

### 2. Image Optimization
```javascript
// next.config.js
module.exports = {
  images: {
    domains: ['your-cdn.com'],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200],
    imageSizes: [16, 32, 48, 64, 96],
  },
  // Enable compression
  compress: true,
  // Enable SWC minification
  swcMinify: true,
}
```

### 3. React Query / SWR cho Data Fetching
- Tự động cache
- Revalidate on focus
- Optimistic updates
- Background refetch

### 4. Virtualization cho Large Lists
```typescript
// Sử dụng react-window hoặc @tanstack/react-virtual
import { useVirtualizer } from '@tanstack/react-virtual'
```

### 5. Memoization
```typescript
// Sử dụng React.memo, useMemo, useCallback đúng cách
const MemoizedComponent = React.memo(MyComponent);
const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);
const memoizedCallback = useCallback(() => doSomething(a, b), [a, b]);
```

---

## 🔧 API & Backend Optimization

### 1. Response Compression
```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const response = NextResponse.next();
  // Add compression headers
  response.headers.set('Content-Encoding', 'gzip');
  return response;
}
```

### 2. Pagination & Limit
```typescript
// API routes với pagination
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get('page') || '1');
  const limit = parseInt(searchParams.get('limit') || '50');
  const offset = (page - 1) * limit;
  
  // Query với limit/offset
  const result = await query(`
    SELECT * FROM users 
    ORDER BY created_at DESC
    OFFSET ${offset} ROWS 
    FETCH NEXT ${limit} ROWS ONLY
  `);
  
  return NextResponse.json({
    data: result,
    pagination: { page, limit, total }
  });
}
```

### 3. Parallel Requests
```typescript
// Thực hiện các API calls song song
const [users, projects, keys] = await Promise.all([
  getUsers(),
  getProjects(),
  getElevenLabsKeys()
]);
```

### 4. Request Deduplication
```typescript
// Sử dụng React Query hoặc SWR để tự động dedupe requests
```

---

## 📊 Progress Tracking cho Operations Lớn

### Cách 1: Server-Sent Events (SSE) - Realtime
```typescript
// API Route: /api/bulk-operation/[id]/progress
export async function GET(request: Request, { params }) {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      // Send progress updates
      for (let i = 0; i <= 100; i += 10) {
        const data = `data: ${JSON.stringify({ progress: i, status: 'processing' })}\n\n`;
        controller.enqueue(encoder.encode(data));
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      controller.close();
    }
  });
  
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    }
  });
}
```

### Cách 2: Polling - Simple & Reliable
```typescript
// Frontend: Polling progress
async function trackProgress(operationId: string) {
  const interval = setInterval(async () => {
    const res = await fetch(`/api/operations/${operationId}/status`);
    const { progress, status } = await res.json();
    
    updateUI(progress);
    
    if (status === 'completed' || status === 'failed') {
      clearInterval(interval);
    }
  }, 1000); // Poll every 1 second
}
```

### Cách 3: WebSocket - Best for Real-time
```typescript
// WebSocket connection
const ws = new WebSocket('ws://localhost:3000/progress');
ws.onmessage = (event) => {
  const { progress, message } = JSON.parse(event.data);
  updateProgressBar(progress, message);
};
```

---

## 💾 Database Optimization

### 1. Indexes
```sql
-- Tạo indexes cho các cột thường query
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_elevenlabs_keys_status ON elevenlabs_keys(status);
CREATE INDEX idx_elevenlabs_keys_assigned_user_id ON elevenlabs_keys(assigned_user_id);

-- Composite index cho queries phức tạp
CREATE INDEX idx_keys_user_status ON elevenlabs_keys(assigned_user_id, status);
```

### 2. Connection Pooling
```typescript
// lib/db.ts
import sql from 'mssql';

const config = {
  // ... connection config
  pool: {
    max: 10,
    min: 0,
    idleTimeoutMillis: 30000
  }
};

let pool = null;
export async function getPool() {
  if (!pool) {
    pool = await sql.connect(config);
  }
  return pool;
}
```

### 3. Query Optimization
```typescript
// ❌ BAD: N+1 Query Problem
for (const user of users) {
  user.keys = await getKeysByUserId(user.id);
}

// ✅ GOOD: Single query with JOIN
const usersWithKeys = await query(`
  SELECT u.*, 
    COUNT(k.id) as key_count
  FROM users u
  LEFT JOIN elevenlabs_keys k ON k.assigned_user_id = u.id
  GROUP BY u.id
`);
```

### 4. Batch Operations
```typescript
// ❌ BAD: Multiple individual inserts
for (const key of keys) {
  await insertKey(key);
}

// ✅ GOOD: Bulk insert
await bulkInsertKeys(keys);
```

---

## 🗄️ Caching Strategy

### 1. Memory Cache (Server-side)
```typescript
// lib/cache.ts
const cache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

export function getCached<T>(key: string): T | null {
  const item = cache.get(key);
  if (!item) return null;
  
  if (Date.now() > item.expiry) {
    cache.delete(key);
    return null;
  }
  
  return item.value;
}

export function setCached<T>(key: string, value: T, ttl = CACHE_TTL) {
  cache.set(key, {
    value,
    expiry: Date.now() + ttl
  });
}
```

### 2. React Query Cache (Client-side)
```typescript
// lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    }
  }
});
```

### 3. HTTP Caching Headers
```typescript
// API route
export async function GET(request: Request) {
  const data = await fetchData();
  
  return NextResponse.json(data, {
    headers: {
      'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=30',
      'CDN-Cache-Control': 'public, s-maxage=300',
    }
  });
}
```

### 4. Local Storage / Session Storage
```typescript
// Persistent cache cho static data
export function getCachedData(key: string) {
  const cached = localStorage.getItem(key);
  if (!cached) return null;
  
  const { data, timestamp } = JSON.parse(cached);
  if (Date.now() - timestamp > 3600000) { // 1 hour
    localStorage.removeItem(key);
    return null;
  }
  
  return data;
}
```

---

## 📈 Monitoring & Analytics

### 1. Web Vitals
```typescript
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
```

### 2. Performance Monitoring
```typescript
// lib/performance.ts
export function measurePerformance(name: string, fn: () => Promise<any>) {
  return async (...args: any[]) => {
    const start = performance.now();
    try {
      return await fn(...args);
    } finally {
      const duration = performance.now() - start;
      console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
      
      // Send to analytics
      if (duration > 1000) {
        console.warn(`[Slow Operation] ${name} took ${duration}ms`);
      }
    }
  };
}
```

### 3. Error Tracking
```typescript
// lib/errorTracking.ts
export function trackError(error: Error, context?: any) {
  console.error('[Error]', error, context);
  
  // Send to error tracking service (Sentry, etc.)
  // sentry.captureException(error, { extra: context });
}
```

---

## 🎯 Implementation Priority

### Phase 1: Quick Wins (1-2 days)
- [x] Add loading states
- [ ] Implement progress bars for bulk operations
- [ ] Add pagination to large lists
- [ ] Enable Next.js compression
- [ ] Add database indexes

### Phase 2: Medium Impact (3-5 days)
- [ ] Implement React Query
- [ ] Add server-side caching
- [ ] Optimize database queries
- [ ] Add request batching
- [ ] Implement virtualization for large tables

### Phase 3: Advanced (1-2 weeks)
- [ ] Server-Sent Events for real-time progress
- [ ] WebSocket for live updates
- [ ] CDN integration
- [ ] Advanced caching strategy
- [ ] Performance monitoring dashboard

---

## 🔍 Performance Checklist

### Frontend
- [ ] Code splitting implemented
- [ ] Images optimized (WebP/AVIF)
- [ ] Lazy loading for heavy components
- [ ] Memoization for expensive calculations
- [ ] Virtualization for long lists
- [ ] Debouncing for search inputs
- [ ] Optimistic UI updates

### Backend
- [ ] Database indexes created
- [ ] Connection pooling enabled
- [ ] Batch operations implemented
- [ ] Query optimization done
- [ ] Response compression enabled
- [ ] Pagination implemented
- [ ] Caching strategy in place

### User Experience
- [ ] Loading states everywhere
- [ ] Progress bars for long operations
- [ ] Error handling with retry
- [ ] Skeleton loaders
- [ ] Toast notifications
- [ ] Optimistic updates
- [ ] Smooth transitions

---

## 📊 Expected Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Initial Load Time | 3-5s | 1-2s | **60-70%** |
| API Response Time | 500-1000ms | 100-300ms | **70%** |
| Time to Interactive | 4-6s | 2-3s | **50%** |
| Bulk Operation Feedback | None | Real-time | **100%** |
| User Satisfaction | ? | ⭐⭐⭐⭐⭐ | **Excellent** |

---

## 🛠️ Tools & Libraries Recommended

```json
{
  "@tanstack/react-query": "^5.0.0",
  "@tanstack/react-virtual": "^3.0.0", 
  "react-hot-toast": "^2.4.1",
  "zustand": "^4.4.0",
  "next-pwa": "^5.6.0"
}
```

---

## 📚 Additional Resources

- [Next.js Performance Docs](https://nextjs.org/docs/app/building-your-application/optimizing)
- [React Query Docs](https://tanstack.com/query/latest)
- [Web Vitals](https://web.dev/vitals/)
- [Database Indexing Best Practices](https://use-the-index-luke.com/)

---

**💡 Pro Tip**: Đừng tối ưu mọi thứ cùng lúc. Measure → Optimize → Measure lại!




























