# VCA Server

## GCP Cloud Runへのデプロイ

### 前提条件

- [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install) インストール済み
- `gcloud auth login` で認証完了

### 初回セットアップ

#### 1. プロジェクト作成

```bash
# プロジェクト作成
gcloud projects create YOUR_PROJECT_ID --name="VCA Server"
gcloud config set project YOUR_PROJECT_ID

# 課金アカウント紐付け
gcloud billing accounts list
gcloud billing projects link YOUR_PROJECT_ID --billing-account=BILLING_ACCOUNT_ID

# API有効化
gcloud services enable run.googleapis.com \
  cloudbuild.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com
```

#### 2. Cloud SQL セットアップ

```bash
# 環境変数設定
export PROJECT_ID=$(gcloud config get-value project)
export REGION=asia-northeast1
export INSTANCE_NAME=vca-postgres
export DB_NAME=vca_db
export DB_USER=vca_user
export ROOT_PASSWORD="<SECURE_ROOT_PASSWORD>"
export DB_PASSWORD="<SECURE_DB_PASSWORD>"

# Cloud SQLインスタンス作成（5-10分）
gcloud sql instances create $INSTANCE_NAME \
  --database-version=POSTGRES_16 \
  --edition=ENTERPRISE \
  --tier=db-f1-micro \
  --region=$REGION \
  --root-password="$ROOT_PASSWORD"

# データベースとユーザー作成
gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME
gcloud sql users create $DB_USER \
  --instance=$INSTANCE_NAME \
  --password="$DB_PASSWORD"

# 接続名を取得
export CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"
```

#### 3. Secret Manager にパスワード保存

```bash
# パスワードをSecretに保存
echo -n "$DB_PASSWORD" | gcloud secrets create vca-db-password \
  --data-file=- \
  --replication-policy="automatic"

# IAM権限設定
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding vca-db-password \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

#### 4. マイグレーション用 Cloud Run Job 作成

```bash
# 初回は先にイメージをビルド
gcloud run deploy vca-server \
  --source . \
  --region=$REGION \
  --platform=managed \
  --no-allow-unauthenticated

# イメージURLを取得
IMAGE_URL=$(gcloud run services describe vca-server \
  --region=$REGION \
  --format="value(spec.template.spec.containers[0].image)")

# マイグレーション用Job作成
gcloud run jobs create vca-migrations \
  --image=$IMAGE_URL \
  --region=$REGION \
  --command="sh" \
  --args="-c,cd /app && uv run alembic upgrade head" \
  --update-env-vars="POSTGRES_SERVER=/cloudsql/$CONNECTION_NAME,POSTGRES_PORT=5432,POSTGRES_USER=$DB_USER,POSTGRES_DB=$DB_NAME" \
  --set-secrets="POSTGRES_PASSWORD=vca-db-password:latest" \
  --set-cloudsql-instances=$CONNECTION_NAME \
  --max-retries=0 \
  --task-timeout=300
```

#### 5. マイグレーション実行

```bash
gcloud run jobs execute vca-migrations \
  --region=$REGION \
  --wait
```

#### 6. Cloud Run デプロイ

```bash
gcloud run deploy vca-server \
  --image=$IMAGE_URL \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="POSTGRES_SERVER=/cloudsql/$CONNECTION_NAME,POSTGRES_PORT=5432,POSTGRES_USER=$DB_USER,POSTGRES_DB=$DB_NAME" \
  --set-secrets="POSTGRES_PASSWORD=vca-db-password:latest" \
  --add-cloudsql-instances=$CONNECTION_NAME \
  --max-instances=10 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300
```

### 再デプロイ（コード変更後）

```bash
# 環境変数を再設定
export PROJECT_ID=$(gcloud config get-value project)
export REGION=asia-northeast1
export INSTANCE_NAME=vca-postgres
export CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")

# 1. 新しいイメージをビルド
gcloud run deploy vca-server \
  --source . \
  --region=$REGION \
  --no-traffic

# 2. 新しいイメージでマイグレーションJob更新
IMAGE_URL=$(gcloud run services describe vca-server \
  --region=$REGION \
  --format="value(spec.template.spec.containers[0].image)")

gcloud run jobs update vca-migrations \
  --image=$IMAGE_URL \
  --region=$REGION

# 3. マイグレーション実行
gcloud run jobs execute vca-migrations \
  --region=$REGION \
  --wait

# 4. トラフィックを新リビジョンに切り替え
gcloud run services update-traffic vca-server \
  --to-latest \
  --region=$REGION
```

### 便利なコマンド

#### ログ確認

```bash
# Cloud Run サービスのログ
gcloud run logs read vca-server --region asia-northeast1 --limit=50

# マイグレーションJobのログ
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=vca-migrations" \
  --limit=50 \
  --format="value(textPayload)"

# リアルタイムログ
gcloud run logs tail vca-server --region asia-northeast1
```

#### サービス情報

```bash
# サービス詳細
gcloud run services describe vca-server --region asia-northeast1

# 現在のイメージURL
gcloud run services describe vca-server \
  --region=$REGION \
  --format="value(spec.template.spec.containers[0].image)"

# 環境変数一覧
gcloud run services describe vca-server \
  --region=$REGION \
  --format="value(spec.template.spec.containers[0].env)"
```

#### データベース操作

```bash
# Cloud SQLに接続
gcloud sql connect vca-postgres --user=vca_user --database=vca_db

# データベース一覧
gcloud sql databases list --instance=vca-postgres

# バックアップ作成
gcloud sql backups create --instance=vca-postgres
```

#### トラブルシューティング

```bash
# マイグレーションを手動で再実行
gcloud run jobs execute vca-migrations --region=$REGION --wait

# サービスを以前のリビジョンにロールバック
gcloud run services update-traffic vca-server \
  --to-revisions=REVISION_NAME=100 \
  --region=$REGION

# 環境変数を更新
gcloud run services update vca-server \
  --region=$REGION \
  --update-env-vars KEY=VALUE
```

### アーキテクチャ

- **API**: Cloud Run (FastAPI)
- **データベース**: Cloud SQL (PostgreSQL 16)
- **シークレット管理**: Secret Manager
- **マイグレーション**: Cloud Run Jobs (Alembic)

### コスト概算（東京リージョン）

- Cloud SQL (db-f1-micro): ~$10/月
- Cloud Run: 従量課金（無料枠あり）
- Secret Manager: ほぼ無料

### トラブルシューティング

#### マイグレーションエラー

```bash
# ログを確認
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=vca-migrations" --limit=20

# 手動で再実行
gcloud run jobs execute vca-migrations --region=$REGION --wait
```
