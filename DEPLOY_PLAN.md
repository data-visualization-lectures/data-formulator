# Data Formulator デプロイ実装計画

## 概要

Data Formulator を `data-formulator.dataviz.jp` にデプロイし、dataviz.jp の既存認証基盤（Supabase + Web Components）と接続する。

**デプロイ構成:**

| レイヤー | サービス | 理由 |
|---------|---------|------|
| フロントエンド | Vercel + カスタムドメイン `data-formulator.dataviz.jp` | Vite SPA のデプロイに最適 |
| バックエンド | Railway | `multiprocessing.Process` のためサーバーレス不可 |
| 認証 | dataviz.jp 既存インフラ | CDNスクリプト3本で統合 |
| プロジェクト保存 | `api.dataviz.jp/api/projects` | 既存API流用 |

```
[ユーザー]
    ↓
[data-formulator.dataviz.jp] ← Vercel
│  <dataviz-header>  ← 認証・サブスク検証
│  <dataviz-tool-header>  ← 保存/読込UI
│  React SPA
│    ↓ Authorization: Bearer JWT
├──→ [api.dataviz.jp] ← 既存インフラ（プロジェクト保存）
└──→ [Railway] ← Flask API（LLM・データ変換）
         ↓ JWT検証
      [Supabase] ← 既存認証基盤
```

---

## タスク一覧

### タスク 1: Vite ビルド出力先変更

**ファイル:** `vite.config.ts`

Vercel は `dist/` ディレクトリを標準出力先とするため変更。

```diff
- outDir: path.join(__dirname, 'py-src', 'data_formulator', "dist"),
+ outDir: 'dist',
```

> ローカルで Flask と一緒に動かす場合は `npm run build && cp -r dist py-src/data_formulator/dist`

---

### タスク 2: `index.html` に認証スクリプト追加

**ファイル:** `index.html`

`</head>` の直前に追加:

```html
<!-- dataviz.jp 認証基盤 -->
<script src="https://auth.dataviz.jp/lib/supabase.js"></script>
<script src="https://auth.dataviz.jp/lib/dataviz-auth-client.js"></script>
<script src="https://auth.dataviz.jp/lib/dataviz-tool-header.js" defer></script>
<style>
  body { padding-top: 48px; }
</style>
```

**読み込み後の自動動作:**
- `<dataviz-header>` が `<body>` 先頭に自動挿入（height: 48px, position: fixed）
- 未ログイン → 5秒後に `auth.dataviz.jp` へリダイレクト
- ログイン済み → サブスク検証
- `window.datavizSupabase` が利用可能になる

---

### タスク 3: API URL 環境変数化 + 認証ヘルパー追加

**ファイル:** `src/app/utils.tsx`

```typescript
// APIベースURL（環境変数優先）
const resolveServerUrl = (): string => {
    if (import.meta.env.VITE_API_BASE_URL) return import.meta.env.VITE_API_BASE_URL;
    if (import.meta.env.PROD) return "./";
    return "http://127.0.0.1:5000/";
};

export const appConfig: AppConfig = {
    serverUrl: resolveServerUrl(),
};

// Supabase トークン取得ヘルパー
export async function getSupabaseToken(): Promise<string | null> {
    const supabase = (window as any).datavizSupabase;
    if (!supabase) return null;
    try {
        const { data: { session } } = await supabase.auth.getSession();
        return session?.access_token ?? null;
    } catch { return null; }
}

// JWT付きfetchラッパー
export async function authenticatedFetch(
    url: string,
    options: RequestInit = {}
): Promise<Response> {
    const token = await getSupabaseToken();
    const headers: Record<string, string> = {
        ...(options.headers as Record<string, string> ?? {}),
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return fetch(url, { ...options, headers });
}
```

**Vercel 環境変数（UIで設定）:**
- `VITE_API_BASE_URL` = `https://（RailwayのURL）`

---

### タスク 4: 全 fetch 呼び出しを authenticatedFetch に変更

すべて `fetch(url, options)` → `authenticatedFetch(url, options)` に変更。
`import { getUrls, authenticatedFetch } from '../app/utils'` を追加。

| ファイル | 変更箇所 |
|---------|---------|
| `src/app/dfSlice.tsx` | `fetchFieldSemanticType`, `fetchCodeExpl`, `fetchAvailableModels` |
| `src/views/ModelSelectionDialog.tsx` | `testModel` 関数 |
| `src/views/EncodingShelfThread.tsx` | `fetch(engine, ...)` |
| `src/views/EncodingShelfCard.tsx` | `fetch(engine, ...)` |
| `src/views/EncodingBox.tsx` | `fetch(getUrls().SORT_DATA_URL, ...)` |
| `src/views/ConceptCard.tsx` | `fetch(getUrls().DERIVE_CONCEPT_URL, ...)` |
| `src/views/TableSelectionView.tsx` | vega-datasets fetch |
| `src/views/SelectableDataGrid.tsx` | `fetch(getUrls().SERVER_PROCESS_DATA_ON_LOAD, ...)` |

`src/app/App.tsx` の `fetch('/.auth/me')` は dataviz.jp 認証に差し替え（`window.datavizSupabase.auth.getSession()` 使用）。

---

### タスク 5: プロジェクト保存/読込機能

**ファイル:** `src/app/App.tsx`

既存の `dfActions.loadState` アクションを流用して状態を復元する。

**追加するState:**
```typescript
const fullState = useSelector((state: DataFormulatorState) => state);
const [projectLoadDialogOpen, setProjectLoadDialogOpen] = useState(false);
const [projectList, setProjectList] = useState<any[]>([]);
```

**追加する定数・関数:**
```typescript
const DATAVIZ_API = 'https://api.dataviz.jp';
const APP_NAME = 'data-formulator';

const saveProject = async () => {
    // URLに project_id があれば PUT、なければ POST
    // 保存後 URL に ?project_id=xxx を付与
    // toolHeader.showMessage('保存しました', 'success')
};

const loadProject = async () => {
    // GET /api/projects?app=data-formulator → projectList にセット → ダイアログ表示
};

const loadProjectById = async (id: string) => {
    // GET /api/projects/:id → dispatch(dfActions.loadState(savedState))
};
```

**`<dataviz-tool-header>` のセットアップ（useEffect内）:**
```typescript
useEffect(() => {
    const setup = () => {
        const toolHeader = document.querySelector('dataviz-tool-header') as any;
        if (!toolHeader) return;
        toolHeader.setConfig({
            logo: { type: 'text', text: 'Data Formulator' },
            buttons: [
                { label: '保存', action: saveProject },
                { label: '読込', action: loadProject },
            ],
        });
    };
    if (customElements.get('dataviz-tool-header')) setup();
    else customElements.whenDefined('dataviz-tool-header').then(setup);
}, []);
```

プロジェクト選択用 MUI `<Dialog>` を追加。

---

### タスク 6: `?project_id` URL パラメータで起動時自動読込

**ファイル:** `src/app/App.tsx`

```typescript
useEffect(() => {
    const autoLoad = async () => {
        const projectId = new URLSearchParams(window.location.search).get('project_id');
        if (!projectId) return;
        // window.datavizSupabase の初期化を最大5秒待つ
        // GET /api/projects/:id → dispatch(dfActions.loadState(savedState))
    };
    autoLoad();
}, []);
```

---

### タスク 7: Flask JWT 検証ミドルウェア + CORS 修正

**ファイル:** `py-src/data_formulator/app.py`

```python
import jwt as pyjwt
from functools import wraps

# CORS: 許可オリジンを環境変数で管理（全許可から絞り込み）
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

# JWT検証デコレータ
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not SUPABASE_JWT_SECRET:  # 未設定時はローカル開発としてスキップ
            return f(*args, **kwargs)
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return flask.jsonify({'error': 'Missing token'}), 401
        try:
            pyjwt.decode(auth.split(' ', 1)[1], SUPABASE_JWT_SECRET,
                         algorithms=["HS256"], options={"verify_aud": False})
        except pyjwt.InvalidTokenError as e:
            return flask.jsonify({'error': str(e)}), 401
        return f(*args, **kwargs)
    return decorated
```

- 全エンドポイント（`/vega-datasets` 〜 `/code-expl`）に `@require_auth` を追加
- 各レスポンスの `response.headers.add('Access-Control-Allow-Origin', '*')` を削除（Flask-CORS が管理）
- ヘルスチェック用エンドポイントを追加（認証不要）:

```python
@app.route('/health')
def health_check():
    return flask.jsonify({'status': 'ok'}), 200
```

**Railway 環境変数（UIで設定）:**
- `SUPABASE_JWT_SECRET` = Supabase > Settings > API > JWT Secret
- `ALLOWED_ORIGINS` = `https://data-formulator.dataviz.jp`

---

### タスク 8: Flask 起動コード修正

**ファイル:** `py-src/data_formulator/app.py`

```python
def run_app():
    args = parse_args()
    # PORT 環境変数（Railway が自動設定）を優先
    port = args.port or int(os.getenv("PORT", 5000))
    # クラウド環境ではブラウザを開かない
    is_cloud = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT")
    if not is_cloud:
        threading.Timer(2, lambda: webbrowser.open(f"http://localhost:{port}", new=2)).start()
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host='0.0.0.0', port=port, threaded=True, debug=debug)
```

---

### タスク 9: Railway デプロイ設定

**ファイル:** `railway.toml`

```toml
[build]
builder = "RAILPACK"

[deploy]
startCommand = "PYTHONPATH=/app/py-src gunicorn data_formulator.app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
```

**`requirements.txt`（抜粋）:**
```
PyJWT>=2.8.0
gunicorn>=21.0.0
```

> ⚠️ `requirements.txt` に `.` を追加してパッケージ自体をインストールする方法は **機能しない**。
> RAILPACK は `pip install -r requirements.txt` をソースファイルが存在しない一時環境で実行するため、
> `py-src` ディレクトリが見つからずエラーになる。
> 代わりに `startCommand` に `PYTHONPATH=/app/py-src` を設定して解決する。

---

### タスク 9-補足: Railway デプロイ ハマりポイント集

実際のデプロイで発生したエラーと解決策をまとめる。

#### ❌ 問題1: nixpacks が deprecated

```
NIXPACKS builder is deprecated
```

**原因:** Railway が NIXPACKS ビルダーのサポートを終了。
**解決:** `railway.toml` の `builder = "nixpacks"` を `builder = "RAILPACK"` に変更。

---

#### ❌ 問題2: `ModuleNotFoundError: No module named 'data_formulator'`

```
ModuleNotFoundError: No module named 'data_formulator'
gunicorn.errors.HaltServer: <HaltServer 'Worker failed to boot.'>
```

**原因:** `data_formulator` パッケージ本体が Python パスに存在しない。
`requirements.txt` は依存ライブラリのみを列挙しており、パッケージ自体はインストールされない。

**試みたが失敗した解決策:**
- `requirements.txt` に `.` を追加 → RAILPACK はソースが存在しない一時環境で pip を実行するため、
  `py-src` が見つからず `error: error in 'egg_base' option: 'py-src' does not exist` が発生。

**正しい解決策:** `startCommand` に `PYTHONPATH=/app/py-src` を設定する。

```toml
startCommand = "PYTHONPATH=/app/py-src gunicorn data_formulator.app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120"
```

---

#### ❌ 問題3: 環境変数を設定してもモデルが自動登録されない

**原因:** `check-available-models` エンドポイントが、環境変数を読み込んだ後に
実際に OpenAI API を呼び出して「I can hear you.」という返答を確認できたモデルだけを登録する
という設計になっていた。このテスト呼び出しが以下の理由で失敗することがあった：
- レート制限・クォータ超過
- ネットワークタイムアウト（フロントエンド側の 20 秒制限）
- モデルが微妙に異なる文面で応答した場合

**解決策:** テスト呼び出しを廃止し、環境変数が揃っていれば即座にモデルを登録するよう変更
（`py-src/data_formulator/agent_routes.py` の `check_available_models` 関数）。

---

**Railway 環境変数（必須）:**

| 変数名 | 値の例 | 説明 |
|--------|--------|------|
| `SUPABASE_JWT_SECRET` | Supabase > Settings > API > JWT Secret | 認証用。未設定だとローカル開発モード（認証スキップ） |
| `ALLOWED_ORIGINS` | `https://data-formulator.dataviz.jp` | CORS 許可オリジン |
| `OPENAI_ENABLED` | `true` | OpenAI を有効化（**必須**、これがないとスキップされる） |
| `OPENAI_API_KEY` | `sk-xxxx` | OpenAI API キー |
| `OPENAI_MODELS` | `gpt-4o,gpt-4o-mini` | 使用するモデル名をカンマ区切りで指定（**必須**） |

---

### タスク 10: Vercel デプロイ設定

**作成ファイル:** `vercel.json`

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

**DNS 設定（dataviz.jp 管理画面）:**
- `data-formulator.dataviz.jp` の CNAME を Vercel ドメインに向ける

---

## 実装順序

```
タスク 1 (vite.config.ts)
    ↓
タスク 2 (index.html) ─┬─ タスク 9 (railway.toml)
                       └─ タスク 10 (vercel.json)
    ↓
タスク 3 (utils.tsx 環境変数化 + authenticatedFetch)
    ↓
タスク 4 (全 fetch → authenticatedFetch)
    ↓
タスク 5 (保存/読込) → タスク 6 (project_id 自動読込)
    ↓
タスク 7 (Flask JWT + CORS)
    ↓
タスク 8 (Flask 起動コード)
```

---

## 検証手順

1. `npm run dev` + `python -m data_formulator` → `SUPABASE_JWT_SECRET` 未設定で認証スキップ動作を確認
2. `npm run build` → `dist/` に出力されることを確認
3. Railway デプロイ → `/health` が 200 を返すことを確認
4. Vercel デプロイ → `data-formulator.dataviz.jp` でアクセス確認
5. 未ログインで `auth.dataviz.jp` にリダイレクトされることを確認
6. 保存/読込ボタンで `api.dataviz.jp/api/projects` への保存・復元を確認
7. 保存後 URL に `?project_id=xxx` が付与 → リロードで自動復元を確認
