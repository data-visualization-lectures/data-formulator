
<h1>
    <img src="./public/favicon.ico" alt="Data Formulator icon" width="28"> <b>Data Formulator: Create Rich Visualizations with AI</b>
</h1>

<div>

[![arxiv](https://img.shields.io/badge/Paper-arXiv:2408.16119-b31b1b.svg)](https://arxiv.org/abs/2408.16119)&ensp;
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)&ensp;
[![YouTube](https://img.shields.io/badge/YouTube-white?logo=youtube&logoColor=%23FF0000)](https://youtu.be/3ndlwt0Wi3c)&ensp;
[![build](https://github.com/microsoft/data-formulator/actions/workflows/python-build.yml/badge.svg)](https://github.com/microsoft/data-formulator/actions/workflows/python-build.yml)

</div>

Transform data and create rich visualizations iteratively with AI 🪄. Try Data Formulator now!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/microsoft/data-formulator?quickstart=1)

<kbd>
  <a target="_blank" rel="noopener noreferrer" href="https://codespaces.new/microsoft/data-formulator?quickstart=1" title="open Data Formulator in GitHub Codespaces"><img src="public/data-formulator-screenshot.png"></a>
</kbd>



## 概要

**Data Formulator** は、Microsoft Researchのアプリケーションで、大規模言語モデルを用いてデータを変換し、データビジュアライゼーションの実践を迅速化します。

Data Formulatorは、アナリストがリッチなビジュアライゼーションを反復的に作成するためのAI搭載ツールです。ユーザーがすべてを自然言語で記述する必要がある多くのチャットベースのAIツールとは異なり、Data Formulatorはユーザーインターフェースインタラクション（UI）と自然言語（NL）入力を組み合わせることで、より簡単なインタラクションを実現します。この融合型アプローチにより、ユーザーはチャートデザインを簡単に記述しながら、データ変換をAIに委任することができます。



## はじめよう

次のいずれかのオプションを使用して、Data Formulator を操作します:

- **オプション 1: Python PIP 経由でインストール**
  
  Python PIP を使用すると、簡単にセットアップでき、ローカルで実行できます (推奨: 仮想環境にインストールします)。

  ```bash
  # install data_formulator
  pip install data_formulator
  
  # start data_formulator
  data_formulator 
  
  # alternatively, you can run data formulator with this command
  python -m data_formulator
  ```

  Data Formulator will be automatically opened in the browser at [http://localhost:5000](http://localhost:5000).

  *Update: you can specify the port number (e.g., 8080) by `python -m data_formulator --port 8080` if the default port is occupied.*

- **オプション 2: Codespaces (5 分)**
  
  You can also run Data Formulator in Codespaces; we have everything pre-configured. For more details, see [CODESPACES.md](CODESPACES.md).
  
  [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/microsoft/data-formulator?quickstart=1)

- **オプション 3: 開発者モードで作業**

  開発環境を完全に制御し、特定のニーズに合わせて設定をカスタマイズしたい場合は、Data Formulator をローカルでビルドできます。
  詳細な手順については、[DEVELOPMENT.md](DEVELOPMENT.md) を参照してください。

## Data Formulator を使う

いずれかのオプションを使用してセットアップを完了したら、次の手順に従って Data Formulator の使用を開始します:

### データ化しかの基本
* OpenAIキーを入力し、モデル（GPT-4oを推奨）を選択してデータセットを選択します。
* チャートの種類を選択し、データフィールドをチャートのプロパティ（x、y、色など）にドラッグアンドドロップして、視覚的なエンコーディングを指定します。

https://github.com/user-attachments/assets/0fbea012-1d2d-46c3-a923-b1fc5eb5e5b8


### 初期データセットを超えた可視化を作成する（🤖 による）

* エンコーディングシェルフに、**現在のデータに存在しない** フィールドの名前を入力できます:
    - これにより、Data Formulator は、既存のデータから計算または変換を必要とするビジュアライゼーションを作成しようとしていることを伝えます。
    - オプションで、意図を明確にするための自然言語プロンプトを提供できます（フィールド名がわかりやすい場合は不要です）。

* **Formulate** ボタンをクリックします。
    - Data Formulator は、エンコーディングとプロンプトに基づいてデータを変換し、ビジュアライゼーションをインスタンス化します。
* データ、チャート、コードを検査します。
* 既存のチャートに基づいて新しいチャートを作成するには、自然言語でフォローアップします:
    - フォローアッププロンプトを提供します (例: *「上位 5件のみを表示!」*)。
    - 新しいチャートのビジュアルエンコーディングを更新することもできます。

https://github.com/user-attachments/assets/160c69d2-f42d-435c-9ff3-b1229b5bddba

https://github.com/user-attachments/assets/c93b3e84-8ca8-49ae-80ea-f91ceef34acb

必要に応じてこのプロセスを繰り返し、データを探索して理解を深めてください。探索結果は **データスレッド** パネルで追跡できます。

## 開発者向け手順

[開発者向け手順](DEVELOPMENT.md) に従って、Data Formulator 上に新しいデータ分析ツールを構築します。

## Research Papers
* [Data Formulator 2: Iteratively Creating Rich Visualizations with AI](https://arxiv.org/abs/2408.16119)

```
@article{wang2024dataformulator2iteratively,
      title={Data Formulator 2: Iteratively Creating Rich Visualizations with AI}, 
      author={Chenglong Wang and Bongshin Lee and Steven Drucker and Dan Marshall and Jianfeng Gao},
      year={2024},
      booktitle={ArXiv preprint arXiv:2408.16119},
}
```

* [Data Formulator: AI-powered Concept-driven Visualization Authoring](https://arxiv.org/abs/2309.10094)

```
@article{wang2023data,
  title={Data Formulator: AI-powered Concept-driven Visualization Authoring},
  author={Wang, Chenglong and Thompson, John and Lee, Bongshin},
  journal={IEEE Transactions on Visualization and Computer Graphics},
  year={2023},
  publisher={IEEE}
}
```


## Contributing

This project welcomes contributions and suggestions. Most contributions require you to
agree to a Contributor License Agreement (CLA) declaring that you have the right to,
and actually do, grant us the rights to use your contribution. For details, visit
https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need
to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the
instructions provided by the bot. You will only need to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
