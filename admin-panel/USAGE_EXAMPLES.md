# 📚 Hướng Dẫn Sử Dụng Progress Tracking

## 🎯 Cách Sử Dụng Progress Bar

### Example 1: Bulk Import với Progress Tracking

```typescript
// app/dashboard/elevenlabs/page.tsx
'use client';

import { useState } from 'react';
import BulkOperationModal from '@/components/BulkOperationModal';
import { useToast } from '@/components/Toast';
import { bulkImportElevenLabsKeys } from '@/lib/api';

export default function ElevenLabsPage() {
  const [operationId, setOperationId] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const { success, error, ToastContainer } = useToast();

  const handleBulkImport = async (keysText: string) => {
    try {
      // Call API với progress tracking
      const res = await fetch('/api/elevenlabs/bulk-import-with-progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ keys_text: keysText }),
      });

      const data = await res.json();
      
      if (data.operationId) {
        setOperationId(data.operationId);
        setShowModal(true);
      } else {
        error('Không thể bắt đầu import');
      }
    } catch (err) {
      error('Lỗi khi import keys');
      console.error(err);
    }
  };

  const handleComplete = (state) => {
    success('Import hoàn thành!');
    // Refresh data
    fetchKeys();
  };

  return (
    <div>
      <ToastContainer />
      
      {/* Your UI */}
      <button onClick={() => handleBulkImport(keys)}>
        Import Keys
      </button>

      {/* Progress Modal */}
      <BulkOperationModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Import ElevenLabs Keys"
        operationId={operationId}
        onComplete={handleComplete}
      />
    </div>
  );
}
```

---

### Example 2: Check All Keys với Progress

```typescript
const handleCheckAllKeys = async () => {
  try {
    const res = await fetch('/api/elevenlabs/check-all-with-progress', {
      method: 'POST',
      credentials: 'include',
    });

    const data = await res.json();
    
    if (data.operationId) {
      setOperationId(data.operationId);
      setShowModal(true);
    }
  } catch (err) {
    error('Lỗi khi kiểm tra keys');
  }
};
```

---

### Example 3: Standalone Progress Bar

```typescript
import ProgressBar from '@/components/ProgressBar';

function MyComponent() {
  const [operationId, setOperationId] = useState<string | null>(null);

  return (
    <div>
      {operationId && (
        <ProgressBar
          operationId={operationId}
          onComplete={(state) => {
            console.log('Completed:', state);
          }}
          onError={(state) => {
            console.log('Error:', state);
          }}
          pollInterval={500}
          showDetails={true}
        />
      )}
    </div>
  );
}
```

---

### Example 4: Sử dụng Loading Spinner

```typescript
import LoadingSpinner, { TableSkeleton } from '@/components/LoadingSpinner';

function DataTable() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchData().then((result) => {
      setData(result);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <TableSkeleton rows={10} cols={5} />;
  }

  return <table>{/* Render data */}</table>;
}
```

---

### Example 5: Toast Notifications

```typescript
import { useToast } from '@/components/Toast';

function MyPage() {
  const { success, error, warning, info, ToastContainer } = useToast();

  const handleSave = async () => {
    try {
      await saveData();
      success('Lưu thành công!');
    } catch (err) {
      error('Lưu thất bại!');
    }
  };

  return (
    <div>
      <ToastContainer />
      <button onClick={handleSave}>Save</button>
    </div>
  );
}
```

---

## 🔧 Tạo API Route với Progress Tracking

### Template cho Bulk Operations

```typescript
// app/api/your-endpoint/route.ts
import { NextRequest, NextResponse } from 'next/server';
import {
  generateOperationId,
  createOperation,
  updateProgress,
  completeOperation,
  failOperation,
  addError
} from '@/lib/progressTracking';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { items } = body;

    // Create operation
    const operationId = generateOperationId('your_operation');
    createOperation(operationId, items.length);

    // Start processing in background
    processItemsInBackground(operationId, items);

    // Return immediately
    return NextResponse.json({
      operationId,
      message: `Bắt đầu xử lý ${items.length} items`,
    });

  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

async function processItemsInBackground(
  operationId: string,
  items: any[]
) {
  try {
    for (let i = 0; i < items.length; i++) {
      const item = items[i];

      try {
        // Update progress
        updateProgress(
          operationId,
          i + 1,
          `Đang xử lý item ${i + 1}/${items.length}`
        );

        // Process item
        await processItem(item);

        // Optional: Add delay để không overwhelm
        if (i % 10 === 0) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }

      } catch (error: any) {
        addError(operationId, item.id, error.message);
      }
    }

    completeOperation(operationId, 'Hoàn thành!');

  } catch (error: any) {
    failOperation(operationId, error.message);
  }
}
```

---

## 🚀 Best Practices

### 1. Loading States
```typescript
const [loading, setLoading] = useState(false);

const handleClick = async () => {
  setLoading(true);
  try {
    await doSomething();
  } finally {
    setLoading(false);
  }
};

<button disabled={loading}>
  {loading ? <ButtonSpinner /> : 'Click Me'}
</button>
```

### 2. Optimistic Updates
```typescript
const handleDelete = async (id: number) => {
  // Optimistic: Remove từ UI ngay
  setItems(items.filter(item => item.id !== id));
  
  try {
    await deleteItem(id);
    success('Xóa thành công!');
  } catch (err) {
    // Rollback nếu lỗi
    setItems([...items]);
    error('Xóa thất bại!');
  }
};
```

### 3. Debounce Search
```typescript
import { useDebounce } from '@/lib/hooks';

const [search, setSearch] = useState('');
const debouncedSearch = useDebounce(search, 500);

useEffect(() => {
  if (debouncedSearch) {
    searchData(debouncedSearch);
  }
}, [debouncedSearch]);
```

### 4. Cache với React Query
```typescript
// lib/hooks.ts
import { useQuery } from '@tanstack/react-query';

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: getUsers,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Usage
const { data, isLoading, error } = useUsers();
```

---

## 📊 Performance Monitoring

### Track API Performance
```typescript
// lib/performance.ts
export async function trackApiCall<T>(
  name: string,
  fn: () => Promise<T>
): Promise<T> {
  const start = performance.now();
  
  try {
    const result = await fn();
    const duration = performance.now() - start;
    
    console.log(`[API] ${name}: ${duration.toFixed(2)}ms`);
    
    // Send to analytics
    if (duration > 1000) {
      console.warn(`[Slow API] ${name} took ${duration}ms`);
    }
    
    return result;
  } catch (error) {
    const duration = performance.now() - start;
    console.error(`[API Error] ${name}: ${duration.toFixed(2)}ms`, error);
    throw error;
  }
}

// Usage
const users = await trackApiCall('getUsers', () => getUsers());
```

---

## 🎨 UI Best Practices

### 1. Always Show Feedback
- ✅ Loading states khi fetch data
- ✅ Progress bars cho bulk operations
- ✅ Toast notifications cho actions
- ✅ Error messages rõ ràng

### 2. Smooth Transitions
```css
/* globals.css */
.smooth-transition {
  transition: all 0.2s ease-in-out;
}
```

### 3. Empty States
```typescript
{items.length === 0 ? (
  <div className="text-center py-12 text-gray-500">
    <p>Không có dữ liệu</p>
    <button onClick={handleAdd}>Thêm mới</button>
  </div>
) : (
  <ItemList items={items} />
)}
```

### 4. Error Boundaries
```typescript
// components/ErrorBoundary.tsx
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <div>Có lỗi xảy ra!</div>;
    }
    return this.props.children;
  }
}
```

---

## 🔍 Debugging

### Log Progress
```typescript
// Enable verbose logging
const state = getProgress(operationId);
console.log('Progress:', state);
```

### Monitor Performance
```typescript
// Check Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

---

## 📱 Responsive Design

```typescript
// Hiển thị progress khác nhau trên mobile
<div className="hidden md:block">
  <ProgressBar operationId={id} showDetails={true} />
</div>
<div className="md:hidden">
  <ProgressBar operationId={id} showDetails={false} />
</div>
```

---

**💡 Tip**: Luôn test với slow network để đảm bảo UX tốt!





















