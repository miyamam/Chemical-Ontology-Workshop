# Chemical-Ontology-Workshop

このリポジトリは[Building an Ontology in Microsoft Fabric: A Trucking Domain Walkthrough](https://github.com/robkerr/trucking-ontology) をもとに科学プラントのオントロジー作成を手作業で行うWorkshopとして組み替えたものです。

作成時のUIの操作方法及び操作画面を使用しています。

## Workshop コンテンツ
- [step0. 事前準備](./Instruction/step00_preparation.md)
- [Step1. Lakehouse の作成](./Instruction/step01_Lakehouse_Creation.md)
- [Step2. リファレンスデータのアップロード](./Instruction/step02_Upload_reference_data.md)
- [Step3. Delta テーブルの作成](./Instruction/step03_Create_DeltaTable.md)
- [Step4. Eventhouse（KQL Database）の作成](./Instruction/step04_Create_Eventhouse.md)
- [Step5. イベントストリームの生成](./Instruction/step05_Generate_Eventstream.md)
- [Step6. オントロジーの作成](./Instruction/step06_Create_Ontology.md)
- [Step7. Data Agent の作成](./Instruction/step07_Create_DataAgent.md)

## Notebook
Notebook フォルダには Workshop 内で使用する(かもしれない) Notebook が格納されています。
- 03_load_reference_data
- 05_generate_events

- 00_AutoCreation（全自動スクリプト）

## Others
このWorkshopデータの[ER図](./Others/chemical_er_diagram.md)が格納されています。
