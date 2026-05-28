# step0. 事前準備

ワークショップを実施するにあたっての事前準備について記載します。

## 共通の事前準備
### ワークスペースとアクセス
- Fabric 対応ワークスペース：ワークショップのすべてのリソースをこのワークスペースに作成します
- ワークスペースロール（Contributor 以上）：リソース作成を行うため Contributor 以上のアクセスが必要です（Admin推奨）
- F16以上の有償版キャパシティ：スロットリングを回避し最適なパフォーマンスを確保するた- めF16以上を使用してください
※Data Agent の作成に有償版が必要となります。

### テナント設定（管理ポータル→テナント設定）
1. ユーザーは Ontology (プレビュー) アイテムを作成できます
2. ユーザーは Graph を作成できます (プレビュー)
3. ユーザーは、Azure OpenAI に対応する Copilot やその他の機能を使用できます
4. Azure OpenAI に送信されたデータは、容量の地理的リージョン、コンプライアンス境界、または国内クラウド インスタンスの外部で処理できます
5. Azure OpenAI に送信されたデータは、容量の地理的リージョン、コンプライアンス境界、または国内クラウド インスタンスの外部に格納できます

**3-5は Azure OpenAI によるリージョン外データ処理を伴います。有効化する前に、組織のデータ所在地及びコンプライアンスポリシーを確認してください。**


## このワークショップでの命名規則
- **Prefix** を決めます。(イニシャル２文字など参加者間で重複しないものを決めます。例：MS)
- [Prefix]_lh_chemical　(レイクハウス)
- [Prefix]_eh_chemical　（イベントハウス）
- [Prefix]_chemical_db　（KQL Database）
- [Prefix]_ChemicalOntology　（オントロジー）
- [Prefix]_ChemicalAgent　（Data Agent）

## 使用する Notebook 及びリファレンスデータのダウンロード
- [Notebooks](../Notebooks/)フォルダの[03_load_reference_data.ipynb](../Notebooks/03_load_reference_data.ipynb)および[05_generate_events.ipynb](../Notebooks/05_generate_events.ipynb)をダウンロードします。これらのファイルはStep3およびStep5で使用します。
- [reference_data](../reference_data/)フォルダにある10個のJSONLファイルをダウンロードします。このファイルは[step2](../Instruction/step02_Upload_reference_data.md)で使用します。

|#|JSONLファイル名|内容|
|---|---|---|
|1|[equipment](../reference_data/equipment.jsonl)|設備|
|2|[failure_events](../reference_data/failure_events.jsonl)|故障イベント|
|3|[operation_phases](../reference_data/operation_phases.jsonl)|オペレーションフェーズ|
|4|[process_deviations](../reference_data/process_deviations.jsonl)|プロセス逸脱|
|5|[process_orders](../reference_data/process_orders.jsonl)|プロセスオーダー|
|6|[production_lines](../reference_data/production_lines.jsonl)|製造ライン|
|7|[products](../reference_data/products.jsonl)|製品|
|8|[quality_results](../reference_data/quality_results.jsonl)|品質検査結果|
|9|[root_causes](../reference_data/quality_results.jsonl)|根本原因|
|10|[sensors](../reference_data/sensors.jsonl)|センサー|



## （参考）Notebook で作業を行う際の準備
Step3でNotebookを実行するとき及び、全部のリソースを自動生成するときの手順となります。
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
1. Lakehouse を開いた状態でブラウザのURLをメモします。（LakehouseはStep1で作成予定）
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
1. Fabricポータルで→ Workspace → Eventhouse → 対象の KQL Databaseを開く（イベントハウスはStep4で作成予定）
2. 右側の 「Database details」 カードの　Query URI　をコピーします。

## Workshop コンテンツ
- [step0. 事前準備](../Instruction/step00_preparation.md)
- [Step1. Lakehouse の作成](../Instruction/step01_Lakehouse_Creation.md)
- [Step2. リファレンスデータのアップロード](../Instruction/step02_Upload_reference_data.md)
- [Step3. Delta テーブルの作成](../Instruction/step03_Create_DeltaTable.md)
- [Step4. Eventhouse（KQL Database）の作成](../Instruction/step04_Create_Eventhouse.md)
- [Step5. イベントストリームの生成](../Instruction/step05_Generate_Eventstream.md)
- [Step6. オントロジーの作成](../Instruction/step06_Create_Ontology.md)
- [Step7. Data Agent の作成](../Instruction/step07_Create_DataAgent.md)


