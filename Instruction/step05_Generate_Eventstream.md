# Step5. イベントストリームの生成

リアルタイムイベントストリームを生成し、
Step4で作成した `[Prefix]_chemical_db` KQL テーブルに Kusto Python SDK 経由で取り込みます：
- SensorReadingEvent（センサー計測値）
- ProcessAlarmEvent（プロセスアラーム）
- EquipmentStatusEvent（設備状態変更）
- BatchPhaseTransitionEvent（バッチフェーズ遷移）
- QualityInspectionEvent（品質検査）

1. ワークスペースのトップ画面でインポート→ノートブック→コンピューターからをクリックし、'generate_events.ipynb' をアップロードします。
![image3-1](./Media/image3-1.png)


2. アップロードしたNotebookを開きデータ項目の追加→OneLakeカタログからStep1で作成したLakehouseを選択し追加をクリックします。
![image3-2](./Media/image3-2.png)
 
![image3-3](./Media/image3-3.png)

![image3-4](./Media/image3-4.png)

![image3-5](./Media/image3-5.png)


3. 設定 の下のセルにWorkspaceのGUID、LakehouseのGUID、KUSTO URI、KUSOTO_DATABASEを設定します。

4. エラーが出ていないことを確認しながら、セルを１つずつ順番に実行します

5. Eventhouse (KQL Database)にデータが挿入されているか確認します

Next: [Step6. オントロジーの作成](../Instruction/step06_Create_Ontology.md)
