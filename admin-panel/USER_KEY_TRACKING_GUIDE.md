# 📊 Hướng Dẫn - User Key Tracking & Statistics

## 🎯 Tổng Quan

Hệ thống đã được nâng cấp với các tính năng tracking và thống kê chi tiết cho việc quản lý API keys:

1. ✅ **Show chi tiết** - Đã giao cho ai bao nhiêu key
2. ✅ **Tracking lifetime** - Tổng số key đã từng nhận
3. ✅ **Usage tracking** - Số key đã từng dùng
4. ✅ **Auto update** - Tool tự động update status khi dùng key
5. ✅ **Credit validation** - Chỉ giao key có credit > 800

---

## 📋 Database Schema Updates

### Users Table - New Columns:

| Column | Type | Description |
|--------|------|-------------|
| `total_keys_received` | INT | Tổng số keys đã từng được giao (lifetime) |
| `total_keys_used` | INT | Tổng số keys đã từng sử dụng (first use) |

### Migration:

```sql
-- Auto-run khi server start (lib/db.ts)
ALTER TABLE [dbo].[users] 
ADD [total_keys_received] INT NOT NULL DEFAULT 0;

ALTER TABLE [dbo].[users] 
ADD [total_keys_used] INT NOT NULL DEFAULT 0;
```

Hoặc chạy migration script:
```bash
npx tsx scripts/add-user-key-tracking.ts
```

---

## 🔧 API Changes

### 1. Bulk Assign Keys - Credit Validation

**Endpoint:** `POST /api/elevenlabs/bulk-assign`

**Changes:**
- ✅ Chỉ assign keys có `credit_balance > 800` hoặc `NULL`
- ✅ Sắp xếp theo credit từ cao xuống thấp
- ✅ Auto increment `total_keys_received` counter

**Example Request:**
```json
{
  "user_id": 5,
  "quantity": 10
}
```

**Response:**
```json
{
  "success": true,
  "assigned_count": 10,
  "assigned_keys": [...],
  "message": "Successfully assigned 10 keys to user"
}
```

**Query Logic:**
```sql
SELECT TOP (@quantity) [id], [credit_balance]
FROM [dbo].[elevenlabs_keys] 
WHERE [assigned_user_id] IS NULL 
  AND [status] = 'active'
  AND ([credit_balance] IS NULL OR [credit_balance] > 800)
ORDER BY [credit_balance] DESC, [created_at] ASC
```

---

### 2. Tool Report Status - Auto Tracking

**Endpoint:** `POST /api/tool/elevenlabs/status`

**Changes:**
- ✅ Detect first use (khi `last_used` NULL → NOT NULL)
- ✅ Auto increment `total_keys_used` khi first use
- ✅ Return `first_use` flag trong response

**Example Request:**
```json
{
  "key_id": 123,
  "status": "active",
  "credit_balance": 45000,
  "error_message": null
}
```

**Response:**
```json
{
  "success": true,
  "message": "Key status updated",
  "first_use": true
}
```

**Logic:**
```javascript
// Check if this is first use
const wasNeverUsed = (last_used === null);

// Update key
UPDATE elevenlabs_keys SET last_used = GETDATE() ...

// If first use, increment counter
if (wasNeverUsed && assigned_user_id) {
  UPDATE users 
  SET total_keys_used = total_keys_used + 1
  WHERE id = assigned_user_id;
}
```

---

### 3. Get Users - With Statistics

**Endpoint:** `GET /api/users`

**Response includes:**
```json
{
  "users": [
    {
      "id": 5,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "user",
      "is_active": true,
      "total_keys_received": 50,
      "total_keys_used": 35,
      "current_assigned_keys": 15,
      "active_keys_count": 12,
      "ready_keys_count": 10,
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```

**Fields Explained:**
- `total_keys_received`: Lifetime total (bao giờ cũng tăng)
- `total_keys_used`: Số keys đã dùng ít nhất 1 lần
- `current_assigned_keys`: Số keys hiện đang assign
- `active_keys_count`: Số keys đang active
- `ready_keys_count`: Số keys có credit > 800 (sẵn sàng dùng)

---

### 4. Get User Stats - Detailed Analytics

**Endpoint:** `GET /api/users/[id]/stats`

**Response:**
```json
{
  "user": {
    "id": 5,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "member_since": "2025-01-01T00:00:00"
  },
  "lifetime_stats": {
    "total_keys_received": 50,
    "total_keys_used": 35,
    "usage_rate": "70.0%"
  },
  "current_keys": {
    "total_assigned": 15,
    "active": 12,
    "dead": 2,
    "out_of_credit": 1,
    "used": 13,
    "unused": 2,
    "ready_to_use": 10
  },
  "credits": {
    "total_available": 450000,
    "avg_per_active_key": 37500
  },
  "recent_usage": [
    {
      "id": 123,
      "name": "Key #1",
      "status": "active",
      "credit_balance": 35000,
      "last_used": "2025-10-31T10:30:00",
      "last_error": null
    }
  ]
}
```

---

## 🎨 UI Updates

### Users Page - New Columns:

| Column | Description | Color |
|--------|-------------|-------|
| **Assigned** | Current total assigned keys | Gray |
| **Active** | Active keys count | Green |
| **Ready (>800)** | Keys sẵn sàng dùng | Blue |
| **Ever Received** | Lifetime total received | Gray |
| **Ever Used** | Lifetime total used | Gray |

**Visual Example:**
```
┌─────────────┬────────────┬──────┬──────────┬────────┬────────────┬──────────────┬───────────┬────────┬─────────┐
│ Username    │ Email      │ Role │ Assigned │ Active │ Ready(>800)│ Ever Received│ Ever Used │ Status │ Actions │
├─────────────┼────────────┼──────┼──────────┼────────┼────────────┼──────────────┼───────────┼────────┼─────────┤
│ john_doe    │ john@...   │ user │    15    │   12   │     10     │      50      │    35     │ Active │ [Edit]  │
│ jane_smith  │ jane@...   │ user │    20    │   18   │     15     │      65      │    48     │ Active │ [Edit]  │
└─────────────┴────────────┴──────┴──────────┴────────┴────────────┴──────────────┴───────────┴────────┴─────────┘
```

---

## 📊 Tracking Logic

### When Keys Are Assigned:

```javascript
// Bulk assign triggers increment
POST /api/elevenlabs/bulk-assign
{
  user_id: 5,
  quantity: 10
}

// System automatically:
1. Finds 10 keys with credit > 800
2. Assigns to user
3. Increments: total_keys_received += 10
```

### When Keys Are First Used:

```javascript
// Python tool reports status
POST /api/tool/elevenlabs/status
{
  key_id: 123,
  status: "active",
  credit_balance: 45000
}

// System checks:
if (key.last_used === null) {
  // This is FIRST use!
  1. Update key: last_used = NOW
  2. Increment: user.total_keys_used += 1
}
```

### When Keys Run Out of Credit:

```javascript
// Python tool reports
POST /api/tool/elevenlabs/status
{
  key_id: 123,
  status: "out_of_credit",
  credit_balance: 0,
  error_message: "No credits remaining"
}

// System updates:
1. key.status = 'out_of_credit'
2. key.credit_balance = 0
3. key.last_error = "No credits remaining"
4. Database persists state
```

---

## 🔄 Complete Flow Example

### Scenario: User receives and uses keys

```
STEP 1: Admin assigns 10 keys
POST /api/elevenlabs/bulk-assign
{
  user_id: 5,
  quantity: 10
}

Database State:
- user.total_keys_received: 0 → 10 ✅
- user.total_keys_used: 0
- user has 10 assigned keys (all unused)

─────────────────────────────────────

STEP 2: Python tool uses first key
POST /api/tool/elevenlabs/status
{
  key_id: 101,
  status: "active",
  credit_balance: 50000
}

Database State:
- user.total_keys_received: 10
- user.total_keys_used: 0 → 1 ✅
- key#101.last_used: NULL → NOW ✅

─────────────────────────────────────

STEP 3: Tool continues using keys
(Keys 102, 103, 104... first use)

Database State:
- user.total_keys_received: 10
- user.total_keys_used: 1 → 2 → 3 → 4... ✅

─────────────────────────────────────

STEP 4: Admin assigns 5 more keys
POST /api/elevenlabs/bulk-assign
{
  user_id: 5,
  quantity: 5
}

Database State:
- user.total_keys_received: 10 → 15 ✅
- user.total_keys_used: 8
- user now has 15 assigned keys total

─────────────────────────────────────

FINAL STATE:
Users Page Shows:
├─ Assigned: 15 (current)
├─ Active: 14 (1 might be dead/no credit)
├─ Ready (>800): 12 (2 have low credit)
├─ Ever Received: 15 (lifetime)
└─ Ever Used: 8 (used at least once)
```

---

## 💡 Business Logic Rules

### Rule 1: Credit Validation
- ✅ **Chỉ assign keys có credit > 800**
- ❌ Keys có ≤ 800 credits sẽ không được giao
- 💡 NULL credit được coi là OK (chưa check)

### Rule 2: Usage Tracking
- ✅ **total_keys_used chỉ tăng khi FIRST USE**
- ❌ Không tăng nếu key đã từng dùng rồi
- 💡 Dựa vào `last_used IS NULL`

### Rule 3: Lifetime Counters
- ✅ **total_keys_received KHÔNG BAO GIỜ GIẢM**
- ✅ **total_keys_used KHÔNG BAO GIỜ GIẢM**
- 💡 Counters này là lifetime metrics

### Rule 4: Current vs Lifetime
- **Current** = Hiện tại đang có
  - `current_assigned_keys` có thể giảm (unassign/delete)
- **Lifetime** = Tổng từ trước đến nay
  - `total_keys_received` chỉ tăng, không giảm

---

## 🧪 Testing Guide

### Test 1: Assign Keys with Credit Check

```bash
# 1. Check user stats before
GET /api/users/5/stats

# 2. Assign 10 keys
POST /api/elevenlabs/bulk-assign
{
  "user_id": 5,
  "quantity": 10
}

# Expected:
# - Only keys with credit > 800 assigned
# - total_keys_received += 10

# 3. Check user stats after
GET /api/users/5/stats
# Verify: lifetime_stats.total_keys_received increased by 10
```

### Test 2: First Use Tracking

```bash
# 1. Get a key that hasn't been used
GET /api/tool/elevenlabs (as user)
# Pick a key where last_used = null

# 2. Report status (simulate tool usage)
POST /api/tool/elevenlabs/status
{
  "key_id": 123,
  "status": "active",
  "credit_balance": 45000
}

# Expected response:
# {
#   "success": true,
#   "first_use": true  ← This means counter incremented!
# }

# 3. Check user stats
GET /api/users/5/stats
# Verify: lifetime_stats.total_keys_used increased by 1

# 4. Report same key again
POST /api/tool/elevenlabs/status
{
  "key_id": 123,
  ...
}

# Expected response:
# {
#   "first_use": false  ← Counter NOT incremented this time
# }
```

### Test 3: UI Display

```
1. Open Users page: /dashboard/users
2. Verify columns:
   ├─ Assigned (current count)
   ├─ Active (green number)
   ├─ Ready (>800) (blue number)
   ├─ Ever Received (lifetime)
   └─ Ever Used (lifetime)

3. Assign more keys to a user
4. Refresh page
5. Verify "Ever Received" increased
6. Verify "Assigned" also increased
```

---

## 🎯 Summary

### ✅ What's New:

| Feature | Description | Auto? |
|---------|-------------|-------|
| **Credit Check** | Only assign keys > 800 credits | ✅ Auto |
| **Lifetime Tracking** | Track total keys received | ✅ Auto |
| **Usage Tracking** | Track keys used (first use) | ✅ Auto |
| **Statistics UI** | Show all stats on Users page | ✅ Auto |
| **Detailed Analytics** | GET /api/users/[id]/stats | Manual |

### 📊 Metrics Available:

**Per User:**
- Total keys ever received (lifetime)
- Total keys ever used (lifetime)
- Current assigned keys
- Active keys count
- Ready to use keys (credit > 800)
- Usage rate percentage
- Average credit per key
- Recent usage history

**Admin Benefits:**
- ✅ Biết rõ ai nhận bao nhiêu key
- ✅ Tracking usage patterns
- ✅ Identify inactive users
- ✅ Optimize key distribution
- ✅ Monitor credit consumption

---

## 🚀 Next Steps

1. **Run Migration:**
   ```bash
   npm run dev
   # Auto-migration will run on first start
   ```

2. **Test Assign:**
   - Go to ElevenLabs page
   - Use Bulk Assign with credit > 800 requirement

3. **Monitor Stats:**
   - Check Users page for statistics
   - Use GET /api/users/[id]/stats for details

4. **Python Tool Integration:**
   - Tool automatically reports usage
   - Counters update in real-time

---

**Happy Tracking! 📊**

