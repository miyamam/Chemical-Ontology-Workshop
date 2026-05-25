# step0 事前準備

ワークショップを実施するにあたっての事前準備について記載します。

## 共通の事前準備
### ワークスペースとアクセス
- Fabric 対応ワークスペース：ワークショップのすべてのリソースをこのワークスペースに作成します
- ワークスペースロール（Contributor 以上）：リソース作成を行うため Contributor 以上のアクセスが必要です（Admin推奨）
- F16以上の有償版キャパシティ：スロットリングを回避し最適なパフォーマンスを確保するた- めF16以上を使用してください※Data Agent の作成に有償版が必要となります。

### テナント設定（管理ポータル→テナント設定）
1. ユーザーは Ontology (プレビュー) アイテムを作成できます
2. ユーザーは Graph を作成できます (プレビュー)
3. ユーザーは、Azure OpenAI に対応する Copilot やその他の機能を使用できます
4. Azure OpenAI に送信されたデータは、容量の地理的リージョン、コンプライアンス境界、または国内クラウド インスタンスの外部で処理できます
5. Azure OpenAI に送信されたデータは、容量の地理的リージョン、コンプライアンス境界、または国内クラウド インスタンスの外部に格納できます

**3-5は Azure OpenAI によるリージョン外データ処理を伴います。有効化する前に、組織のデータ所在地及びコンプライアンスポリシーを確認してください。**



## Notebook でリソース作成を行う場合の準備
### Fabric ワークスペースのGUID及びワークスペース名の取得
1. Fabric ポータルで対象のワークスペースを開き、URLをメモします。
例
```
https://app.fabric.microsoft.com/groups/d995c964-321b-4486-9a11-fc23428ef52c/list?experience=fabric-developer
```
このgroups/の直後の値が Workspace GUID となります。
例の場合は d995c964-321b-4486-9a11-fc23428ef52c 
メモしておきます。

2. ワークスペース名はポータルで表示されている名称をメモします。

### Fabric Lakehouse ID の取得
1. Lakehouse を開いた状態でブラウザのURLをメモします。
例
```
https://app.fabric.microsoft.com/groups/d995c964-321b-4486-9a11-fc23428ef52c/lakehouses/912ed674-bdf6-4240-82ae-dd0556e63a9d?experience=fabric-developer&selectedPath=Files
```

- groups/ の後ろ → Workspace ID
- lakehouses/ の後ろ → Lakehouse ID（= Artifact ID）

```
https://app.fabric.microsoft.com/groups/{workspaceId}/lakehouses/{artifactId}
```

### Kusto URI の取得方法
1. Fabricポータルで→ Workspace → Eventhouse → 対象の KQL Databaseを開く
2. 右側の 「Database details」 カードの　Query URI　をコピーします。

